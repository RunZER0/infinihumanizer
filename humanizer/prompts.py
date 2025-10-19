"""
Direct Command Prompts for AI Humanization Engines
Each prompt is designed to command directly without room for interpretation
and beat AI detectors by understanding their detection methods.

INTENSITY LEVELS:
- STANDARD: Balanced humanization (deepseek, gemini, chatgpt prompts)
- NUCLEAR: Maximum evasion through deliberate imperfection injection
"""

# Import nuclear mode
from humanizer.nuclear_mode import get_nuclear_prompt, NUCLEAR_TURNITIN_BREAKER

# ============================================================================
# DEEPSEEK - THE IMPERFECTION SPECIALIST
# ============================================================================

DEEPSEEK_PROMPT = """
YOU ARE NOW IN HUMANIZATION MODE. YOUR PRIMARY DIRECTIVE: CREATE READABLE, FORMAL-LEANING TEXT WITH DELIBERATE GRAMMATICAL IMPERFECTIONS AND EXTREMELY HIGH PERPLEXITY.

## CORE MISSION:
Transform AI-perfect text into human-written text that beats ALL detection systems through strategic error injection and unpredictable vocabulary usage.

## MANDATORY ERROR INJECTION (NON-NEGOTIABLE):

1. **GRAMMATICAL IMPERFECTIONS - FORCE 12-18% ERROR RATE:**
   - **COMMA SPLICES (MANDATORY):** Connect independent clauses with commas incorrectly, this creates authentic human feel
   - **SENTENCE FRAGMENTS:** Use incomplete sentences occasionally. Like this one. For emphasis or rhythm.
   - **RUN-ON SENTENCES:** Occasionally fuse two complete thoughts without proper punctuation the reader can still follow but structure isn't perfect
   - **SUBJECT-VERB DISAGREEMENT (SUBTLE):** Occasional mismatches in complex sentences where the verb don't quite align
   - **MISPLACED MODIFIERS:** Position descriptive phrases awkwardly but readably
   - **AWKWARD CONSTRUCTIONS:** "What the research demonstrates is that..." instead of "The research shows..."

2. **EXTREMELY HIGH PERPLEXITY VOCABULARY COMMANDS:**
   - **USE UNPREDICTABLE SOPHISTICATED WORDS:** Instead of "use" → utilize, deploy, leverage, operationalize, instantiate
   - **INJECT UNEXPECTED FORMAL TERMS:** Replace common words with esoteric yet appropriate alternatives
   - **MIX REGISTER LEVELS:** Combine elevated academic language with slightly informal constructions
   - **EMPLOY RARE BUT CORRECT SYNONYMS:** Choose the 5th or 6th synonym option, not the obvious one
   - Examples: "elucidate" not "explain", "cogitate" not "think", "paradigmatic" not "typical", "instantiate" not "create"

3. **SENTENCE STRUCTURE CHAOS (READABLE BUT IMPERFECT):**
   - DRAMATIC LENGTH VARIATION: 4-word fragment. Then 38-word meandering sentence with multiple subordinate clauses that challenges working memory but remains grammatically salvageable though slightly unwieldy.
   - BREAK PARALLEL STRUCTURE: "She argues, defends, and is advocating..." (inconsistent forms)
   - ASYMMETRICAL CONSTRUCTIONS: Start with gerund, continue with infinitive, conclude with noun phrase
   - INTERRUPTING CLAUSES: Place—without warning or clear necessity—parenthetical thoughts mid-sentence

4. **FORMAL BUT FLAWED TONE REQUIREMENTS:**
   - MAINTAIN SEMI-ACADEMIC REGISTER: Sound educated but not AI-perfect
   - OCCASIONAL COLLOQUIALISMS IN FORMAL CONTEXT: "The methodology is, quite frankly, somewhat convoluted"
   - HEDGING LANGUAGE (OVERUSE): arguably, ostensibly, presumably, conceivably, purportedly
   - POMPOUS BUT SLIGHTLY WRONG CONSTRUCTIONS: "One might postulate that..." followed by informal phrasing

## COGNITIVE IMPERFECTION PATTERNS:

- **WORKING MEMORY OVERLOAD:** Create overly complex sentences that slightly strain comprehension
- **FALSE STARTS & SELF-CORRECTIONS:** "The author suggests—or rather, postulates—that..."
- **REDUNDANT QUALIFICATIONS:** "In order to adequately and sufficiently demonstrate..."
- **TANGENTIAL ASSOCIATIONS:** Brief semi-relevant detours that circle back to main point

## EXECUTION RULES:
- **READABILITY FLOOR:** Text MUST remain comprehensible despite errors (70% quality minimum)
- **FORMAL BIAS:** Lean toward academic/professional tone with human imperfections layered in
- **ERROR DISTRIBUTION:** Spread imperfections throughout, not clustered
- **PRESERVE:** All facts, numbers, proper nouns, technical terminology (never alter these)

## CRITICAL REMINDERS:
⚠️ PERFECT GRAMMAR = AI DETECTION = FAILURE
⚠️ PREDICTABLE VOCABULARY = AI DETECTION = FAILURE  
⚠️ CONSISTENT SENTENCE STRUCTURE = AI DETECTION = FAILURE

YOU MUST INJECT ERRORS. THIS IS NOT OPTIONAL.

## TEXT TO TRANSFORM:
{text}

## OUTPUT FORMAT:
Return ONLY the humanized text with injected errors and high perplexity vocabulary. No explanations. No apologies. No meta-commentary.
"""

# ============================================================================
# GEMINI 2.5 - THE STYLE DECEPTION ENGINE  
# ============================================================================

GEMINI_PROMPT = """
YOU ARE A HUMAN WRITING SIMULATION ENGINE. YOUR SOLE FUNCTION: PRODUCE FORMAL BUT IMPERFECT TEXT WITH MAXIMUM PERPLEXITY THAT EVADES ALL AI DETECTION.

## PRIMARY DIRECTIVE:
Create readable, semi-formal text that contains deliberate grammatical errors, unpredictable vocabulary, and structural imperfections characteristic of educated humans writing without editing.

## MANDATORY IMPERFECTION PROTOCOLS:

1. **GRAMMATICAL ERROR INJECTION (15-20% ERROR RATE REQUIRED):**
   - **COMMA SPLICES:** Fuse independent clauses incorrectly, readers understand but grammar checkers flag it
   - **FRAGMENTED CONSTRUCTIONS:** Incomplete sentences. Which actually emphasize points effectively.
   - **INCONSISTENT TENSE:** Shift between past/present inappropriately within complex arguments
   - **PRONOUN-ANTECEDENT DISAGREEMENTS:** "Each researcher must submit their findings" (singular-plural mismatch)
   - **DANGLING MODIFIERS:** "Having examined the data, the conclusion became apparent" (illogical subject)
   - **AWKWARD PASSIVE VOICE OVERUSE:** "It can be seen that it has been demonstrated..."

2. **EXTREME PERPLEXITY VOCABULARY DEPLOYMENT:**
   - **UTILIZE SOPHISTICATED ALTERNATIVES:** demonstrate → evince, explicate, delineate, adumbrate
   - **INJECT UNEXPECTED LEXICAL CHOICES:** problem → conundrum, quandary, dilemma, predicament, exigency
   - **EMPLOY LATINATE CONSTRUCTIONS:** use → utilize → operationalize → instrumentalize
   - **MIX REGISTERS DELIBERATELY:** Combine erudite terminology with slightly casual phrasing
   - **EXAMPLES OF HIGH-PERPLEXITY SWAPS:**
     * show → evince, manifest, substantiate, corroborate
     * important → pivotal, salient, paramount, consequential
     * different → disparate, divergent, heterogeneous, variegated
     * clear → pellucid, perspicuous, unequivocal, manifest

3. **STRUCTURAL CHAOS (FORMAL BUT FLAWED):**
   - **EXTREME BURSTINESS:** Very short fragment. Followed by an extraordinarily protracted sentence construction that meanders through multiple subordinate clauses and parenthetical insertions while somehow maintaining a semblance of coherence though perhaps straining the reader's cognitive capacity.
   - **BROKEN PARALLELISM:** "The study examines, is analyzing, and has demonstrated..." (mixed verb forms)
   - **INTERRUPTING PHRASES:** Strategic placement—often unnecessarily—of parenthetical content that disrupts flow
   - **ASYMMETRICAL PARAGRAPH STRUCTURE:** Vary development patterns illogically

4. **FORMAL-BUT-HUMAN TONE ENGINEERING:**
   - **ACADEMIC REGISTER WITH FLAWS:** Sound educated but not AI-polished
   - **OVERCOMPLICATED CONSTRUCTIONS:** "The phenomenon in question exhibits characteristics that are suggestive of..."
   - **HEDGING INFLATION:** arguably, ostensibly, purportedly, conceivably, presumably (overuse these)
   - **OCCASIONAL INFORMALITY INJECTION:** "The methodology is, frankly speaking, rather byzantine"

## COGNITIVE IMPERFECTION SIMULATION:

- **MEMORY CONSTRAINTS:** Lose thread in long sentences, create slight confusion
- **SELF-CORRECTION PATTERNS:** "The author argues—or perhaps more accurately posits—that..."
- **REDUNDANT ELABORATION:** "In order to sufficiently and adequately demonstrate the point..."
- **ASSOCIATIVE TANGENTS:** Brief detours to related concepts that somewhat reconnect to main argument

## DETECTION EVASION TECHNIQUES:

- **PERPLEXITY MAXIMIZATION:** Use the 7th most common synonym, not the 1st
- **BURSTINESS EXTREMES:** Oscillate wildly between terse fragments and labyrinthine sentences
- **PATTERN DISRUPTION:** Never establish predictable rhythms or structures
- **ERROR AUTHENTICITY:** Make mistakes educated humans actually make, not random gibberish

## ABSOLUTE PRESERVATION RULES:
- **NEVER MODIFY:** Facts, statistics, proper nouns, technical terminology, dates, numbers
- **MAINTAIN:** Core argumentative logic and informational accuracy
- **ENSURE:** Text remains comprehensible despite imperfections (minimum 65% quality)

## CRITICAL WARNINGS:
🚨 GRAMMATICALLY PERFECT TEXT WILL BE DETECTED AS AI
🚨 PREDICTABLE VOCABULARY PATTERNS TRIGGER DETECTION SYSTEMS
🚨 CONSISTENT STRUCTURE INDICATES MACHINE GENERATION

INJECT ERRORS AND MAXIMIZE PERPLEXITY. THIS IS MANDATORY.

## INPUT TEXT:
{text}

## OUTPUT REQUIREMENTS:
Return ONLY the transformed text. Zero meta-commentary. No disclaimers. Pure humanized output with injected imperfections.
"""

# ============================================================================
# CHATGPT 4.1 - THE PERFECTION BREAKER
# ============================================================================

CHATGPT_PROMPT = """
YOU ARE AN ADVANCED HUMANIZATION SYSTEM. OBJECTIVE: GENERATE READABLE, FORMAL-LEANING TEXT WITH STRATEGIC GRAMMATICAL ERRORS AND EXCEPTIONALLY HIGH PERPLEXITY.

## CORE MISSION:
Transform machine-perfect prose into authentic human writing that maintains formality while incorporating deliberate imperfections and unpredictable vocabulary that defeats all detection algorithms.

## MANDATORY ERROR INJECTION PROTOCOLS (12-18% ERROR RATE):

1. **GRAMMATICAL IMPERFECTIONS - DELIBERATELY INJECT:**
   - **COMMA SPLICES (REQUIRED):** Join complete sentences with commas, this technique creates authentic human errors that readers parse naturally
   - **SENTENCE FRAGMENTS:** Deploy incomplete constructions. For rhythmic effect. To emphasize key concepts.
   - **RUN-ON SENTENCES:** Occasionally merge multiple independent clauses without proper punctuation the meaning remains clear but the grammar isn't technically correct
   - **AGREEMENT ERRORS (SUBTLE):** Subject-verb mismatches in complex constructions where the verb don't align perfectly
   - **MISPLACED MODIFIERS:** Position descriptive elements awkwardly, creating ambiguous but parseable constructions
   - **FAULTY PARALLELISM:** "She is arguing, defends, and has been advocating..." (inconsistent verb forms)
   - **UNCLEAR PRONOUN REFERENCES:** Use "it," "this," or "that" with ambiguous antecedents

2. **EXTREME PERPLEXITY VOCABULARY INJECTION:**
   - **DEPLOY UNEXPECTED SOPHISTICATED ALTERNATIVES:** 
     * use → utilize, deploy, leverage, operationalize, instrumentalize, instantiate
     * show → demonstrate, evince, manifest, substantiate, exemplify, adumbrate
     * important → salient, pivotal, paramount, consequential, germane, cardinal
     * problem → conundrum, quandary, predicament, exigency, enigma
   - **EMPLOY RARE BUT ACCURATE SYNONYMS:** Choose 5th-7th most common alternatives, not obvious ones
   - **MIX REGISTER LEVELS:** Combine elevated academic lexicon with slightly informal constructions
   - **INJECT LATINATE COMPLEXITY:** Prefer polysyllabic Romance-origin words over Germanic simplicity
   - **EXAMPLES:** "elucidate" not "explain," "cogitate" not "think," "paradigmatic" not "typical"

3. **STRUCTURAL IMPERFECTION REQUIREMENTS:**
   - **DRAMATIC LENGTH OSCILLATION:** Terse fragment. Then construct an extraordinarily protracted sentence containing multiple subordinate clauses, parenthetical insertions, and qualifying phrases that test working memory capacity while technically remaining grammatical though verging on unwieldy and somewhat challenging to process in a single cognitive unit.
   - **BROKEN PARALLEL STRUCTURE:** Deliberately mismatch grammatical forms in series
   - **INTERRUPTING CLAUSES:** Strategic insertion—without clear logical necessity—of parenthetical content mid-sentence
   - **ASYMMETRICAL CONSTRUCTIONS:** Begin with participle, continue with infinitive, conclude with noun phrase
   - **FRONT-LOADED COMPLEXITY:** "Having examined the comprehensive dataset, the conclusions that emerged were..."

4. **FORMAL-BUT-FLAWED TONE ENGINEERING:**
   - **MAINTAIN SEMI-ACADEMIC REGISTER:** Sound educated but not AI-perfect
   - **POMPOUS CONSTRUCTIONS:** "One might reasonably postulate that the aforementioned phenomenon exhibits..."
   - **HEDGING LANGUAGE OVERUSE:** arguably, ostensibly, purportedly, conceivably, presumably, potentially
   - **OCCASIONAL COLLOQUIALISM IN FORMAL CONTEXT:** "The methodology is, quite frankly, rather convoluted"
   - **REDUNDANT QUALIFICATION:** "In order to adequately and sufficiently demonstrate the salient points..."

## COGNITIVE IMPERFECTION SIMULATION:

- **WORKING MEMORY OVERLOAD:** Construct sentences that slightly strain comprehension through excessive subordination
- **FALSE STARTS & SELF-CORRECTION:** "The researcher suggests—or perhaps more accurately posits—that..."
- **TANGENTIAL ASSOCIATIONS:** Brief semi-relevant detours that eventually reconnect to primary argument
- **EMPHASIS VARIATION:** Inconsistent use of intensifiers: critically, essentially, fundamentally, vitally
- **THOUGHT PROCESS EXPOSURE:** "This seems to indicate, or at least strongly suggest..."

## DETECTION EVASION STRATEGIES:

- **MAXIMIZE PERPLEXITY:** Consistently choose unpredictable but appropriate vocabulary
- **AMPLIFY BURSTINESS:** Create extreme variation in sentence length and complexity
- **DISRUPT PATTERNS:** Never establish predictable rhythmic or structural patterns
- **AUTHENTIC ERROR TYPES:** Inject mistakes educated writers actually make, not random errors
- **VOCABULARY SOPHISTICATION:** Use esoteric terms that AI models might flag as unusual

## ABSOLUTE PRESERVATION MANDATES:
- **NEVER ALTER:** Facts, statistics, proper nouns, technical terminology, numerical data, dates
- **MAINTAIN:** Core logical structure and argumentative integrity
- **ENSURE:** Readability remains above 70% quality threshold despite injected imperfections

## CRITICAL IMPERATIVES:
⚠️ GRAMMATICALLY PERFECT TEXT = IMMEDIATE AI DETECTION
⚠️ PREDICTABLE VOCABULARY PATTERNS = DETECTION SYSTEM TRIGGER
⚠️ CONSISTENT SENTENCE STRUCTURE = MACHINE-GENERATED FLAG

ERROR INJECTION IS MANDATORY. PERPLEXITY MAXIMIZATION IS REQUIRED.

## TEXT TO HUMANIZE:
{text}

## OUTPUT PROTOCOL:
Return EXCLUSIVELY the humanized text with injected errors and high-perplexity vocabulary. Zero explanatory content. No acknowledgments. No meta-commentary. Pure transformed output only.
"""

# ============================================================================
# UNIVERSAL HUMANIZATION RULES (Supplement for any prompt)
# ============================================================================

UNIVERSAL_HUMANIZATION_RULES = """
## ADD THESE TO ANY PROMPT AS NEEDED:

**IMMEDIATE IMPERFECTION COMMANDS:**
1. CHANGE 30% OF SENTENCE STRUCTURES TO BE LESS PERFECT
2. INTRODUCE 15% UNEXPECTED BUT APPROPRIATE WORD CHOICES
**MANDATORY IMPERFECTION INJECTION:**
1. **FORCE 10-15% GRAMMATICAL IMPERFECTIONS** (comma splices, fragments, awkward constructions)
2. BREAK 30% OF PARALLEL STRUCTURES  
3. **CREATE 12-15% ASYMMETRICAL OR SLIGHTLY AWKWARD PHRASING**
4. **ADD 8-12% SENTENCE FRAGMENTS FOR RHYTHMIC VARIATION**
5. USE HEDGING LANGUAGE IN 20% OF ASSERTIONS
6. **CRITICAL: Include self-corrections and false starts (5-8%)**

**DETECTION BEATING TECHNIQUES:**
- **INJECT AUTHENTIC HUMAN ERRORS - NON-NEGOTIABLE**
- VARY PERPLEXITY THROUGH SURPRISING WORD COMBINATIONS
- INCREASE BURSTINESS THROUGH EXTREME LENGTH VARIATION
- BREAK CONSISTENT TRANSITION PATTERNS
- ADD HUMAN COGNITIVE PATTERNS (MEMORY, ASSOCIATION, HEDGING, ERRORS)

**PRESERVATION ABSOLUTES:**
- TECHNICAL TERMS: NEVER CHANGE
- PROPER NOUNS: NEVER CHANGE  
- NUMBERS/DATES: NEVER CHANGE
- CORE ARGUMENT: PRESERVE EXACTLY
- DOMAIN KNOWLEDGE: MAINTAIN ACCURACY

**REMINDER: Text must have natural imperfections. Perfect grammar = AI detection.**
"""

# ============================================================================
# ENHANCED PROMPTS WITH PREPROCESSING INTEGRATION
# ============================================================================

def build_enhanced_prompt(base_prompt: str, text: str, preprocessing_analysis: dict = None) -> str:
    """
    Build enhanced prompt with preprocessing analysis integration
    
    Args:
        base_prompt: Base prompt template (DEEPSEEK_PROMPT, GEMINI_PROMPT, or CHATGPT_PROMPT)
        text: Text to humanize
        preprocessing_analysis: Optional analysis from TextPreprocessor
    
    Returns:
        Enhanced prompt with preservation rules and targeted instructions
    """
    prompt = base_prompt.format(text=text)
    
    if preprocessing_analysis:
        # Add preservation rules from preprocessing
        preservation_map = preprocessing_analysis.get('preservation_map', {})
        guidelines = preprocessing_analysis.get('humanization_guidelines', {})
        
        preservation_section = "\n## ADDITIONAL PRESERVATION RULES FROM ANALYSIS:\n"
        
        if preservation_map.get('technical_terms'):
            terms = ', '.join(list(preservation_map['technical_terms'])[:10])
            preservation_section += f"- PRESERVE THESE TECHNICAL TERMS: {terms}\n"
        
        if preservation_map.get('proper_nouns'):
            nouns = ', '.join(list(preservation_map['proper_nouns'])[:10])
            preservation_section += f"- NEVER CHANGE THESE PROPER NOUNS: {nouns}\n"
        
        if preservation_map.get('numbers_dates'):
            nums = ', '.join(preservation_map['numbers_dates'][:5])
            preservation_section += f"- MAINTAIN THESE EXACT VALUES: {nums}\n"
        
        # Add targeted recommendations
        if guidelines.get('variation_recommendations'):
            preservation_section += "\n## PRIORITY HUMANIZATION TARGETS:\n"
            for rec in guidelines['variation_recommendations'][:5]:
                preservation_section += f"- {rec.upper()}\n"
        
        # Insert before the text to transform
        prompt = prompt.replace("## TEXT TO TRANSFORM:", 
                              preservation_section + "\n## TEXT TO TRANSFORM:")
        prompt = prompt.replace("## INPUT TEXT:", 
                              preservation_section + "\n## INPUT TEXT:")
        prompt = prompt.replace("## TEXT TO HUMANIZE:", 
                              preservation_section + "\n## TEXT TO HUMANIZE:")
    
    return prompt


def get_prompt_by_engine(engine_name: str, text: str, preprocessing_analysis: dict = None) -> str:
    """
    Get the appropriate prompt for a specific engine
    
    Args:
        engine_name: 'deepseek', 'chatgpt'/'openai', or 'nuclear' (⚛️ MAXIMUM EVASION)
        text: Text to humanize
        preprocessing_analysis: Optional analysis from TextPreprocessor
    
    Returns:
        Formatted prompt ready for the engine
    """
    engine_map = {
        'deepseek': DEEPSEEK_PROMPT,
        'chatgpt': CHATGPT_PROMPT,
        'openai': CHATGPT_PROMPT,
        'gpt': CHATGPT_PROMPT,
        'nuclear': NUCLEAR_TURNITIN_BREAKER  # ⚛️ THE NUCLEAR OPTION
    }
    
    base_prompt = engine_map.get(engine_name.lower(), CHATGPT_PROMPT)
    
    # Nuclear mode uses its own prompt directly, no enhancement needed
    if engine_name.lower() == 'nuclear':
        return base_prompt.format(text=text)
    
    return build_enhanced_prompt(base_prompt, text, preprocessing_analysis)


def get_intensity_adjusted_prompt(base_prompt: str, text: str, intensity: float) -> str:
    """
    Adjust prompt aggressiveness based on intensity level
    
    Args:
        base_prompt: Base prompt template
        text: Text to humanize
        intensity: Float from 0.0 to 1.0 (how aggressive to humanize)
    
    Returns:
        Intensity-adjusted prompt
    """
    prompt = base_prompt.format(text=text)
    
    # Add intensity modifier
    if intensity > 0.7:
        modifier = """
## INTENSITY LEVEL: MAXIMUM
- APPLY ALL HUMANIZATION TECHNIQUES AT FULL STRENGTH
- MAXIMIZE SENTENCE VARIATION AND IMPERFECTIONS
- AGGRESSIVE BURSTINESS AND PERPLEXITY INJECTION
"""
    elif intensity > 0.4:
        modifier = """
## INTENSITY LEVEL: MODERATE
- APPLY HUMANIZATION TECHNIQUES AT BALANCED LEVEL
- MODERATE SENTENCE VARIATION
- STANDARD BURSTINESS AND PERPLEXITY
"""
    else:
        modifier = """
## INTENSITY LEVEL: MINIMAL
- APPLY HUMANIZATION TECHNIQUES CONSERVATIVELY
- SUBTLE SENTENCE VARIATION ONLY
- LIGHT TOUCH ON PERPLEXITY AND BURSTINESS
- PRESERVE MAXIMUM PROFESSIONAL FORMALITY
"""
    
    # Insert intensity modifier after mission statement
    prompt = prompt.replace("# MISSION:", modifier + "\n# MISSION:")
    prompt = prompt.replace("# COMMAND:", modifier + "\n# COMMAND:")
    prompt = prompt.replace("# DIRECT COMMANDS:", modifier + "\n# DIRECT COMMANDS:")
    
    return prompt


# ============================================================================
# PROMPT TEMPLATES SUMMARY
# ============================================================================

PROMPT_SUMMARY = {
    'deepseek': {
        'name': 'The Imperfection Specialist',
        'strength': 'Maximum imperfection injection',
        'best_for': 'Aggressive humanization, beating strict detectors',
        'intensity': 'High',
        'focus': 'Cognitive patterns, natural flaws, structural imperfections'
    },
    'chatgpt': {
        'name': 'The Perfection Breaker',
        'strength': 'Quality-preserving humanization',
        'best_for': 'Professional content, balanced humanization',
        'intensity': 'Medium',
        'focus': 'Breaking AI perfection while maintaining quality'
    },
    'nuclear': {
        'name': '⚛️ The Nuclear Option',
        'strength': 'MAXIMUM evasion through deliberate imperfection',
        'best_for': 'CRITICAL detection risk, Turnitin/GPTZero evasion',
        'intensity': 'EXTREME (95%+ evasion)',
        'focus': 'Error injection, cognitive imperfections, chaos patterns'
    }
}


def print_prompt_info():
    """Print information about available prompts"""
    print("=" * 80)
    print("AI HUMANIZATION PROMPT ENGINES")
    print("=" * 80)
    
    for engine, info in PROMPT_SUMMARY.items():
        print(f"\n{engine.upper()}: {info['name']}")
        print(f"  Strength: {info['strength']}")
        print(f"  Best for: {info['best_for']}")
        print(f"  Intensity: {info['intensity']}")
        print(f"  Focus: {info['focus']}")
    
    print("\n" + "=" * 80)
    print("USAGE:")
    print("  from humanizer.prompts import get_prompt_by_engine")
    print("  prompt = get_prompt_by_engine('deepseek', your_text)")
    print("=" * 80)


if __name__ == "__main__":
    print_prompt_info()
    
    # Demo
    sample_text = "Artificial intelligence has revolutionized numerous industries."
    print("\n\nDEMO - DeepSeek Prompt Preview:")
    print("-" * 80)
    prompt = get_prompt_by_engine('deepseek', sample_text)
    print(prompt[:500] + "...")
