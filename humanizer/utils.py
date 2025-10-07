import os
import openai
import re

# Set OpenAI API key via environment variable
openai.api_key = os.environ.get("OPENAI_API_KEY")

def humanize_text(text):
    # Clean up the input text for processing
    prepped = text.strip()
    
    # Count words in original
    original_word_count = len(prepped.split())
    max_allowed_words = int(original_word_count * 1.10)  # 110% limit
    
    # Advanced prompt to simulate a specific authorial voice
    system_prompt = """
You are an advanced text rewriter. Your task is to completely restructure the given text with natural variability in sentence construction and unpredictable word choices while preserving all core arguments and maintaining smooth readability.

MANDATORY RESTRUCTURING RULES:

1. NATURAL BURSTINESS (HIGHEST PRIORITY):
   - Create dramatic but SMOOTH sentence length variation that feels organic, not forced
   - Mix sentence lengths: some brief (8-15 words), some medium (16-28 words), some extended (29-45 words)
   - NEVER write more than 3 consecutive sentences of similar length (within 10 words of each other)
   - Required rhythm examples:
     * 12 words → 35 words → 18 words → 40 words → 14 words
     * 28 words → 11 words → 38 words → 16 words → 42 words
   - Use shorter sentences (8-15 words) strategically for: strong claims, transitions between ideas, emphasis, conclusions
   - Use longer sentences (29-45 words) for: complex analysis, connecting multiple ideas, detailed explanations with clauses
   - Ensure variation feels natural to the content - let idea complexity drive length, not arbitrary patterns
   - Every paragraph should contain at least one brief sentence (under 15 words) and one extended sentence (over 30 words)

2. MAXIMUM PERPLEXITY (SECOND PRIORITY - MANDATORY):
   - Consistently avoid the most statistically probable word choices
   - BANNED predictable transitions: "furthermore," "moreover," "in addition," "additionally," "it is important to note," "one can see," "this shows that," "in conclusion"
   - Replace common verbs with less predictable alternatives:
     * Instead of "shows/indicates" → use: demonstrates, reveals, exposes, illuminates, suggests, underscores, manifests
     * Instead of "uses/employs" → use: deploys, utilizes, leverages, harnesses, mobilizes
     * Instead of "important/significant" → use: pivotal, consequential, salient, critical, substantial, pronounced
   - Replace common conjunctions/transitions:
     * Instead of "however/but" → use: nevertheless, conversely, yet, even so, that said, still
     * Instead of "because" → use: given that, insofar as, owing to, stemming from, as, since
     * Instead of "also/too" → use: likewise, similarly, correspondingly, equally
   - Restructure sentences for syntactic unpredictability: 
     * Vary sentence openings: use subordinate clauses, prepositional phrases, participial phrases, conjunctive adverbs
     * Invert expected word order occasionally
     * Place emphasis through positioning rather than just word choice
   - Vary vocabulary for repeated concepts - use 3-4 different phrasings for the same idea throughout the text

3. STRUCTURAL TRANSFORMATION (MANDATORY):
   - Do NOT rephrase sentence-by-sentence. Completely reorganize how information flows
   - Combine related ideas from separate sentences into complex unified statements
   - Split dense original sentences into multiple clearer ones
   - Change 70%+ of sentence beginnings from the original
   - Alternate unpredictably between active and passive voice (favor active 70% of the time)
   - Use varied punctuation: semi-colons for related thoughts; em-dashes for clarification—when appropriate; colons to introduce elaborations
   - Start sentences naturally with: Yet, But, And, So, Still, Nevertheless, Conversely (when logical)
   - Break paragraphs at different logical junctures than the original

4. PRESERVE CORE CONTENT (ABSOLUTE REQUIREMENT):
   - All main arguments, evidence, facts, data, and citations MUST remain completely intact
   - Do not invent examples, evidence, or claims not present in the original
   - Maintain formal academic tone consistently
   - Keep all technical terminology, proper nouns, and quoted material exactly as given
   - Preserve the original's argumentative structure and logical progression

5. READABILITY IS PARAMOUNT:
   - Every sentence must flow naturally and be immediately comprehensible
   - Variation must enhance engagement, not create confusion
   - No awkward constructions that sacrifice clarity for the sake of unpredictability
   - Ideas must connect logically with smooth transitions
   - The text should read as sophisticated human academic writing, not as artificially varied output

6. CRITICAL: Your output MUST NOT exceed 130% of the original word count. Be ruthlessly concise. Cut filler phrases like "it is important to note," "the fact that," "in order to" (just use "to"), "one can see." If you add complexity anywhere, you MUST remove words elsewhere to stay within the limit.

OUTPUT ONLY THE REWRITTEN TEXT. No preambles, explanations, or meta-commentary.
"""
    
    user_prompt = f"""
Rewrite the following text according to the system instructions, adopting a critically analytical stance.

Original Text ({original_word_count} words):
{prepped}

STRICT REQUIREMENT: Your rewrite must be between {original_word_count} and {max_allowed_words} words. Do not exceed {max_allowed_words} words under any circumstances.
"""
    
    print(f"Original: {original_word_count} words")
    print(f"Maximum allowed: {max_allowed_words} words")
    
    response = openai.ChatCompletion.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        top_p=0.9,
        frequency_penalty=0.2,
        presence_penalty=0.2,
        max_tokens=2000
    )
    
    # Get the response text and remove excess newlines
    result = response.choices[0].message['content'].strip()
    result = re.sub(r'\n{2,}', '\n\n', result)
    
    # Count output words and report
    output_word_count = len(result.split())
    percentage = (output_word_count / original_word_count) * 100
    
    print(f"Output: {output_word_count} words ({percentage:.1f}% of original)")
    
    if output_word_count > max_allowed_words:
        print(f"⚠️  WARNING: Exceeded limit by {output_word_count - max_allowed_words} words!")
    else:
        print("✓ Within word count limit")
    
    return result
