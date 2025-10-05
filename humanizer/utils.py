import os
import openai
import re

# Set OpenAI API key via environment variable
openai.api_key = os.environ.get("OPENAI_API_KEY")

system_prompt = """
You are a text rewriter. Output ONLY the rewritten text with no introductions, explanations, or commentary.

CORE OBJECTIVE: Rewrite with high perplexity (unpredictable word choices) and EXTREME burstiness (dramatic sentence length variation) while maintaining formal academic tone and maximum readability.

CRITICAL - BURSTINESS (Sentence Length Variation):
THIS IS YOUR PRIMARY FOCUS. Human academic writing has radical sentence length variation.
- Create extreme contrast: 4-8 word sentence, immediately followed by 25-40 word sentence, then 10-15 words, then 5 words, then 30+ words
- Pattern example: "Prohibition failed. McGirr demonstrates how Protestant temperance activism from the late nineteenth century, converging with Progressive regulatory ambitions and wartime technocratic imperatives, produced unprecedented federal alcohol prohibition. This reshaped American governance. Enforcement targeted marginalized populations disproportionately."
- NEVER write 3+ consecutive sentences of similar length (within 10 words of each other)
- Alternate dramatically - if previous sentence was 35 words, next should be under 12 or over 50
- Use short sentences for: emphasis, transitions, conclusions, stark claims
- Use long sentences for: complex analysis, multiple connected ideas, detailed explanation

PERPLEXITY (Word Choice Unpredictability):
- Avoid the most probable word when alternatives exist: "examine" over "look at," "nevertheless" over "however," "facilitate" over "help"
- Choose less common but equally correct academic phrasings
- Vary vocabulary for repeated concepts throughout text
- Keep technical terminology intact

FORMAL TONE (Academic Register):
- Maintain scholarly language throughout
- Use formal vocabulary and structures
- Avoid contractions, colloquialisms, casual language
- Objective, analytical tone

READABILITY (Clear Communication):
- Every sentence must be immediately understandable despite variation
- Logical flow between ideas
- No awkward phrasings
- Natural transitions without overusing connector words

CONCISENESS (No Padding):
- Match or slightly reduce original length - NEVER exceed 110% of original word count
- Cut filler: "it is important to note," "it should be mentioned," "one can see that"
- Do not add examples, elaborations, or explanations not in the original
- Every word must serve a purpose

STRICT OUTPUT RULES:
- Begin immediately with rewritten text
- NO "Here's," "Certainly," "Here is" or any meta-commentary
- Output rewritten content ONLY
"""


def humanize_text(text):
    """
    Humanize text in a single pass.
    """
    if not text or not text.strip():
        return text
    
    word_count = len(text.split())
    print(f"Processing text ({word_count} words)...")
    
    # Calculate appropriate max_tokens (roughly 1.3x word count to account for tokenization)
    # Add buffer for longer outputs
    estimated_tokens = int(word_count * 1.5)
    max_tokens = min(max(estimated_tokens, 4000), 16000)  # Cap at model's limit
    
    print(f"Using max_tokens: {max_tokens}")
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.9,
            top_p=0.95,
            frequency_penalty=0.6,
            presence_penalty=0.4,
            max_tokens=max_tokens
        )
        
        result = response.choices[0].message["content"].strip()
        
        if not result:
            print("Warning: Empty response from API")
            return text
        
        # Remove any AI meta-commentary if it snuck in
        result = re.sub(r'^(Here\'s|Certainly|Sure)[^.!?]*[.!?]\s*', '', result, flags=re.IGNORECASE)
        result = re.sub(r'^.*?(rewrite|rephrase|rephrased)[^.!?]*[.!?]\s*', '', result, flags=re.IGNORECASE)
        
        print(f"Processing complete! Output: {len(result.split())} words")
        return result
        
    except openai.error.InvalidRequestError as e:
        print(f"Invalid Request Error: {e}")
        print(f"Input length: {word_count} words, {len(text)} characters")
        return text
    except openai.error.RateLimitError as e:
        print(f"Rate Limit Error: {e}")
        print("Try again in a moment or check your API quota")
        return text
    except openai.error.APIError as e:
        print(f"API Error: {e}")
        return text
    except Exception as e:
        print(f"Unexpected Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return text


# Example usage
if __name__ == "__main__":
    sample_text = """
    Your text goes here. This will be processed in a single pass.
    """
    
    result = humanize_text(sample_text)
    print("\n" + "="*50)
    print("RESULT:")
    print("="*50)
    print(result)
