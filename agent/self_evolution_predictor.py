#!/usr/bin/env python3
"""
Self-Evolving Agent - Intent Predictor

Predicts user intent BEFORE they finish typing based on:
- Conversation history patterns
- User behavior profiles
- Sequence learning
- Temporal patterns
"""

import time
import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from collections import deque, defaultdict, Counter
from pathlib import Path


@dataclass
class Prediction:
    """An intent prediction"""
    predicted_intent: str
    confidence: float
    prediction_type: str  # "sequence", "history", "keyword", "temporal"
    evidence: List[str]
    suggested_tools: List[str]
    latency_ms: float


class IntentPredictor:
    """
    Predicts user intent based on learned patterns.
    
    Prediction Sources:
    1. Sequence Prediction: What intent usually comes after X -> Y?
    2. History Prediction: What does THIS user usually ask?
    3. Keyword Prediction: Partial text pattern matching
    4. Temporal Prediction: What intents happen at certain times?
    """
    
    def __init__(self, feedback_engine):
        self.feedback = feedback_engine
        
        # Learning data structures
        self.sequence_model: Dict[Tuple[str, ...], Counter] = defaultdict(Counter)
        self.user_profile: Dict[str, Counter] = defaultdict(Counter)
        self.temporal_patterns: Dict[str, Counter] = defaultdict(Counter)
        
        # Markov chain order
        self.markov_order = 2
        
        # Prediction thresholds
        self.MIN_CONFIDENCE_TO_ACT = 0.7
        
        # Recent context
        self.recent_intents = deque(maxlen=5)
        
        # Stats
        self.predictions_made = 0
        self.correct_predictions = 0
        self.avg_confidence = 0.0
    
    def learn_from_interaction(self, intent: str, user_id: str = "default"):
        """Learn from a completed interaction"""
        # 1. Update sequence model (Markov chain)
        if len(self.recent_intents) >= self.markov_order:
            context = tuple(list(self.recent_intents)[-self.markov_order:])
            self.sequence_model[context][intent] += 1
        
        # 2. Update user profile
        self.user_profile[user_id][intent] += 1
        
        # 3. Update temporal patterns
        hour = time.localtime().tm_hour
        time_slot = f"hour_{hour}"
        self.temporal_patterns[time_slot][intent] += 1
        
        # Add to recent history
        self.recent_intents.append(intent)
    
    def predict(self, partial_input: str = "", user_id: str = "default") -> List[Prediction]:
        """Make predictions based on available context"""
        predictions = []
        start_time = time.time()
        
        # 1. Sequence-based prediction
        seq_preds = self._predict_by_sequence()
        predictions.extend(seq_preds)
        
        # 2. User history prediction
        hist_preds = self._predict_by_history(user_id)
        predictions.extend(hist_preds)
        
        # 3. Partial keyword prediction
        if partial_input:
            key_preds = self._predict_by_keywords(partial_input)
            predictions.extend(key_preds)
        
        # 4. Temporal prediction
        temp_preds = self._predict_by_time()
        predictions.extend(temp_preds)
        
        # Merge and normalize
        merged = self._merge_predictions(predictions)
        merged.sort(key=lambda p: -p.confidence)
        
        latency = (time.time() - start_time) * 1000
        for p in merged:
            p.latency_ms = latency
        
        self.predictions_made += len(merged)
        
        return merged
    
    def _predict_by_sequence(self) -> List[Prediction]:
        """Predict based on recent intent sequence"""
        predictions = []
        
        if len(self.recent_intents) >= self.markov_order:
            context = tuple(list(self.recent_intents)[-self.markov_order:])
            
            if context in self.sequence_model:
                next_intents = self.sequence_model[context]
                total = sum(next_intents.values())
                
                for intent, count in next_intents.most_common(3):
                    confidence = count / total
                    if confidence >= 0.3:
                        predictions.append(Prediction(
                            predicted_intent=intent,
                            confidence=confidence,
                            prediction_type="sequence",
                            evidence=[
                                f"Sequence: {' -> '.join(context)} -> {intent}",
                                f"Seen {count}/{total} times"
                            ],
                            suggested_tools=self._get_tools_for_intent(intent),
                            latency_ms=0.0
                        ))
        
        return predictions
    
    def _predict_by_history(self, user_id: str) -> List[Prediction]:
        """Predict based on user's history"""
        predictions = []
        
        if user_id in self.user_profile:
            intents = self.user_profile[user_id]
            total = sum(intents.values())
            
            if total >= 5:  # Enough data to make predictions
                for intent, count in intents.most_common(3):
                    confidence = count / total
                    if confidence >= 0.2:
                        predictions.append(Prediction(
                            predicted_intent=intent,
                            confidence=confidence * 0.8,  # Discount
                            prediction_type="history",
                            evidence=[
                                f"User prefers {intent}",
                                f"{count}/{total} historical requests"
                            ],
                            suggested_tools=self._get_tools_for_intent(intent),
                            latency_ms=0.0
                        ))
        
        return predictions
    
    def _predict_by_keywords(self, partial_input: str) -> List[Prediction]:
        """Predict based on partial text input"""
        predictions = []
        text = partial_input.lower()
        
        # Keyword -> Intent mapping (learned from feedback)
        keyword_map = {
            "search": "WEB",
            "find": "WEB",
            "web": "WEB",
            "read": "FILES",
            "file": "FILES",
            "config": "FILES",
            "run": "CODE",
            "debug": "CODE",
            "fix": "CODE",
            "write": "CODE",
        }
        
        matches = []
        for keyword, intent in keyword_map.items():
            if keyword in text:
                matches.append((keyword, intent))
        
        if matches:
            # In real implementation, use learned success rates
            for keyword, intent in matches:
                predictions.append(Prediction(
                    predicted_intent=intent,
                    confidence=0.75,
                    prediction_type="keyword",
                    evidence=[
                        f"Matched keyword '{keyword}'",
                        f"Maps to {intent}"
                    ],
                    suggested_tools=self._get_tools_for_intent(intent),
                    latency_ms=0.0
                ))
        
        return predictions
    
    def _predict_by_time(self) -> List[Prediction]:
        """Predict based on temporal patterns"""
        predictions = []
        
        hour = time.localtime().tm_hour
        time_slot = f"hour_{hour}"
        
        if time_slot in self.temporal_patterns:
            intents = self.temporal_patterns[time_slot]
            total = sum(intents.values())
            
            if total >= 3:
                for intent, count in intents.most_common(2):
                    confidence = count / total
                    if confidence >= 0.4:
                        predictions.append(Prediction(
                            predicted_intent=intent,
                            confidence=confidence * 0.6,  # Heavily discounted
                            prediction_type="temporal",
                            evidence=[
                                f"Temporal pattern for hour {hour}",
                                f"{count}/{total} occurrences"
                            ],
                            suggested_tools=self._get_tools_for_intent(intent),
                            latency_ms=0.0
                        ))
        
        return predictions
    
    def _merge_predictions(self, predictions: List[Prediction]) -> List[Prediction]:
        """Merge overlapping predictions"""
        by_intent: Dict[str, List[Prediction]] = defaultdict(list)
        
        for p in predictions:
            by_intent[p.predicted_intent].append(p)
        
        merged = []
        for intent, preds in by_intent.items():
            # Weighted average confidence
            weighted_conf = sum(p.confidence for p in preds) / len(preds)
            
            # Combine evidence
            all_evidence = []
            for p in preds:
                all_evidence.extend(p.evidence)
            
            # Union of suggested tools
            all_tools = set()
            for p in preds:
                all_tools.update(p.suggested_tools)
            
            merged.append(Prediction(
                predicted_intent=intent,
                confidence=min(weighted_conf, 0.95),  # Cap at 95%
                prediction_type="combined",
                evidence=all_evidence,
                suggested_tools=list(all_tools),
                latency_ms=0.0
            ))
        
        return merged
    
    def _get_tools_for_intent(self, intent: str) -> List[str]:
        """Get recommended tools for an intent"""
        mapping = {
            "WEB": ["web_search", "web_extract"],
            "FILES": ["read_file", "search_files"],
            "CODE": ["terminal", "execute_code"],
            "RESEARCH": ["web_search", "search_files"],
            "CREATIVE": [],
            "FULL": [],
        }
        return mapping.get(intent, [])
    
    def report_prediction_result(self, predicted_intent: str, actual_intent: str):
        """Report whether a prediction was correct"""
        if predicted_intent == actual_intent:
            self.correct_predictions += 1
    
    def get_prediction_accuracy(self) -> float:
        """Get current prediction accuracy"""
        if self.predictions_made == 0:
            return 0.0
        return self.correct_predictions / self.predictions_made
    
    def get_prediction_stats(self) -> Dict[str, Any]:
        """Get prediction statistics"""
        return {
            "predictions_made": self.predictions_made,
            "correct_predictions": self.correct_predictions,
            "accuracy": round(self.get_prediction_accuracy() * 100, 1),
            "sequence_patterns_learned": len(self.sequence_model),
            "user_profiles": len(self.user_profile),
            "recent_context": list(self.recent_intents)
        }


# ---------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------

if __name__ == "__main__":
    from self_evolution_feedback import FeedbackCaptureEngine, InteractionRecord
    
    print("=" * 70)
    print("🔮 INTENT PREDICTOR DEMO")
    print("=" * 70)
    print()
    
    # Setup
    engine = FeedbackCaptureEngine(db_path="/tmp/evolution_demo5")
    predictor = IntentPredictor(engine)
    
    # Simulate conversation history to learn from
    conversation = [
        "Search for Python tutorials",
        "Read the config file",
        "Run the test script",
        "Search for API documentation",
        "Read the log file",
        "Fix the bug",
        "Search for solutions",
    ]
    
    intents = ["WEB", "FILES", "CODE", "WEB", "FILES", "CODE", "WEB"]
    
    print("📝 Training on conversation sequence...")
    print(f"   Sequence: {' -> '.join(intents)}")
    print()
    
    for intent in intents:
        predictor.learn_from_interaction(intent)
    
    # Make predictions
    print("🔮 Making predictions based on learned patterns...")
    print()
    
    predictions = predictor.predict()
    
    for i, pred in enumerate(predictions[:3]):
        print(f"   Prediction #{i+1}: {pred.predicted_intent} "
              f"(confidence: {pred.confidence:.0%})")
        print(f"   Type: {pred.prediction_type}")
        for ev in pred.evidence:
            print(f"      - {ev}")
        print(f"   Suggested tools: {', '.join(pred.suggested_tools)}")
        print()
    
    # Show stats
    stats = predictor.get_prediction_stats()
    print("📊 PREDICTION STATISTICS:")
    print(f"   Patterns Learned: {stats['sequence_patterns_learned']}")
    print(f"   Recent Context: {' -> '.join(stats['recent_context'])}")
    print()
    
    # Simulate partial input prediction
    print("🔮 Predicting from partial input 'search for...':")
    partial_preds = predictor.predict("search for")
    for p in partial_preds[:1]:
        print(f"   Most likely: {p.predicted_intent} ({p.confidence:.0%})")
    print()
    
    print("✅ Intent Predictor - READY!")
    print()
    print("   Next: Full Self-Evolving Agent Integration")
    print("=" * 70)
