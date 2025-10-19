"""
Complete Integration Example: Preprocessing + Prompts
Demonstrates the full workflow from analysis to humanization
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from preprocessing import TextPreprocessor
from prompts import (
    get_prompt_by_engine,
    get_intensity_adjusted_prompt,
    DEEPSEEK_PROMPT,
    GEMINI_PROMPT,
    CHATGPT_PROMPT
)


def complete_humanization_workflow(text: str, engine: str = 'deepseek', domain: str = 'general'):
    """
    Complete humanization workflow with preprocessing and prompt generation
    
    Args:
        text: Text to humanize
        engine: 'deepseek', 'gemini', or 'chatgpt'
        domain: Content domain (legal, medical, technical, academic, business, creative, general)
    
    Returns:
        dict: Complete analysis and ready-to-use prompt
    """
    print("=" * 80)
    print("COMPLETE HUMANIZATION WORKFLOW")
    print("=" * 80)
    
    # STEP 1: Preprocessing Analysis
    print("\n[STEP 1] Running preprocessing analysis...")
    preprocessor = TextPreprocessor()
    analysis = preprocessor.preprocess_text(text, domain)
    
    # Show analysis summary
    print(preprocessor.generate_summary_report(analysis))
    
    # STEP 2: Generate Enhanced Prompt
    print("\n[STEP 2] Generating enhanced prompt...")
    prompt = get_prompt_by_engine(engine, text, analysis)
    
    # STEP 3: Get Intensity Recommendation
    intensity = analysis['humanization_guidelines']['intensity_settings']['overall_intensity']
    print(f"\nRecommended intensity: {intensity:.2f}")
    
    # STEP 4: Adjust for intensity
    print(f"\n[STEP 3] Adjusting prompt for intensity level...")
    base_prompts = {
        'deepseek': DEEPSEEK_PROMPT,
        'gemini': GEMINI_PROMPT,
        'chatgpt': CHATGPT_PROMPT
    }
    final_prompt = get_intensity_adjusted_prompt(
        base_prompts.get(engine.lower(), CHATGPT_PROMPT),
        text,
        intensity
    )
    
    print("\n" + "=" * 80)
    print("WORKFLOW COMPLETE - READY FOR AI ENGINE")
    print("=" * 80)
    
    return {
        'analysis': analysis,
        'prompt': final_prompt,
        'intensity': intensity,
        'engine': engine,
        'domain': domain,
        'preservation_rules': analysis['humanization_guidelines']['preservation_rules'],
        'recommendations': analysis['humanization_guidelines']['variation_recommendations']
    }


def demonstrate_all_engines(text: str):
    """
    Demonstrate prompt generation for all three engines
    """
    print("\n" + "=" * 80)
    print("DEMONSTRATION: PROMPTS FOR ALL ENGINES")
    print("=" * 80)
    
    engines = ['deepseek', 'gemini', 'chatgpt']
    
    for engine in engines:
        print(f"\n{'=' * 80}")
        print(f"{engine.upper()} ENGINE")
        print("=" * 80)
        
        prompt = get_prompt_by_engine(engine, text)
        
        # Show first 600 characters of prompt
        print(prompt[:600])
        print("\n... [TRUNCATED] ...\n")
        print(f"Full prompt length: {len(prompt)} characters")


def demonstrate_intensity_levels(text: str):
    """
    Demonstrate how intensity affects prompts
    """
    print("\n" + "=" * 80)
    print("DEMONSTRATION: INTENSITY LEVELS")
    print("=" * 80)
    
    intensities = [
        (0.2, "MINIMAL - Legal/Medical"),
        (0.5, "MODERATE - General"),
        (0.9, "MAXIMUM - Creative")
    ]
    
    for intensity, label in intensities:
        print(f"\n{'-' * 80}")
        print(f"Intensity: {intensity} - {label}")
        print("-" * 80)
        
        prompt = get_intensity_adjusted_prompt(DEEPSEEK_PROMPT, text, intensity)
        
        # Extract intensity modifier
        lines = prompt.split('\n')
        for i, line in enumerate(lines):
            if 'INTENSITY LEVEL' in line:
                print('\n'.join(lines[i:i+6]))
                break


# ============================================================================
# EXAMPLE USAGE SCENARIOS
# ============================================================================

def scenario_1_academic_paper():
    """Scenario: Humanizing an academic paper excerpt"""
    print("\n" + "=" * 80)
    print("SCENARIO 1: Academic Paper")
    print("=" * 80)
    
    text = """
    The implementation of machine learning algorithms in healthcare diagnostics has 
    demonstrated significant improvements in accuracy rates. Moreover, these systems 
    exhibit enhanced pattern recognition capabilities. Furthermore, the integration 
    of neural networks has revolutionized medical imaging analysis. Additionally, 
    predictive analytics continues to transform patient care outcomes.
    """
    
    result = complete_humanization_workflow(text, engine='chatgpt', domain='academic')
    
    print("\nKEY RECOMMENDATIONS:")
    for rec in result['recommendations']:
        print(f"  • {rec}")


def scenario_2_business_content():
    """Scenario: Humanizing business/marketing content"""
    print("\n" + "=" * 80)
    print("SCENARIO 2: Business Content")
    print("=" * 80)
    
    text = """
    Our innovative platform leverages cutting-edge technology to deliver exceptional 
    results. The comprehensive solution provides seamless integration across multiple 
    channels. Organizations can maximize efficiency while minimizing operational costs. 
    The robust framework ensures scalability and reliability for enterprise deployments.
    """
    
    result = complete_humanization_workflow(text, engine='gemini', domain='business')
    
    print("\nPRESERVATION RULES:")
    for rule in result['preservation_rules']:
        print(f"  • {rule}")


def scenario_3_technical_documentation():
    """Scenario: Humanizing technical documentation"""
    print("\n" + "=" * 80)
    print("SCENARIO 3: Technical Documentation")
    print("=" * 80)
    
    text = """
    The API endpoint accepts POST requests with JSON payloads containing authentication 
    tokens. The system validates credentials against the OAuth 2.0 specification and 
    returns a 200 status code upon successful authentication. Error handling implements 
    retry logic with exponential backoff for network failures.
    """
    
    result = complete_humanization_workflow(text, engine='chatgpt', domain='technical')
    
    print(f"\nIntensity: {result['intensity']:.2f} (Lower for technical content)")
    print(f"Engine: {result['engine']} (Quality preservation focus)")


# ============================================================================
# MAIN DEMO
# ============================================================================

if __name__ == "__main__":
    # Sample text with clear AI patterns
    sample_text = """
    Artificial intelligence systems have revolutionized numerous industries. However, 
    these systems require substantial computational resources. Additionally, they must 
    be trained on extensive datasets. Therefore, organizations should carefully consider 
    implementation costs. Furthermore, ethical considerations remain paramount in AI deployment.
    """
    
    print("\n" + "=" * 100)
    print(" " * 30 + "INFINIHUMANIZER INTEGRATION DEMO")
    print("=" * 100)
    
    # Run complete workflow
    result = complete_humanization_workflow(sample_text, engine='deepseek', domain='business')
    
    print("\n\n" + "=" * 100)
    print("FINAL OUTPUT SUMMARY")
    print("=" * 100)
    print(f"Engine: {result['engine'].upper()}")
    print(f"Domain: {result['domain'].upper()}")
    print(f"Intensity: {result['intensity']:.2%}")
    print(f"Prompt Length: {len(result['prompt'])} characters")
    print(f"Preservation Rules: {len(result['preservation_rules'])}")
    print(f"Recommendations: {len(result['recommendations'])}")
    
    # Additional demos
    print("\n\n[Press Enter to see all engine comparisons...]")
    input()
    demonstrate_all_engines(sample_text)
    
    print("\n\n[Press Enter to see intensity level effects...]")
    input()
    demonstrate_intensity_levels(sample_text)
    
    print("\n\n[Press Enter to see scenario examples...]")
    input()
    scenario_1_academic_paper()
    scenario_2_business_content()
    scenario_3_technical_documentation()
    
    print("\n\n" + "=" * 100)
    print("DEMO COMPLETE - Ready for production integration!")
    print("=" * 100)
