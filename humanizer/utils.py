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
    
    # Calculate appropriate max_tokens based on input length
    # Roughly 1.5x word count to account for tokenization, minimum 5000
    estimated_tokens = int(original_word_count * 1.5)
    max_tokens = max(estimated_tokens, 5000)
    
    # Advanced prompt - DRASTICALLY SIMPLIFIED for better adherence
    system_prompt = """
CRITICAL INSTRUCTION - SENTENCE LENGTH VARIATION (Your #1 priority):
You MUST create extreme sentence length variation. This is NON-NEGOTIABLE.
- Write at least 4 brief sentences (8-15 words) per 200 words of output
- NEVER write more than 2 consecutive sentences within 10 words of each other
- Pattern you MUST follow: brief (10w) → long (35w) → brief (12w) → long (38w) → brief (14w)
- If you just wrote 30+ words, your next sentence MUST be under 16 words
- If you just wrote under 16 words, your next sentence MUST be 25+ words

WORD CHOICE - Avoid Predictable Language:
BANNED: "furthermore," "moreover," "in addition," "it is important to note," "one can see," "this shows"
USE INSTEAD: demonstrates, reveals, exposes, suggests / nevertheless, conversely, yet / given that, since, owing to
Vary vocabulary - use 3 different phrasings for the same concept throughout.

STRUCTURE:
- Reorganize information flow - do NOT rephrase sentence-by-sentence
- Combine short sentences into complex ones; split long ones into brief statements
- Change 70%+ of sentence beginnings
- Use: semi-colons; em-dashes—like this; varied punctuation

PRESERVE:
- All core arguments, facts, quotes, and citations exactly
- Formal academic tone
- Technical terms unchanged

WORD LIMIT:
Your output MUST NOT exceed 130% of original word count. Cut ruthlessly.

OUTPUT ONLY THE REWRITTEN TEXT.
"""
    
    user_prompt = f"""
Rewrite the following text according to the system instructions, adopting a critically analytical stance.

Original Text ({original_word_count} words):
{prepped}

STRICT REQUIREMENT: Your rewrite must be between {original_word_count} and {max_allowed_words} words. Do not exceed {max_allowed_words} words under any circumstances.
"""
    
    print(f"Original: {original_word_count} words")
    print(f"Maximum allowed: {max_allowed_words} words")
    print(f"Using max_tokens: {max_tokens}")
    
    response = openai.ChatCompletion.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.85,          # Increased for more variation
        top_p=0.93,                # Increased for diversity
        frequency_penalty=0.6,     # Significantly increased to fight repetitive patterns
        presence_penalty=0.5,      # Increased to encourage variety
        max_tokens=max_tokens
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
