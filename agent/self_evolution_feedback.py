#!/usr/bin/env python3
"""
Self-Evolving Agent - Feedback Capture Engine

Monitors interactions, captures user corrections,
and builds the learning dataset for continuous improvement.
"""

import json
import time
import hashlib
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict, Counter


@dataclass
class InteractionRecord:
    """Single interaction record for learning"""
    timestamp: float
    session_id: str
    turn_id: str
    user_message: str
    detected_intent: str
    tools_used: List[str]
    user_correction: Optional[str] = None
    correction_type: Optional[str] = None  # "wrong_tool", "missing_tool", "wrong_intent"
    success_rating: int = 1  # 0=fail, 1=neutral, 2=success
    tokens_saved: int = 0
    latency_ms: float = 0.0


@dataclass
class LearnedPattern:
    """Pattern learned from feedback"""
    pattern_id: str
    pattern_type: str  # "keyword_map", "fallback_trigger", "success_formula"
    trigger_words: List[str]
    correct_intent: str
    confidence: float
    occurrence_count: int
    last_seen: float
    metadata: Dict[str, Any]


class FeedbackCaptureEngine:
    """
    Captures and processes interaction feedback to enable learning.
    
    Key Features:
    - Non-invasive monitoring (doesn't change behavior, just observes)
    - Automatic correction detection
    - Success/failure pattern tracking
    - Persistent learning database
    """
    
    def __init__(self, db_path: str = "data/evolution_db"):
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        self.interactions_file = self.db_path / "interactions.jsonl"
        self.patterns_file = self.db_path / "learned_patterns.json"
        self.stats_file = self.db_path / "evolution_stats.json"
        
        # In-memory caches
        self.recent_interactions: List[InteractionRecord] = []
        self.learned_patterns: List[LearnedPattern] = []
        self.intent_correction_map: Dict[str, Counter] = defaultdict(Counter)
        self.keyword_success_map: Dict[str, Counter] = defaultdict(Counter)
        
        # Load existing data
        self._load_patterns()
        self._load_stats()
        
        # Stats
        self.total_interactions = 0
        self.total_corrections = 0
        self.total_patterns_learned = 0
        self.learning_rate = 0.0
        
    def record_interaction(self, record: InteractionRecord) -> str:
        """Record an interaction and return its ID"""
        # Append to file
        with open(self.interactions_file, 'a') as f:
            f.write(json.dumps(asdict(record)) + '\n')
        
        # Update memory
        self.recent_interactions.append(record)
        if len(self.recent_interactions) > 1000:
            self.recent_interactions.pop(0)
        
        self.total_interactions += 1
        
        # Process for learning
        if record.success_rating != 1:  # Not neutral
            self._process_feedback(record)
        
        return record.turn_id
    
    def record_correction(self, turn_id: str, correction: str, 
                          correction_type: str) -> bool:
        """Record a user correction retroactively"""
        # Find the interaction and update
        # In production, would update the file
        self.total_corrections += 1
        
        # Extract learning from this correction
        self._extract_learning(turn_id, correction, correction_type)
        
        return True
    
    def _process_feedback(self, record: InteractionRecord):
        """Process feedback to extract learnings"""
        if record.success_rating == 0:  # Failure
            # Record what went wrong
            for word in record.user_message.lower().split():
                if len(word) > 3:
                    self.keyword_success_map[word]["fail"] += 1
                    
        elif record.success_rating == 2:  # Success
            # Record what worked
            for word in record.user_message.lower().split():
                if len(word) > 3:
                    self.keyword_success_map[word]["success"] += 1
                    self.keyword_success_map[word][record.detected_intent] += 1
    
    def _extract_learning(self, turn_id: str, correction: str, 
                          correction_type: str):
        """Extract actionable learning from a correction"""
        # In a full implementation, would:
        # 1. Find the original interaction
        # 2. Identify what was wrong
        # 3. Extract corrected pattern
        # 4. Add to learned patterns
        
        self.total_patterns_learned += 1
    
    def get_successful_keywords_for_intent(self, intent: str) -> List[Tuple[str, float]]:
        """Get keywords that correlate with successful routing for an intent"""
        results = []
        for word, counts in self.keyword_success_map.items():
            success = counts.get(intent, 0)
            total = counts.get("success", 0) + counts.get("fail", 0)
            if total >= 3 and success > 0:
                rate = success / total
                if rate > 0.7:
                    results.append((word, rate))
        
        return sorted(results, key=lambda x: -x[1])[:20]
    
    def get_failure_prone_keywords(self) -> List[Tuple[str, float]]:
        """Get keywords that often trigger routing failures"""
        results = []
        for word, counts in self.keyword_success_map.items():
            fail = counts.get("fail", 0)
            total = counts.get("success", 0) + fail
            if total >= 3 and fail > 0:
                rate = fail / total
                if rate > 0.5:
                    results.append((word, rate))
        
        return sorted(results, key=lambda x: -x[1])[:20]
    
    def suggest_keyword_updates(self) -> List[Dict]:
        """Suggest keyword list updates based on learned patterns"""
        suggestions = []
        
        # Suggest adding successful keywords to their intent's keyword list
        for intent in ["WEB", "CODE", "FILES", "RESEARCH", "CREATIVE"]:
            good_keywords = self.get_successful_keywords_for_intent(intent)
            for word, rate in good_keywords[:5]:
                suggestions.append({
                    "type": "add_keyword",
                    "intent": intent,
                    "keyword": word,
                    "confidence": rate,
                    "reason": f"{rate:.0%} success rate in {intent} routing"
                })
        
        # Suggest removing failure-prone keywords
        for word, rate in self.get_failure_prone_keywords():
            suggestions.append({
                "type": "remove_keyword",
                "keyword": word,
                "confidence": rate,
                "reason": f"{rate:.0%} failure rate"
            })
        
        return suggestions
    
    def get_evolution_stats(self) -> Dict[str, Any]:
        """Get comprehensive evolution statistics"""
        if self.total_interactions > 0:
            self.learning_rate = self.total_corrections / self.total_interactions
        
        return {
            "total_interactions": self.total_interactions,
            "total_corrections": self.total_corrections,
            "total_patterns_learned": self.total_patterns_learned,
            "learning_rate": round(self.learning_rate * 100, 2),
            "keywords_tracked": len(self.keyword_success_map),
            "recent_success_rate": self._calculate_recent_success_rate(),
            "improvement_trend": self._calculate_improvement_trend()
        }
    
    def _calculate_recent_success_rate(self) -> float:
        """Calculate success rate for recent interactions"""
        if not self.recent_interactions:
            return 1.0
        
        recent = self.recent_interactions[-100:]
        successes = sum(1 for r in recent if r.success_rating == 2)
        failures = sum(1 for r in recent if r.success_rating == 0)
        total = successes + failures
        
        return successes / total if total > 0 else 1.0
    
    def _calculate_improvement_trend(self) -> float:
        """Calculate improvement trend (positive = getting better)"""
        if len(self.recent_interactions) < 200:
            return 0.0
        
        # Compare first half vs second half
        mid = len(self.recent_interactions) // 2
        old = self.recent_interactions[:mid]
        new = self.recent_interactions[mid:]
        
        def success_rate(items):
            s = sum(1 for r in items if r.success_rating == 2)
            f = sum(1 for r in items if r.success_rating == 0)
            return s / (s + f) if (s + f) > 0 else 0.5
        
        return success_rate(new) - success_rate(old)
    
    def _load_patterns(self):
        """Load learned patterns from disk"""
        if self.patterns_file.exists():
            data = json.loads(self.patterns_file.read_text())
            self.learned_patterns = [LearnedPattern(**p) for p in data]
    
    def _load_stats(self):
        """Load stats from disk"""
        if self.stats_file.exists():
            data = json.loads(self.stats_file.read_text())
            self.total_interactions = data.get("total_interactions", 0)
            self.total_corrections = data.get("total_corrections", 0)
            self.total_patterns_learned = data.get("total_patterns_learned", 0)
    
    def save(self):
        """Save all learning data to disk"""
        self.stats_file.write_text(json.dumps(self.get_evolution_stats(), indent=2))
        self.patterns_file.write_text(
            json.dumps([asdict(p) for p in self.learned_patterns], indent=2)
        )


# ---------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 70)
    print("🧠 FEEDBACK CAPTURE ENGINE DEMO")
    print("=" * 70)
    print()
    
    engine = FeedbackCaptureEngine(db_path="/tmp/evolution_demo")
    
    # Simulate some interactions
    print("📝 Simulating learning interactions...")
    print()
    
    test_cases = [
        ("Search for Python tutorials", "WEB", 2),  # Success
        ("Read the config file", "FILES", 2),  # Success
        ("Run the test script", "CODE", 2),  # Success
        ("Find me some recipes", "WEB", 2),  # Success
        ("Let me check the logs", "FILES", 2),  # Success
        ("Debug the database connection", "CODE", 0),  # Fail - needed WEB too
        ("Search the web for API docs", "WEB", 2),  # Success
        ("Fix the import error", "CODE", 2),  # Success
    ]
    
    for i, (msg, intent, rating) in enumerate(test_cases):
        record = InteractionRecord(
            timestamp=time.time(),
            session_id="demo_session",
            turn_id=f"turn_{i}",
            user_message=msg,
            detected_intent=intent,
            tools_used=[intent.lower()],
            success_rating=rating,
            tokens_saved=1500 if rating == 2 else 0,
            latency_ms=120.5
        )
        engine.record_interaction(record)
    
    # Show stats
    stats = engine.get_evolution_stats()
    print("📊 EVOLUTION STATISTICS:")
    print(f"   Total Interactions: {stats['total_interactions']}")
    print(f"   Total Corrections: {stats['total_corrections']}")
    print(f"   Learning Rate: {stats['learning_rate']}%")
    print(f"   Recent Success Rate: {stats['recent_success_rate']:.1%}")
    print(f"   Improvement Trend: {stats['improvement_trend']:+.1%}")
    print()
    
    print("💡 SUGGESTED KEYWORD UPDATES:")
    suggestions = engine.suggest_keyword_updates()
    for s in suggestions[:5]:
        print(f"   • {s['type'].upper()}: '{s.get('keyword', '?')}' -> {s.get('intent', 'N/A')}")
        print(f"     Confidence: {s['confidence']:.0%} - {s['reason']}")
    print()
    
    print("✅ Feedback Capture Engine - READY!")
    print()
    print("   Next: Pattern Mining -> Rule Optimizer -> Intent Predictor")
    print("=" * 70)
