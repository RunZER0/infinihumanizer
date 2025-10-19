"""
Diagnostic script to test API connectivity and configuration
Run this to check if your AI engines are configured correctly
NOTE: Gemini removed - it refuses to follow humanization instructions
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from django.conf import settings
from humanizer.utils import humanize_with_openai, humanize_with_deepseek

def check_api_keys():
    """Check if API keys are configured"""
    print("=" * 80)
    print("API KEY CONFIGURATION CHECK")
    print("=" * 80)
    
    # Check environment variables (engines read from os.environ)
    keys = {
        'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY'),
        'DEEPSEEK_API_KEY': os.environ.get('DEEPSEEK_API_KEY'),
    }
    
    # Also check settings
    print("\nChecking os.environ:")
    for key_name, key_value in keys.items():
        if key_value:
            masked = key_value[:10] + "..." + key_value[-4:] if len(key_value) > 14 else "***"
            print(f"✅ {key_name}: {masked}")
        else:
            print(f"❌ {key_name}: NOT SET")
    
    print("\nChecking Django settings:")
    settings_keys = {
        'OPENAI_API_KEY': getattr(settings, 'OPENAI_API_KEY', None),
        'DEEPSEEK_API_KEY': getattr(settings, 'DEEPSEEK_API_KEY', None),
    }
    
    for key_name, key_value in settings_keys.items():
        if key_value:
            masked = key_value[:10] + "..." + key_value[-4:] if len(key_value) > 14 else "***"
            print(f"✅ {key_name}: {masked}")
        else:
            print(f"❌ {key_name}: NOT SET")
    
    print()
    return all(keys.values())


def test_engine(engine_name, test_func):
    """Test a specific engine"""
    print(f"\n{'=' * 80}")
    print(f"TESTING {engine_name.upper()} ENGINE")
    print("=" * 80)
    
    test_text = "This is a simple test sentence to verify the API is working correctly."
    
    try:
        print(f"📤 Sending test request...")
        print(f"   Input: {test_text}")
        
        result = test_func(test_text)
        
        print(f"✅ SUCCESS!")
        print(f"   Output length: {len(result)} characters")
        print(f"   First 100 chars: {result[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED!")
        print(f"   Error: {str(e)}")
        print(f"   Error type: {type(e).__name__}")
        
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()
        
        return False


def main():
    print("\n" + "=" * 80)
    print("INFINIHUMANIZER DIAGNOSTIC TOOL")
    print("=" * 80)
    
    # Check API keys
    all_keys_set = check_api_keys()
    
    if not all_keys_set:
        print("\n⚠️  WARNING: Not all API keys are configured!")
        print("   Set them in your .env file or core/settings.py")
        print("   The engines read API keys from os.environ, so make sure they're in environment!")
        print()
    
    # Test each engine (Gemini removed - refuses instructions)
    results = {}
    
    print("\n" + "=" * 80)
    print("STARTING ENGINE TESTS")
    print("=" * 80)
    
    engines = [
        ('OpenAI', humanize_with_openai),
        ('DeepSeek', humanize_with_deepseek),
    ]
    
    for engine_name, test_func in engines:
        results[engine_name] = test_engine(engine_name, test_func)
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    for engine_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {engine_name}: {status}")
    
    print()
    
    if all(results.values()):
        print("🎉 ALL TESTS PASSED! Your humanizer is ready to use!")
    else:
        print("⚠️  SOME TESTS FAILED. Check the errors above and:")
        print("   1. Verify API keys are correct")
        print("   2. Check your internet connection")
        print("   3. Verify API quotas/limits")
        print("   4. Check if API services are accessible from your location")
        print("   5. IMPORTANT: API keys must be in os.environ (not just Django settings)")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
