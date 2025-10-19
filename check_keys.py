"""
Quick check if API keys are loaded
"""
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ dotenv loaded")
except:
    print("⚠️ dotenv not available")

print("\nAPI Keys Status:")
print(f"CLAUDE_API_KEY: {'✅ SET' if os.getenv('CLAUDE_API_KEY') else '❌ NOT SET'}")
print(f"OPENAI_API_KEY: {'✅ SET' if os.getenv('OPENAI_API_KEY') else '❌ NOT SET'}")
print(f"DEEPSEEK_API_KEY: {'✅ SET' if os.getenv('DEEPSEEK_API_KEY') else '❌ NOT SET'}")

if not any([os.getenv('CLAUDE_API_KEY'), os.getenv('OPENAI_API_KEY'), os.getenv('DEEPSEEK_API_KEY')]):
    print("\n❌ NO API KEYS FOUND!")
    print("   1. Copy .env.example to .env")
    print("   2. Add your API keys to .env")
    print("   3. Run this script again")
else:
    print("\n✅ At least one API key is set!")
