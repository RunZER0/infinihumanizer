"""Diagnostic script and pytest coverage for configured humanizer engines."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Callable, Iterable, Tuple

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
import django

django.setup()

from django.conf import settings
from humanizer.utils import (
    humanize_with_claude,
    humanize_with_deepseek,
    humanize_with_openai,
)


ENGINE_REGISTRY: Tuple[Tuple[str, Callable[[str], str], Tuple[str, ...]], ...] = (
    ("Claude", humanize_with_claude, ("ANTHROPIC_API_KEY", "CLAUDE_API_KEY")),
    ("OpenAI", humanize_with_openai, ("OPENAI_API_KEY",)),
    ("DeepSeek", humanize_with_deepseek, ("DEEPSEEK_API_KEY",)),
)


def _mask_key(value: str | None) -> str:
    if not value:
        return "NOT SET"
    return value[:10] + "..." + value[-4:] if len(value) > 14 else "***"


def _is_key_configured(possible_keys: Iterable[str]) -> bool:
    return any(os.environ.get(key) for key in possible_keys)

def check_api_keys() -> bool:
    """Check if API keys are configured."""
    print("=" * 80)
    print("API KEY CONFIGURATION CHECK")
    print("=" * 80)
    
    print("\nChecking os.environ:")
    env_results = {}
    for engine_name, _, env_keys in ENGINE_REGISTRY:
        configured = _is_key_configured(env_keys)
        env_results[engine_name] = configured
        display_key = env_keys[0]
        env_value = next((os.environ.get(key) for key in env_keys if os.environ.get(key)), None)
        masked = _mask_key(env_value)
        status = "✅" if configured else "❌"
        print(f"{status} {display_key}: {masked}")

    print("\nChecking Django settings:")
    for engine_name, _, env_keys in ENGINE_REGISTRY:
        setting_key = env_keys[0]
        setting_value = getattr(settings, setting_key, None)
        masked = _mask_key(setting_value)
        status = "✅" if setting_value else "❌"
        print(f"{status} {setting_key}: {masked}")

    print()
    return all(env_results.values())


def _exercise_engine(engine_name: str, test_func: Callable[[str], str]) -> bool:
    """Test a specific engine."""
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


@pytest.mark.parametrize("engine_name,test_func,env_keys", ENGINE_REGISTRY)
def test_engine_connectivity(engine_name: str, test_func: Callable[[str], str], env_keys: Tuple[str, ...]):
    if not _is_key_configured(env_keys):
        pytest.skip(
            f"Skipping {engine_name} test: missing API key(s) {', '.join(env_keys)}"
        )

    assert _exercise_engine(engine_name, test_func)


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
    
    # Test each supported engine
    results = {}

    print("\n" + "=" * 80)
    print("STARTING ENGINE TESTS")
    print("=" * 80)

    for engine_name, test_func, env_keys in ENGINE_REGISTRY:
        if not _is_key_configured(env_keys):
            print(
                f"⚠️  Skipping {engine_name}: missing API key(s) "
                f"{', '.join(env_keys)}"
            )
            results[engine_name] = None
            continue

        results[engine_name] = _exercise_engine(engine_name, test_func)
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    for engine_name, success in results.items():
        if success is True:
            status = "✅ PASS"
        elif success is False:
            status = "❌ FAIL"
        else:
            status = "⚠️ SKIPPED"
        print(f"   {engine_name}: {status}")

    print()

    any_failures = any(result is False for result in results.values())
    any_successes = any(result is True for result in results.values())

    if any_failures:
        print("⚠️  SOME TESTS FAILED. Check the errors above and:")
        print("   1. Verify API keys are correct")
        print("   2. Check your internet connection")
        print("   3. Verify API quotas/limits")
        print("   4. Check if API services are accessible from your location")
        print("   5. IMPORTANT: API keys must be in os.environ (not just Django settings)")
    elif any_successes:
        print("🎉 ALL CONFIGURED TESTS PASSED! Your humanizer is ready to use!")
    else:
        print("⚠️  All tests were skipped because API keys are missing.")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
