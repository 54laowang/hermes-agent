#!/usr/bin/env python3
"""
Self-Evolving Agent - Feedback Capture Engine

Monitors interactions, captures user corrections,
and builds the learning dataset for continuous improvement.
"""

import json
import sqlite3
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict, Counter
from pathlib import Path
from datetime import datetime, timedelta


@dataclass
class InteractionRecord:
    """A single agent interaction recorded for learning"""
    timestamp: float
    session_id: str
    turn_id: str
    user_message: str
    detected_intent: str
    tools_used: List[str]
    success_rating: int  # 0=failure, 1=partial, 2=success
    tokens_saved: int
    latency_ms: float
    user_feedback: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['tools_used'] = json.dumps(self.tools_used)
        return data


class FeedbackCaptureEngine:
    """
    Engine that captures interaction feedback for self-improvement.
    
    Captures:
    1. What the user asked
    2. How the agent routed it
    3. How successful the interaction was
    4. Token savings achieved
    5. Explicit user corrections/feedback
    
    Uses SQLite for persistent storage with automatic schema migration.
    """
    
    def __init__(self, db_path: str = None):
        """Initialize with optional custom database path"""
        self.db_path = db_path or "/tmp/hermes_evolution.db"
        self.total_interactions = 0
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                session_id TEXT NOT NULL,
                turn_id TEXT NOT NULL,
                user_message TEXT NOT NULL,
                detected_intent TEXT NOT NULL,
                tools_used TEXT NOT NULL,
                success_rating INTEGER NOT NULL,
                tokens_saved INTEGER NOT NULL,
                latency_ms REAL NOT NULL,
                user_feedback TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS corrections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                interaction_id INTEGER,
                original_intent TEXT NOT NULL,
                corrected_intent TEXT NOT NULL,
                original_tools TEXT NOT NULL,
                corrected_tools TEXT NOT NULL,
                FOREIGN KEY (interaction_id) REFERENCES interactions(id)
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON interactions(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_intent ON interactions(detected_intent)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_success ON interactions(success_rating)')
        
        conn.commit()
        conn.close()
    
    def record_interaction(self, record: InteractionRecord) -> int:
        """Record an interaction for learning. Returns interaction ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO interactions 
            (timestamp, session_id, turn_id, user_message, detected_intent, 
             tools_used, success_rating, tokens_saved, latency_ms, user_feedback)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            record.timestamp,
            record.session_id,
            record.turn_id,
            record.user_message,
            record.detected_intent,
            json.dumps(record.tools_used),
            record.success_rating,
            record.tokens_saved,
            record.latency_ms,
            record.user_feedback
        ))
        
        interaction_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        self.total_interactions += 1
        return interaction_id
    
    def record_correction(self, interaction_id: int, original_intent: str,
                          corrected_intent: str, original_tools: List[str],
                          corrected_tools: List[str]) -> int:
        """Record an explicit user correction for learning"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO corrections
            (timestamp, interaction_id, original_intent, corrected_intent,
             original_tools, corrected_tools)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().timestamp(),
            interaction_id,
            original_intent,
            corrected_intent,
            json.dumps(original_tools),
            json.dumps(corrected_tools)
        ))
        
        correction_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return correction_id
    
    def get_recent_interactions(self, minutes: int = 60) -> List[InteractionRecord]:
        """Get interactions from recent time window"""
        cutoff = datetime.now().timestamp() - (minutes * 60)
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM interactions WHERE timestamp >= ? ORDER BY timestamp DESC
        ''', (cutoff,))
        
        records = []
        for row in cursor.fetchall():
            records.append(InteractionRecord(
                timestamp=row['timestamp'],
                session_id=row['session_id'],
                turn_id=row['turn_id'],
                user_message=row['user_message'],
                detected_intent=row['detected_intent'],
                tools_used=json.loads(row['tools_used']),
                success_rating=row['success_rating'],
                tokens_saved=row['tokens_saved'],
                latency_ms=row['latency_ms'],
                user_feedback=row['user_feedback']
            ))
        
        conn.close()
        return records
    
    def get_failure_patterns(self, min_occurrences: int = 3) -> Dict[str, Dict[str, Any]]:
        """Find patterns that correlate with failures"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT detected_intent, 
                   COUNT(*) as total,
                   SUM(CASE WHEN success_rating = 0 THEN 1 ELSE 0 END) as failures,
                   AVG(success_rating) as avg_success
            FROM interactions
            GROUP BY detected_intent
            HAVING total >= ?
            ORDER BY failures DESC
        ''', (min_occurrences,))
        
        patterns = {}
        for row in cursor.fetchall():
            intent, total, failures, avg_success = row
            failure_rate = failures / total if total > 0 else 0
            
            patterns[intent] = {
                'total': total,
                'failures': failures,
                'failure_rate': failure_rate,
                'avg_success': avg_success
            }
        
        conn.close()
        return patterns
    
    def get_keyword_correlations(self) -> Dict[str, Dict[str, float]]:
        """Find correlations between keywords and success/failure"""
        interactions = self.get_recent_interactions(1440)  # Last 24h
        
        keyword_success = defaultdict(list)
        
        for record in interactions:
            words = record.user_message.lower().split()
            for word in words:
                if len(word) >= 4:
                    keyword_success[word].append(record.success_rating)
        
        correlations = {}
        for keyword, ratings in keyword_success.items():
            if len(ratings) >= 5:
                avg_rating = sum(ratings) / len(ratings)
                correlations[keyword] = {
                    'occurrences': len(ratings),
                    'avg_success': avg_rating
                }
        
        return correlations
    
    def get_evolution_stats(self) -> Dict[str, Any]:
        """Get statistics about the evolution progress"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM interactions')
        total_interactions = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM corrections')
        total_corrections = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(success_rating) FROM interactions')
        result = cursor.fetchone()
        avg_success = result[0] if result and result[0] else 0
        
        cursor.execute('''
            SELECT AVG(success_rating) 
            FROM interactions 
            ORDER BY timestamp DESC 
            LIMIT 50
        ''')
        result = cursor.fetchone()
        recent_success = result[0] if result and result[0] else 0
        
        cursor.execute('SELECT SUM(tokens_saved) FROM interactions')
        result = cursor.fetchone()
        tokens_saved = result[0] if result and result[0] else 0
        
        conn.close()
        
        return {
            'total_interactions': total_interactions,
            'total_corrections': total_corrections,
            'avg_success_rating': avg_success,
            'recent_success_rate': recent_success / 2 if recent_success else 0,
            'tokens_saved_total': tokens_saved,
            'learning_rate': total_corrections / max(total_interactions, 1)
        }
