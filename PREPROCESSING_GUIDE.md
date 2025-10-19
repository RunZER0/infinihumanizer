# Pre-Processing Module Guide

## Overview

The pre-processing stage analyzes raw AI-generated text to identify patterns, extract constraints, and prepare for safe humanization while preserving critical content.

## What This Stage Does

### 1. AI Pattern Detection
- Identifies telltale AI writing characteristics
- Flags overly perfect structures
- Detects unnatural consistency patterns

### 2. Content Preservation Mapping
- Extracts technical terms, proper nouns, and domain-specific language
- Identifies core arguments and logical structures
- Maps what MUST remain unchanged

### 3. Safe Variation Zones
- Finds areas where humanization can be safely applied
- Identifies sentence structures ripe for variation
- Flags high-risk areas to avoid

### 4. Intensity Calibration
- Analyzes text complexity and determines appropriate humanization level
- Sets boundaries for variation intensity
- Prevents over-humanization of already natural text

## Usage

### Basic Usage

```python
from humanizer.preprocessing import TextPreprocessor

# Initialize
preprocessor = TextPreprocessor()

# Analyze text
text = """Your AI-generated text here..."""
analysis = preprocessor.preprocess_text(text, domain="business")

# Generate report
report = preprocessor.generate_summary_report(analysis)
print(report)
```

### Domain Types

- `legal` - Legal documents (intensity: 0.3)
- `medical` - Medical/health content (intensity: 0.2)
- `technical` - Technical documentation (intensity: 0.4)
- `academic` - Academic papers (intensity: 0.6)
- `business` - Business content (intensity: 0.7)
- `creative` - Creative writing (intensity: 0.9)
- `general` - General content (intensity: 0.5)

## Key Outputs

### 1. Preservation Map
Elements that must stay exactly the same:
- Technical terms
- Proper nouns
- Numbers and dates
- Acronyms
- Quotes and citations

### 2. AI Pattern Analysis
Specific AI tells to target:
- Overly consistent sentence lengths
- Transition word overuse
- Low vocabulary diversity
- Perfect parallel structures
- Repetitive sentence starts

### 3. Safe Variation Zones
Sentences identified as safe for humanization with:
- Risk level (low/medium/high)
- Recommended variation types
- Reasoning for classification

### 4. Humanization Guidelines
- **Preservation rules**: What to protect
- **Variation recommendations**: What to change
- **Intensity settings**: How aggressively to humanize
- **Model-specific instructions**: Tailored prompts for each LLM

### 5. Risk Assessment
- High-risk elements
- Medium-risk elements
- Recommended precautions

## Integration with Humanizer

The preprocessing analysis can be used to:

1. **Generate better prompts** for LLM humanization
2. **Set dynamic temperature** based on intensity settings
3. **Protect critical content** during humanization
4. **Focus on problem areas** identified by AI pattern detection

### Example Integration

```python
# In views.py or utils.py
from humanizer.preprocessing import TextPreprocessor

def humanize_with_preprocessing(text, engine, domain="general"):
    # Pre-process
    preprocessor = TextPreprocessor()
    analysis = preprocessor.preprocess_text(text, domain)
    
    # Extract guidelines
    guidelines = analysis['humanization_guidelines']
    preservation_rules = guidelines['preservation_rules']
    intensity = guidelines['intensity_settings']['overall_intensity']
    
    # Build enhanced prompt
    prompt = f"""
    Humanize this text with the following rules:
    
    {chr(10).join(preservation_rules)}
    
    Recommendations:
    {chr(10).join(guidelines['variation_recommendations'])}
    
    Humanization intensity: {intensity:.1%}
    
    Text to humanize:
    {text}
    """
    
    # Send to LLM with adjusted temperature
    temperature = 0.3 + (intensity * 0.5)  # Range: 0.3 to 0.8
    
    return engine.process(prompt, temperature)
```

## Analysis Structure

```python
{
    'original_text': str,
    'domain': str,
    'preservation_map': {
        'technical_terms': set,
        'proper_nouns': set,
        'numbers_dates': list,
        'acronyms': set,
        'quotes_citations': list
    },
    'ai_patterns': {
        'sentence_length_consistency': {...},
        'transition_overuse': {...},
        'vocabulary_repetition': {...},
        'perfection_indicators': {...},
        'structural_patterns': {...}
    },
    'safe_variation_zones': [
        {
            'sentence_index': int,
            'sentence': str,
            'safe_for_variation': bool,
            'variation_types': list,
            'risk_level': str,
            'reasoning': list
        }
    ],
    'humanization_guidelines': {
        'preservation_rules': list,
        'variation_recommendations': list,
        'intensity_settings': {
            'overall_intensity': float,
            'sentence_variation_intensity': float,
            'vocabulary_intensity': float,
            'structural_intensity': float
        },
        'model_specific_instructions': {
            'chatgpt': str,
            'deepseek': str,
            'gemini': str
        }
    },
    'risk_assessment': {
        'high_risk_elements': list,
        'medium_risk_elements': list,
        'recommended_precautions': list
    }
}
```

## Example Output

```
=== PRE-PROCESSING ANALYSIS REPORT ===

Domain: business
Text length: 37 words

PRESERVATION ELEMENTS:
  - Technical terms: 2
  - Proper nouns: 5
  - Numbers/dates: 3
  - Acronyms: 1

AI PATTERNS DETECTED: 3 issues
  - sentence_length_consistency: overly_consistent_sentence_lengths
  - transition_overuse: however, therefore, additionally
  - perfection_indicators: perfect_parallel_structures

SAFE VARIATION ZONES: 4/6 sentences
RECOMMENDED INTENSITY: 0.70

RECOMMENDATIONS:
  • Vary sentence lengths dramatically
  • Reduce overuse of: however, therefore, additionally
  • Break up perfect parallel structures occasionally
```

## Benefits

1. **Safety First**: Prevents accidental changes to critical content
2. **Targeted Humanization**: Focuses on actual AI patterns, not random changes
3. **Domain Awareness**: Adjusts intensity based on content type
4. **Model Optimization**: Provides specific instructions for each LLM
5. **Risk Management**: Identifies and handles high-risk content appropriately

## Dependencies

- `numpy` - For statistical analysis
- `re` - For pattern matching
- `collections.Counter` - For word frequency analysis

## Future Enhancements

- [ ] spaCy integration for advanced NLP (optional)
- [ ] Machine learning pattern detection
- [ ] Custom domain rules configuration
- [ ] Multi-language support
- [ ] Real-time analysis feedback in UI

## Testing

Run the demo:
```bash
python humanizer/preprocessing.py
```

This will demonstrate the preprocessor with sample text and show all available features.
