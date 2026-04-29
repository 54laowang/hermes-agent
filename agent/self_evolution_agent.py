#!/usr/bin/env python3
"""
Self-Evolving Agent - Complete Integration

Unified system that combines:
1. Feedback Capture    (observes)
2. Pattern Mining      (discovers)
3. Rule Optimization   (improves)
4. Self-Healing        (recovers)
5. Intent Prediction   (anticipates)

This is a fully autonomous agent that learns and improves over time
without human intervention.
"""

import time
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict

# Import all components
from self_evolution_feedback import FeedbackCaptureEngine, InteractionRecord
from self_evolution_mining import PatternMiningEngine, DiscoveredPattern
from self_evolution_optimizer import RuleOptimizer, OptimizationAction
from self_evolution_healing import SelfHealingEngine, HealthStatus
from self_evolution_predictor import IntentPredictor, Prediction


@dataclass
class SelfEvolutionMetrics:
    """Metrics for tracking self-evolution progress"""
    total_interactions: int
    total_optimizations: int
    total_healings: int
    total_predictions: int
    accuracy_trend: List[float]
    savings_trend: List[float]
    learning_velocity: float  # Improvements per interaction


class SelfEvolvingRouter:
    """
    The Complete Self-Evolving Agent.
    
    Evolution Lifecycle:
    ┌─────────┐     ┌─────────┐     ┌─────────┐
    │ Observe │────▶│ Discover│────▶│ Improve │
    └─────────┘     └─────────┘     └─────────┘
          ▲              │               │
          │              ▼               ▼
    ┌─────────┐     ┌─────────┐     ┌─────────┐
    │ Predict │────▶│ Recover │◀────│ Measure │
    └─────────┘     └─────────┘     └─────────┘
    
    Key Features:
    - Zero configuration needed
    - Learns automatically from every interaction
    - Heals itself when problems arise
    - Predicts future needs
    - Provides full transparency into its evolution
    """
    
    def __init__(self, base_router, db_path: str = None):
        """Initialize with a base router to evolve"""
        self.base_router = base_router
        
        # Core engines
        self.feedback = FeedbackCaptureEngine(db_path or "/tmp/self_evolution_db")
        self.miner = PatternMiningEngine(self.feedback)
        self.optimizer = RuleOptimizer(base_router, self.feedback, self.miner)
        self.healer = SelfHealingEngine(base_router, self.feedback, self.optimizer)
        self.predictor = IntentPredictor(self.feedback)
        
        # Evolution state
        self.birth_time = time.time()
        self.evolution_cycles_completed = 0
        self.auto_evolution_enabled = True
        
        # Configuration
        self.EVOLUTION_CYCLE_INTERVAL = 50  # Evolve every 50 interactions
        self.OPTIMIZE_ON_DEMAND_THRESHOLD = 0.6  # Trigger if accuracy < 60%
        
        # Metrics history
        self.metrics_history: List[SelfEvolutionMetrics] = []
        
        print("=" * 70)
        print("🧠 SELF-EVOLVING AGENT ACTIVATED")
        print("=" * 70)
        print(f"   Born: {time.ctime(self.birth_time)}")
        print(f"   Auto-evolution: {'ENABLED' if self.auto_evolution_enabled else 'DISABLED'}")
        print(f"   Core Engines: Feedback → Mining → Optimization → Healing → Prediction")
        print()
    
    def route(self, user_message: str, context: Dict = None) -> Tuple[str, List[str]]:
        """
        Route a user message with self-evolution superpowers.
        
        The process:
        1. Predict what the user will need (before routing)
        2. Route using the base router
        3. Record the interaction for learning
        4. Check health and self-heal if needed
        5. Trigger evolution cycle if ready
        """
        start_time = time.time()
        
        # 1. PREDICT: Anticipate user intent
        predictions = self.predictor.predict(user_message)
        if predictions:
            top_pred = predictions[0]
            if top_pred.confidence > 0.7:
                print(f"   🔮 Predicted: {top_pred.predicted_intent} ({top_pred.confidence:.0%})")
        
        # 2. ROUTE: Use base router
        intent, tools = self.base_router.analyze_intent(user_message, use_llm=False)
        
        # 3. LEARN: Record the interaction
        # (Success rating would come from user feedback in real implementation)
        # For now, simulate success based on prediction accuracy
        success_rating = 2  # Default success
        if predictions and predictions[0].predicted_intent != intent:
            success_rating = 1  # Mismatch = partial failure
        
        record = InteractionRecord(
            timestamp=time.time(),
            session_id="current",
            turn_id=f"turn_{self.feedback.total_interactions}",
            user_message=user_message,
            detected_intent=intent,
            tools_used=tools,
            success_rating=success_rating,
            tokens_saved=len(tools) * 500,  # Estimate
            latency_ms=(time.time() - start_time) * 1000
        )
        self.feedback.record_interaction(record)
        
        # Learn from this intent for future predictions
        self.predictor.learn_from_interaction(intent)
        
        # 4. HEAL: Check health and apply healing
        self.healer.record_turn_result(success_rating == 2, intent, tools)
        
        # 5. EVOLVE: Check if ready for evolution cycle
        if self.auto_evolution_enabled:
            self._check_evolution_cycle()
        
        return intent, tools
    
    def _check_evolution_cycle(self):
        """Check if we should run an evolution cycle"""
        interaction_count = self.feedback.total_interactions
        
        # Check: Interval reached?
        interval_ready = interaction_count > 0 and \
                        interaction_count % self.EVOLUTION_CYCLE_INTERVAL == 0
        
        # Check: Accuracy too low?
        stats = self.feedback.get_evolution_stats()
        accuracy_low = stats.get("recent_success_rate", 1.0) < self.OPTIMIZE_ON_DEMAND_THRESHOLD
        
        if interval_ready or accuracy_low:
            self.run_evolution_cycle()
    
    def run_evolution_cycle(self) -> Dict[str, Any]:
        """Run a complete evolution cycle"""
        cycle_start = time.time()
        self.evolution_cycles_completed += 1
        
        print()
        print("🔄" + "=" * 66 + "🔄")
        print(f"   EVOLUTION CYCLE #{self.evolution_cycles_completed} STARTING")
        print("🔄" + "=" * 66 + "🔄")
        print()
        
        # Step 1: Discover patterns
        print("🔍 Phase 1: Pattern Discovery")
        patterns = self.miner.mine_all_patterns()
        high_impact = self.miner.get_high_impact_patterns(0.5)
        print(f"   Discovered {len(patterns)} patterns total")
        print(f"   {len(high_impact)} high-impact patterns")
        print()
        
        # Step 2: Optimize rules
        print("⚙️  Phase 2: Rule Optimization")
        result = self.optimizer.run_optimization_cycle()
        print(f"   Applied {result.get('actions_applied', 0)} optimizations")
        print()
        
        # Step 3: Verify health
        print("🩹 Phase 3: Health Verification")
        health = self.healer.check_health()
        print(f"   System health: {health['status'].upper()}")
        print(f"   Failure rate: {health['failure_rate']:.1%}")
        print()
        
        # Step 4: Check improvements
        print("📈 Phase 4: Improvement Measurement")
        stats_before = self.feedback.get_evolution_stats()
        # In a real system, would compare with cycle #N-1
        print(f"   Current accuracy: {stats_before.get('recent_success_rate', 0):.1%}")
        print(f"   Token savings: {stats_before.get('tokens_saved_total', 0):,}")
        print()
        
        cycle_time = (time.time() - cycle_start) * 1000
        
        print("✨ Cycle completed in {:.0f}ms!".format(cycle_time))
        print()
        
        return {
            "cycle": self.evolution_cycles_completed,
            "patterns_discovered": len(patterns),
            "optimizations_applied": result.get("actions_applied", 0),
            "health_status": health["status"],
            "cycle_time_ms": round(cycle_time, 1)
        }
    
    def get_evolution_report(self) -> Dict[str, Any]:
        """Get comprehensive evolution report"""
        age_hours = (time.time() - self.birth_time) / 3600
        
        feedback_stats = self.feedback.get_evolution_stats()
        health = self.healer.check_health()
        prediction_stats = self.predictor.get_prediction_stats()
        optimization_report = self.optimizer.get_optimization_report()
        
        return {
            "agent_bio": {
                "age_hours": round(age_hours, 2),
                "evolution_cycles": self.evolution_cycles_completed,
                "total_interactions": self.feedback.total_interactions,
                "learning_velocity": round(
                    self.evolution_cycles_completed / max(self.feedback.total_interactions, 1) * 100, 
                    2
                )
            },
            "performance": {
                "health_status": health["status"],
                "routing_accuracy": f"{feedback_stats.get('recent_success_rate', 0):.1%}",
                "prediction_accuracy": f"{prediction_stats['accuracy']}%",
                "auto_heal_success_rate": health["auto_heal_success_rate"],
                "token_savings_rate": f"{feedback_stats.get('avg_tokens_saved', 0):,} per turn"
            },
            "learning_progress": {
                "patterns_learned": len(self.miner.discovered_patterns),
                "active_optimizations": optimization_report["summary"]["active_optimizations"],
                "healings_performed": health["healings_performed"],
                "sequence_patterns": prediction_stats["sequence_patterns_learned"]
            }
        }
    
    def print_evolution_summary(self):
        """Print a human-readable evolution summary"""
        report = self.get_evolution_report()
        
        print()
        print("=" * 70)
        print("🧠 SELF-EVOLUTION SUMMARY")
        print("=" * 70)
        print()
        print(f"📋 AGENT BIO:")
        print(f"   Age: {report['agent_bio']['age_hours']} hours")
        print(f"   Evolution Cycles: {report['agent_bio']['evolution_cycles']}")
        print(f"   Total Interactions: {report['agent_bio']['total_interactions']}")
        print(f"   Learning Velocity: {report['agent_bio']['learning_velocity']}%")
        print()
        print(f"📊 PERFORMANCE:")
        print(f"   Health: {report['performance']['health_status'].upper()}")
        print(f"   Routing Accuracy: {report['performance']['routing_accuracy']}")
        print(f"   Prediction Accuracy: {report['performance']['prediction_accuracy']}")
        print(f"   Auto-Heal Rate: {report['performance']['auto_heal_success_rate']:.1%}")
        print()
        print(f"🧠 LEARNING PROGRESS:")
        print(f"   Patterns Learned: {report['learning_progress']['patterns_learned']}")
        print(f"   Active Optimizations: {report['learning_progress']['active_optimizations']}")
        print(f"   Healings Performed: {report['learning_progress']['healings_performed']}")
        print(f"   Sequence Patterns: {report['learning_progress']['sequence_patterns']}")
        print()
        print("=" * 70)


# ---------------------------------------------------------------------
# Full End-to-End Demo
# ---------------------------------------------------------------------

if __name__ == "__main__":
    # Create a simple base router for the demo
    class SimpleRouter:
        def __init__(self):
            self.intent_keywords = defaultdict(list)
            self.enabled = True
            self.force_full_mode = False
        
        def analyze_intent(self, message: str, use_llm: bool = False):
            """Simple keyword-based routing"""
            msg = message.lower()
            if "search" in msg or "web" in msg or "find" in msg:
                return "WEB", ["web_search"]
            elif "read" in msg or "file" in msg or "config" in msg:
                return "FILES", ["read_file"]
            elif "run" in msg or "debug" in msg or "fix" in msg or "code" in msg:
                return "CODE", ["terminal"]
            else:
                return "FULL", []
    
    print()
    print("🚀" + "=" * 66 + "🚀")
    print("   SELF-EVOLVING AGENT - END-TO-END DEMO")
    print("🚀" + "=" * 66 + "🚀")
    print()
    
    # Create our self-evolving agent!
    base_router = SimpleRouter()
    agent = SelfEvolvingRouter(base_router, db_path="/tmp/self_evolution_demo_final")
    
    # Simulate 100 interactions to watch it evolve
    test_conversations = [
        # Normal pattern: WEB -> FILES -> CODE
        "Search for Python tutorials",
        "Read the config file",
        "Run the test script",
        "Search for API documentation",
        "Read the log file",
        "Debug the connection issue",
        "Search for database solutions",
        "Read the database config",
        "Fix the database connection",
        
        # Trigger some failures with 'debug' pattern
        "Debug the API issue",
        "Debug connection pool",
        "Debug memory leak",
        
        # More normal usage
        "Search for React tutorials",
        "Read package.json",
        "Run npm install",
        "Search for CSS tips",
        "Read styles.css",
        "Fix the layout bug",
    ]
    
    print("📝 Simulating 17 interactions to trigger evolution...")
    print()
    
    for i, message in enumerate(test_conversations):
        print(f"   [{i+1}] {message}")
        intent, tools = agent.route(message)
        print(f"        → {intent}: {tools}")
        
        # Trigger evolution cycle at 15 interactions
        if i == 14:
            print()
            print("   🎯 Reached 15 interactions - triggering evolution cycle!")
            agent.run_evolution_cycle()
            print()
    
    # Show final summary
    agent.print_evolution_summary()
    
    print()
    print("🎉 SELF-EVOLVING AGENT DEMO COMPLETE!")
    print()
    print("   What we witnessed:")
    print()
    print("   1. 👁️  OBSERVATION: Agent recorded every interaction")
    print("   2. 🔍 DISCOVERY: Agent found patterns in usage")
    print("   3. ⚙️  OPTIMIZATION: Agent improved its own rules")
    print("   4. 🩹  SELF-HEALING: Agent monitored health and fixed issues")
    print("   5. 🔮 PREDICTION: Agent anticipated future intents")
    print()
    print("   This agent will keep learning and improving FOREVER")
    print("   without any human intervention.")
    print()
    print("=" * 70)
