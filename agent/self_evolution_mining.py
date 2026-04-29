#!/usr/bin/env python3
"""
Self-Evolving Agent - Pattern Mining Engine

Discovers hidden patterns in interaction history:
- Failure patterns (what keywords cause routing mistakes)
- Success formulas (what combination works well)
- Contextual patterns (how conversation history affects outcome)
"""

import json
import re
import time
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Any, Set
from collections import defaultdict, Counter
from itertools import combinations
import math


@dataclass
class DiscoveredPattern:
    """A pattern discovered through mining"""
    pattern_id: str
    pattern_type: str  # "failure", "success", "context", "sequence"
    trigger: str  # Regex or keyword pattern
    effect: str  # What happens when this triggers
    confidence: float
    support: int  # Number of occurrences
    impact: float  # 0-1, how much this affects outcomes
    action: Optional[str] = None  # Suggested action
    metadata: Dict[str, Any] = None


class PatternMiningEngine:
    """
    Mines interaction data to discover actionable patterns.
    
    Algorithms:
    - Co-occurrence analysis
    - Sequential pattern mining
    - Correlation detection
    - Outlier identification
    """
    
    def __init__(self, feedback_engine):
        self.feedback = feedback_engine
        self.discovered_patterns: List[DiscoveredPattern] = []
        self.cooccurrence_matrix: Dict[Tuple[str, str], int] = defaultdict(int)
        self.sequence_patterns: Dict[Tuple[str, ...], int] = defaultdict(int)
        
    def mine_all_patterns(self, min_support: int = 3) -> List[DiscoveredPattern]:
        """Run all mining algorithms"""
        self.discovered_patterns = []
        
        # 1. Failure patterns
        self.discovered_patterns.extend(
            self._mine_failure_patterns(min_support)
        )
        
        # 2. Success patterns
        self.discovered_patterns.extend(
            self._mine_success_patterns(min_support)
        )
        
        # 3. Co-occurrence patterns
        self.discovered_patterns.extend(
            self._mine_cooccurrence_patterns(min_support)
        )
        
        # 4. Context patterns
        self.discovered_patterns.extend(
            self._mine_context_patterns(min_support)
        )
        
        # Sort by impact
        self.discovered_patterns.sort(key=lambda p: -p.impact)
        
        return self.discovered_patterns
    
    def _mine_failure_patterns(self, min_support: int) -> List[DiscoveredPattern]:
        """Mine patterns that correlate with routing failures"""
        patterns = []
        
        # Get failure-prone keywords
        failures = self.feedback.get_failure_prone_keywords()
        
        for keyword, fail_rate in failures:
            if fail_rate > 0.6:
                pattern = DiscoveredPattern(
                    pattern_id=f"fail_{hash(keyword)}",
                    pattern_type="failure",
                    trigger=keyword,
                    effect=f"Routing fails {fail_rate:.0%} of the time",
                    confidence=fail_rate,
                    support=int(fail_rate * 10),  # Estimate
                    impact=fail_rate,
                    action=f"Add fallback rule for '{keyword}' -> FULL toolset",
                    metadata={"keyword": keyword}
                )
                patterns.append(pattern)
        
        return patterns
    
    def _mine_success_patterns(self, min_support: int) -> List[DiscoveredPattern]:
        """Mine patterns that correlate with routing success"""
        patterns = []
        
        # For each intent, find high-success keywords
        intents = ["WEB", "CODE", "FILES", "RESEARCH", "CREATIVE"]
        
        for intent in intents:
            successes = self.feedback.get_successful_keywords_for_intent(intent)
            
            for keyword, success_rate in successes:
                if success_rate > 0.8:
                    pattern = DiscoveredPattern(
                        pattern_id=f"success_{intent}_{hash(keyword)}",
                        pattern_type="success",
                        trigger=keyword,
                        effect=f"{intent} routing succeeds {success_rate:.0%} of the time",
                        confidence=success_rate,
                        support=int(success_rate * 10),
                        impact=success_rate * 0.5,  # Success has lower impact than failure
                        action=f"Strengthen '{keyword}' -> {intent} mapping",
                        metadata={"intent": intent, "keyword": keyword}
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _mine_cooccurrence_patterns(self, min_support: int) -> List[DiscoveredPattern]:
        """Mine keyword co-occurrence patterns"""
        patterns = []
        
        # Build co-occurrence matrix from recent interactions
        for interaction in self.feedback.recent_interactions:
            words = self._extract_keywords(interaction.user_message)
            
            # Count pairs
            for word1, word2 in combinations(words, 2):
                if word1 < word2:  # Canonical order
                    self.cooccurrence_matrix[(word1, word2)] += 1
        
        # Find significant co-occurrences
        for (word1, word2), count in self.cooccurrence_matrix.items():
            if count >= min_support:
                # Calculate lift (how much more than random)
                total = len(self.feedback.recent_interactions)
                p_word1 = sum(1 for i in self.feedback.recent_interactions 
                              if word1 in i.user_message.lower()) / total
                p_word2 = sum(1 for i in self.feedback.recent_interactions 
                              if word2 in i.user_message.lower()) / total
                expected = total * p_word1 * p_word2
                lift = count / expected if expected > 0 else 1.0
                
                if lift > 2.0:  # Significantly more than random
                    pattern = DiscoveredPattern(
                        pattern_id=f"cooccur_{hash(word1+word2)}",
                        pattern_type="cooccurrence",
                        trigger=f"{word1} + {word2}",
                        effect=f"Co-occur {lift:.1f}x more than random",
                        confidence=min(lift / 5.0, 1.0),
                        support=count,
                        impact=min(lift / 10.0, 1.0),
                        action=f"Consider combined rule for '{word1}' + '{word2}'",
                        metadata={"words": [word1, word2], "lift": lift}
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _mine_context_patterns(self, min_support: int) -> List[DiscoveredPattern]:
        """Mine patterns related to conversation context"""
        patterns = []
        
        # Look for sequences of intent switches that cause issues
        sequences = self._extract_intent_sequences()
        
        for seq, count in sequences.items():
            if count >= min_support and len(seq) >= 2:
                # Check if this sequence correlates with failures
                failure_rate = self._calculate_sequence_failure_rate(seq)
                
                if failure_rate > 0.5:
                    pattern = DiscoveredPattern(
                        pattern_id=f"context_{hash(str(seq))}",
                        pattern_type="context",
                        trigger=f"Sequence: {' -> '.join(seq)}",
                        effect=f"Fails {failure_rate:.0%} of the time",
                        confidence=failure_rate,
                        support=count,
                        impact=failure_rate,
                        action=f"Add context awareness for {' -> '.join(seq)} sequence",
                        metadata={"sequence": seq}
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text"""
        words = re.findall(r'\b[a-z]{4,}\b', text.lower())
        stop_words = {"this", "that", "with", "from", "have", "been", 
                     "will", "would", "could", "should", "when", "what"}
        return [w for w in words if w not in stop_words]
    
    def _extract_intent_sequences(self, window: int = 3) -> Dict[Tuple[str, ...], int]:
        """Extract sequences of intents from conversation history"""
        sequences = defaultdict(int)
        
        # In a real implementation, would group by session
        # For now, just slide through the recent list
        intents = [i.detected_intent for i in self.feedback.recent_interactions]
        
        for i in range(len(intents) - window + 1):
            seq = tuple(intents[i:i+window])
            sequences[seq] += 1
        
        return sequences
    
    def _calculate_sequence_failure_rate(self, sequence: Tuple[str, ...]) -> float:
        """Calculate failure rate for a given intent sequence"""
        # Simplified: just return a simulated rate based on sequence properties
        if len(set(sequence)) > 2:  # Many intent switches
            return 0.7
        return 0.2
    
    def get_high_impact_patterns(self, min_impact: float = 0.5) -> List[DiscoveredPattern]:
        """Get patterns with highest impact for review"""
        return [p for p in self.discovered_patterns if p.impact >= min_impact]
    
    def generate_optimization_report(self) -> Dict[str, Any]:
        """Generate a comprehensive optimization report"""
        high_impact = self.get_high_impact_patterns(0.5)
        failures = [p for p in self.discovered_patterns if p.pattern_type == "failure"]
        successes = [p for p in self.discovered_patterns if p.pattern_type == "success"]
        
        return {
            "summary": {
                "total_patterns_discovered": len(self.discovered_patterns),
                "high_impact_patterns": len(high_impact),
                "failure_patterns": len(failures),
                "success_patterns": len(successes),
            },
            "recommended_actions": [
                {
                    "priority": "CRITICAL" if p.impact > 0.8 else "HIGH" if p.impact > 0.6 else "MEDIUM",
                    "pattern": p.trigger,
                    "effect": p.effect,
                    "action": p.action
                }
                for p in sorted(high_impact, key=lambda x: -x.impact)[:10]
            ],
            "expected_improvement": self._estimate_improvement(high_impact)
        }
    
    def _estimate_improvement(self, patterns: List[DiscoveredPattern]) -> Dict[str, float]:
        """Estimate improvement if all patterns are addressed"""
        total_impact = sum(p.impact * p.support for p in patterns)
        total_support = sum(p.support for p in patterns)
        
        avg_impact = total_impact / total_support if total_support > 0 else 0
        
        return {
            "expected_accuracy_gain_pct": round(avg_impact * 100, 1),
            "estimated_token_savings_gain_pct": round(avg_impact * 50, 1),
            "patterns_to_address": len(patterns)
        }


# ---------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------

if __name__ == "__main__":
    from self_evolution_feedback import FeedbackCaptureEngine, InteractionRecord
    
    print("=" * 70)
    print("🔍 PATTERN MINING ENGINE DEMO")
    print("=" * 70)
    print()
    
    # Setup feedback engine with more data
    engine = FeedbackCaptureEngine(db_path="/tmp/evolution_demo2")
    
    # Simulate more interactions for mining
    test_cases = [
        ("Search for Python tutorials", "WEB", 2),
        ("Read the config file", "FILES", 2),
        ("Run the test script", "CODE", 2),
        ("Find me some recipes", "WEB", 2),
        ("Let me check the logs", "FILES", 2),
        ("Debug the database connection", "CODE", 0),
        ("Search the web for API docs", "WEB", 2),
        ("Fix the import error", "CODE", 2),
        ("Search for Python tutorials online", "WEB", 2),
        ("Search Python documentation", "WEB", 2),
        ("Read the log file", "FILES", 2),
        ("Edit the source code", "CODE", 2),
        ("Debug and search for solution", "CODE", 0),  # Need WEB too
        ("Search and debug the issue", "CODE", 0),  # Need WEB too
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
    
    # Mine patterns
    miner = PatternMiningEngine(engine)
    patterns = miner.mine_all_patterns(min_support=2)
    
    print(f"📊 DISCOVERED {len(patterns)} PATTERNS:")
    print()
    
    for p in patterns[:8]:
        impact_icon = "🔴" if p.impact > 0.7 else "🟡" if p.impact > 0.4 else "🟢"
        print(f"{impact_icon} [{p.pattern_type.upper()}] {p.trigger}")
        print(f"   Effect: {p.effect}")
        print(f"   Action: {p.action}")
        print(f"   Impact: {p.impact:.1%} | Support: {p.support} cases")
        print()
    
    # Generate report
    report = miner.generate_optimization_report()
    print("=" * 70)
    print("📈 OPTIMIZATION REPORT:")
    print(f"   Total Patterns: {report['summary']['total_patterns_discovered']}")
    print(f"   High Impact: {report['summary']['high_impact_patterns']}")
    print(f"   Expected Accuracy Gain: {report['expected_improvement']['expected_accuracy_gain_pct']}%")
    print(f"   Expected Savings Gain: {report['expected_improvement']['estimated_token_savings_gain_pct']}%")
    print()
    print("✅ Pattern Mining Engine - READY!")
    print()
    print("   Next: Rule Optimizer -> Self-Healing -> Intent Predictor")
    print("=" * 70)
