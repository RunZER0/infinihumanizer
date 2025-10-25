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


@pytest.mark.parametrize("engine_name,test_func,env_keys", ENGINE_REGISTRY)
def test_engine_large_input_handling(engine_name: str, test_func: Callable[[str], str], env_keys: Tuple[str, ...]):
    """
    Regression test for large input handling across all engines.
    Verifies that all engines handle large Academic Stealth prompts with large input text
    consistently - either successfully processing or timing out gracefully without crashing.
    
    This test ensures timeout handling is standardized across Claude, OpenAI, and DeepSeek
    engines to prevent worker crashes on large inputs.
    """
    if not _is_key_configured(env_keys):
        pytest.skip(
            f"Skipping {engine_name} large input test: missing API key(s) {', '.join(env_keys)}"
        )
    
    # Create a large academic text input targeting exactly 20,000 characters
    # This simulates the "Academic Stealth Humanization" scenario with a large essay
    base_text = """
    The Industrial Revolution represents a fundamental transformation in human history that began in Britain 
    during the late eighteenth century and subsequently spread across Europe and North America. This period 
    witnessed profound changes in manufacturing processes, economic structures, and social organization that 
    would reshape the trajectory of human civilization. The transition from agrarian economies to industrial 
    production systems fundamentally altered not only the means of production but also the very fabric of 
    society itself.
    
    The technological innovations that characterized this era were both cause and consequence of broader 
    economic and social changes. The development of steam power, particularly James Watt's improvements to 
    the Newcomen engine, provided a reliable and efficient source of mechanical energy that was no longer 
    dependent on natural forces such as water or wind. This innovation enabled factories to be established 
    in urban centers rather than being constrained to locations near rivers or other natural power sources.
    
    The textile industry emerged as the vanguard of industrialization, with innovations such as the spinning 
    jenny, the water frame, and the power loom dramatically increasing productivity while simultaneously 
    reducing the cost of cloth production. These mechanical advances transformed textile manufacturing from 
    a cottage industry conducted in individual homes to a factory-based system characterized by centralized 
    production and wage labor. The concentration of workers in factories created new forms of labor 
    organization and sparked the development of industrial cities.
    
    The iron and steel industries underwent equally dramatic transformations during this period. Henry Cort's 
    puddling process and the subsequent development of the Bessemer converter enabled the mass production of 
    high-quality iron and steel at unprecedented scales. These materials became the foundation for railway 
    construction, shipbuilding, and the manufacture of machinery, creating a self-reinforcing cycle of 
    industrial expansion. The availability of cheap, reliable iron and steel facilitated the construction 
    of infrastructure that further accelerated industrial development.
    
    Transportation networks expanded dramatically during the Industrial Revolution, with the development of 
    canal systems, improved road networks, and ultimately the revolutionary introduction of railways. The 
    railway system in particular transformed both the geography and the temporal experience of industrial 
    society. Journey times that had previously required days could now be accomplished in hours, while the 
    cost of transporting goods decreased substantially. This revolution in transportation enabled the 
    creation of truly national and international markets for manufactured goods.
    
    The social consequences of industrialization were profound and multifaceted. The migration of workers 
    from rural areas to industrial cities created unprecedented urban growth and new forms of social 
    organization. Factory work imposed new rhythms of labor, with workers subjected to the discipline of 
    the clock and the machine rather than the natural cycles of agricultural production. This transformation 
    in the nature of work had far-reaching implications for family structures, gender roles, and social 
    relationships.
    
    Working conditions in early industrial factories were often harsh and dangerous. Long hours, unsafe 
    machinery, and unhealthy environments characterized much of industrial labor during this period. Child 
    labor was widespread, with young children working in mines and factories under conditions that would 
    later be recognized as exploitative and harmful. These conditions eventually sparked social reform 
    movements and the development of labor organizations that sought to improve working conditions and 
    protect workers' rights.
    
    The economic theories that emerged during this period reflected the profound changes in production 
    and commerce. Adam Smith's analysis of the division of labor and market mechanisms provided a 
    theoretical framework for understanding the efficiency gains achieved through industrial organization. 
    David Ricardo's theory of comparative advantage explained the benefits of international trade and 
    specialization. These economic theories both described and justified the emerging industrial capitalist 
    system, though they also provoked critical responses from thinkers who questioned the social costs of 
    industrial development.
    
    The environmental consequences of industrialization were substantial, though they were not immediately 
    recognized as such by contemporaries. The burning of coal to power steam engines created air pollution 
    in industrial cities, while the disposal of industrial waste contaminated water sources. The extraction 
    of resources to feed industrial production altered landscapes and ecosystems. These environmental impacts 
    would become increasingly evident and problematic in subsequent centuries, though they were viewed as 
    acceptable costs of progress during the height of industrial expansion.
    
    The global dimensions of industrialization extended beyond Europe and North America. The demand for raw 
    materials to feed industrial production drove imperial expansion and the exploitation of resources in 
    colonized territories. Cotton from India and the American South, rubber from Southeast Asia, and minerals 
    from Africa were all integrated into global supply chains that sustained industrial production. This 
    process created economic dependencies and power imbalances that would have lasting consequences for 
    international relations and development patterns.
    """
    
    # Calculate precise repetition factor to reach target size
    target_size = 20000
    base_size = len(base_text)
    repetitions = (target_size // base_size) + 1
    large_academic_text = (base_text * repetitions)[:target_size]
    
    print(f"\n{'=' * 80}")
    print(f"TESTING {engine_name.upper()} ENGINE WITH LARGE INPUT")
    print("=" * 80)
    print(f"📤 Sending large academic text ({len(large_academic_text)} characters)...")
    
    try:
        # This should either succeed or fail gracefully with a timeout error
        # It should NOT crash the worker or hang indefinitely
        result = test_func(large_academic_text)
        
        print(f"✅ SUCCESS! Engine processed large input.")
        print(f"   Output length: {len(result)} characters")
        print(f"   First 100 chars: {result[:100]}...")
        
        # Verify we got some output back
        assert len(result) > 0, "Engine returned empty result"
        assert result != large_academic_text, "Engine returned input unchanged"
        
    except RuntimeError as e:
        error_msg = str(e)
        
        # If it's a timeout error, that's acceptable - we're testing that it fails gracefully
        # Check for timeout indicators: "timeout", "timed out", or specific timeout durations
        # Use case-insensitive matching for robustness
        error_msg_lower = error_msg.lower()
        timeout_indicators = ["timeout", "timed out", "25 second", "apitimeout"]
        is_timeout = any(indicator in error_msg_lower for indicator in timeout_indicators)
        
        if is_timeout:
            print(f"✅ ACCEPTABLE: Engine timed out gracefully (as expected for very large input)")
            print(f"   Error: {error_msg}")
            # This is not a failure - it's the expected behavior for inputs that are too large
            # The important thing is that we got a clean timeout, not a worker crash
        else:
            # Other errors might indicate a real problem
            print(f"⚠️  WARNING: Engine failed with non-timeout error")
            print(f"   Error: {error_msg}")
            raise  # Re-raise to fail the test
    
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {type(e).__name__}: {str(e)}")
        raise


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
