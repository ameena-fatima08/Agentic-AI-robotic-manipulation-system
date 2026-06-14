import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.master_agent import MasterAgent

def main():
    """Start the agentic system"""
    try:
        system = MasterAgent()
        system.run()
    except KeyboardInterrupt:
        print("\n System stopped.")
    except Exception as e:
        print(f" Error: {e}")

if __name__ == "__main__":
    main()