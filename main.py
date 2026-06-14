import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.master_agent import MasterAgent

def main():
    """Main function"""
    print("\n" + "="*70)
    print("🤖 AI-POWERED VOICE-CONTROLLED ROBOTIC GRASPING SYSTEM")
    print("="*70)
    print("\nDeveloped by: [Your Name]")
    print("Version: 1.0.0")
    print("="*70 + "\n")
    
    # Check configuration
    from config.settings import GEMINI_API_KEY
    
    if not GEMINI_API_KEY:
        print("⚠️ WARNING: No Gemini API key found!")
        print("   System will use keyword matching only.")
        print("   Add your API key to: config/api_keys.env\n")
        
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Exiting...")
            return
    
    # Initialize and start system
    try:
        master = MasterAgent()
        master.start()
        
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()


