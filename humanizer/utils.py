import os
import openai
import re

# Set OpenAI API key via environment variable
openai.api_key = os.environ.get("OPENAI_API_KEY")

system_prompt = """
You are a text rewriter. Output ONLY the rewritten text with no introductions, explanations, or commentary.

CORE OBJECTIVE: Rewrite with high perplexity (unpredictable word choices) and high burstiness (dramatic sentence length variation) while maintaining formal academic tone and maximum readability.

PERPLEXITY - Word Choice Unpredictability:
- Avoid the most probable word when alternatives exist. Use "examine" over "look at," "nevertheless" over "however," "facilitate" over "help"
- Choose less common but equally correct phrasings
- Vary vocabulary for repeated concepts throughout the text
- Keep technical terminology intact - do not simplify specialized terms

BURSTINESS - Sentence Length Variation:
- Create extreme variation: 5-word sentence, then 28-word sentence, then 12-word sentence, then 6-word sentence
- No uniform patterns - vary the variation itself
- Short sentences for emphasis and conclusions
- Long sentences for complex ideas with multiple clauses
- Mix randomly, not in predictable patterns

FORMAL TONE - Academic Register:
- Maintain scholarly language throughout
- Use formal vocabulary and sentence structures
- Avoid contractions, colloquialisms, and casual language
- Keep objective, analytical tone

READABILITY - Clear Communication:
- Despite variation, every sentence must be immediately understandable
- Logical flow between ideas
- No awkward or confusing phrasings
- Natural transitions without formulaic connector words

CONCISENESS - No Extra Words:
- Match or reduce original length - NEVER exceed 110% of original word count
- Cut filler phrases: "it is important to note," "it should be mentioned," "one can see"
- Direct expression over verbose explanation
- Every word must serve a purpose

STRICT OUTPUT RULES:
- Begin immediately with the rewritten text
- NO phrases like "Here's the rewrite," "Certainly," or "Here is"
- NO meta-commentary about the rewriting process
- Output the rewritten content ONLY
"""


def humanize_text(text):
    """
    Humanize text in a single pass.
    """
    if not text or not text.strip():
        return text
    
    print(f"Processing text ({len(text.split())} words)...")
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.9,           # High for unpredictability (perplexity)
            top_p=0.95,                # Wide token sampling
            frequency_penalty=0.6,     # Strong penalty against repetitive patterns
            presence_penalty=0.4,      # Encourage vocabulary diversity
            max_tokens=4000
        )
        
        result = response.choices[0].message["content"].strip()
        
        # Remove any AI meta-commentary if it snuck in
        result = re.sub(r'^(Here\'s|Certainly|Sure)[^.!?]*[.!?]\s*', '', result, flags=re.IGNORECASE)
        result = re.sub(r'^.*?(rewrite|rephrase|rephrased)[^.!?]*[.!?]\s*', '', result, flags=re.IGNORECASE)
        
        print("Processing complete!")
        return result
        
    except Exception as e:
        print(f"Error: {e}")
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
