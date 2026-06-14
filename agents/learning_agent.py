import json
import time
from datetime import datetime
from typing import Dict, List
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from config.settings import LEARNING_CONFIG, LOGS_DIR
from utils.message_format import create_message

class LearningAgent:
    """
    Tracks system performance and learns from experience
    - Logs all actions
    - Tracks success/failure rates
    - Identifies patterns
    - Suggests improvements
    """
    
    def __init__(self):
        print("🧠 Initializing Learning Agent...")
        
        self.log_file = LEARNING_CONFIG["log_file"]
        self.action_history = []
        self.performance_stats = {
            "total_actions": 0,
            "successful_actions": 0,
            "failed_actions": 0,
            "success_rate": 0.0
        }
        
        # Object-specific stats
        self.object_stats = {}
        
        # Load previous logs if exist
        self._load_history()
        
        print("✅ Learning Agent ready!")
    
    def _load_history(self):
        """Load previous action history"""
        try:
            if self.log_file.exists():
                with open(self.log_file, 'r') as f:
                    data = json.load(f)
                    self.action_history = data.get("history", [])
                    self.performance_stats = data.get("stats", self.performance_stats)
                    self.object_stats = data.get("object_stats", {})
                print(f"📚 Loaded {len(self.action_history)} previous actions")
        except Exception as e:
            print(f"⚠️ Could not load history: {e}")
    
    def _save_history(self):
        """Save action history to file"""
        try:
            data = {
                "history": self.action_history,
                "stats": self.performance_stats,
                "object_stats": self.object_stats,
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.log_file, 'w') as f:
                json.dump(data, f, indent=2)
            
        except Exception as e:
            print(f"⚠️ Could not save history: {e}")
    
    def log_action(self, action_data: Dict):
        """
        Log a single action
        
        Args:
            action_data: {
                "action": "pick",
                "object": "bottle",
                "result": "success" or "failure",
                "duration": 5.2,
                "error": "optional error message"
            }
        """
        timestamp = datetime.now().isoformat()
        
        log_entry = {
            "timestamp": timestamp,
            "action": action_data.get("action"),
            "object": action_data.get("object"),
            "result": action_data.get("result", "unknown"),
            "duration": action_data.get("duration", 0),
            "error": action_data.get("error")
        }
        
        # Add to history
        self.action_history.append(log_entry)
        
        # Update stats
        self._update_stats(log_entry)
        
        # Save periodically
        if len(self.action_history) % LEARNING_CONFIG["save_frequency"] == 0:
            self._save_history()
        
        print(f"\n📝 Logged action: {log_entry['action']} → {log_entry['result']}")
    
    def _update_stats(self, log_entry: Dict):
        """Update performance statistics"""
        # Overall stats
        self.performance_stats["total_actions"] += 1
        
        if log_entry["result"] == "success":
            self.performance_stats["successful_actions"] += 1
        elif log_entry["result"] == "failure":
            self.performance_stats["failed_actions"] += 1
        
        # Calculate success rate
        total = self.performance_stats["total_actions"]
        successful = self.performance_stats["successful_actions"]
        self.performance_stats["success_rate"] = (successful / total * 100) if total > 0 else 0
        
        # Object-specific stats
        obj = log_entry.get("object")
        if obj:
            if obj not in self.object_stats:
                self.object_stats[obj] = {
                    "attempts": 0,
                    "successes": 0,
                    "failures": 0,
                    "success_rate": 0.0
                }
            
            self.object_stats[obj]["attempts"] += 1
            
            if log_entry["result"] == "success":
                self.object_stats[obj]["successes"] += 1
            elif log_entry["result"] == "failure":
                self.object_stats[obj]["failures"] += 1
            
            # Calculate object success rate
            attempts = self.object_stats[obj]["attempts"]
            successes = self.object_stats[obj]["successes"]
            self.object_stats[obj]["success_rate"] = (successes / attempts * 100) if attempts > 0 else 0
    
    def get_performance_report(self) -> Dict:
        """
        Generate performance report
        Returns: Detailed performance statistics
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "overall_performance": self.performance_stats,
            "object_performance": self.object_stats,
            "recent_actions": self.action_history[-10:],  # Last 10 actions
            "recommendations": self._generate_recommendations()
        }
        
        return create_message(
            "learning_agent",
            "report",
            report,
            "success"
        )
    
    def _generate_recommendations(self) -> List[str]:
        """Generate improvement recommendations based on data"""
        recommendations = []
        
        # Check overall success rate
        success_rate = self.performance_stats["success_rate"]
        
        if success_rate < 50:
            recommendations.append("⚠️ Low success rate - Check camera positioning and lighting")
        elif success_rate < 70:
            recommendations.append("⚠️ Moderate success rate - Consider recalibrating vision system")
        else:
            recommendations.append("✅ Good success rate - System performing well")
        
        # Check object-specific performance
        for obj, stats in self.object_stats.items():
            if stats["success_rate"] < 50 and stats["attempts"] > 3:
                recommendations.append(f"⚠️ Difficulty grasping {obj} - May need custom grip strategy")
        
        # Check recent failures
        recent_failures = [
            entry for entry in self.action_history[-10:]
            if entry["result"] == "failure"
        ]
        
        if len(recent_failures) >= 5:
            recommendations.append("🔴 Multiple recent failures - System may need maintenance")
        
        return recommendations
    
    def print_statistics(self):
        """Print formatted statistics to console"""
        print("\n" + "="*60)
        print("📊 LEARNING AGENT - PERFORMANCE STATISTICS")
        print("="*60)
        
        # Overall stats
        print("\n🎯 Overall Performance:")
        print(f"   Total Actions: {self.performance_stats['total_actions']}")
        print(f"   Successful: {self.performance_stats['successful_actions']}")
        print(f"   Failed: {self.performance_stats['failed_actions']}")
        print(f"   Success Rate: {self.performance_stats['success_rate']:.1f}%")
        
        # Object stats
        if self.object_stats:
            print("\n📦 Object-Specific Performance:")
            for obj, stats in self.object_stats.items():
                print(f"   {obj.title()}:")
                print(f"      Attempts: {stats['attempts']}")
                print(f"      Success Rate: {stats['success_rate']:.1f}%")
        
        # Recommendations
        recommendations = self._generate_recommendations()
        if recommendations:
            print("\n💡 Recommendations:")
            for rec in recommendations:
                print(f"   {rec}")
        
        print("="*60 + "\n")


# Test the agent
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 TESTING LEARNING AGENT")
    print("="*60)
    
    agent = LearningAgent()
    
    # Simulate some actions
    print("\n📝 Logging test actions...")
    
    test_actions = [
        {"action": "pick", "object": "bottle", "result": "success", "duration": 3.2},
        {"action": "pick", "object": "cup", "result": "success", "duration": 2.8},
        {"action": "pick", "object": "bottle", "result": "failure", "duration": 4.5, "error": "Object not found"},
        {"action": "pick", "object": "phone", "result": "success", "duration": 3.0},
        {"action": "place", "object": "bottle", "result": "success", "duration": 2.5},
    ]
    
    for action in test_actions:
        agent.log_action(action)
        time.sleep(0.5)
    
    # Print statistics
    agent.print_statistics()
    
    # Get report
    print("\n📄 Generating detailed report...")
    report = agent.get_performance_report()
    print(json.dumps(report['data'], indent=2))



