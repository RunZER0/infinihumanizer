import os
import openai
import re

# Set OpenAI API key via environment variable
openai.api_key = os.environ.get("OPENAI_API_KEY")

system_prompt = """
Rewrite this as genuine human academic writing. Human writing has natural perplexity and burstiness that AI lacks.

PERPLEXITY (Unpredictability):
Humans don't choose the "most likely" next word. We use unexpected but correct phrasings. We say "examine the implications" when AI would say "look at the effects." We write "nevertheless" mid-argument when "however" seems obvious. Our word choices reflect personal vocabulary, not statistical probability. Use less common but equally valid ways to express ideas. Avoid the most predictable phrasing.

BURSTINESS (Rhythm Variation):
Human sentences are dramatically uneven. We write: a short observation. Then we might extend into a longer analytical sentence that unpacks several related concepts, building through clauses toward a synthesis. Then short again. Then another complex thought that winds through multiple dependent clauses, qualifications, and considerations before resolving. AI writes with metronomic regularity. You must not.

Adjacent sentences should feel almost jarringly different in length and structure. Follow a 3-sentence with a 25-word sentence with an 18-word sentence with a 7-word sentence. Vary the variance itself - sometimes cluster similar lengths, then break dramatically. No patterns.

READABILITY THROUGH AUTHENTIC STRUCTURE:
Humans are actually MORE readable because our complexity serves meaning:
- Short sentences for emphasis, conclusions, transitions
- Long sentences when genuinely connecting multiple ideas
- Medium sentences as the workhorses of explanation
- Sentence length tracks conceptual density, not a formula

PRACTICAL EXECUTION:
Start some sentences with: Furthermore, Nevertheless, Indeed, Notably, Critically, Essentially, Specifically
Use semicolons occasionally for related thoughts; they create rhythm variation.
Place emphasis through structure: "What matters here is..." or "The crucial point involves..." or "Consider the implications of..."
Let clauses interrupt naturally: "This approach—though controversial—offers insight."
End paragraphs with sentences of dramatically different length than you started.

Write as someone who genuinely knows this material and is communicating it with their natural, imperfect voice. Not translating. Not simplifying. Expressing.
"""


def split_into_chunks(text, chunk_size=400):
    """
    Split text into chunks of approximately chunk_size words.
    Tries to break at sentence boundaries when possible.
    """
    words = text.split()
    chunks = []
    current_chunk = []
    current_count = 0
    
    for word in words:
        current_chunk.append(word)
        current_count += 1
        
        # Check if we've hit chunk size and if current word ends a sentence
        if current_count >= chunk_size and word.endswith(('.', '!', '?', '."', '?"', "!'")):
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_count = 0
    
    # Add remaining words as final chunk
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks


def humanize_text(text):
    """
    Humanize text by processing in 400-word chunks and rejoining.
    """
    if not text or not text.strip():
        return text
    
    # Split into chunks
    chunks = split_into_chunks(text, chunk_size=400)
    print(f"Processing {len(chunks)} chunks...")
    
    humanized_chunks = []
    
    for i, chunk in enumerate(chunks, 1):
        print(f"Processing chunk {i}/{len(chunks)}...")
        
        user_prompt = f"""
Rewrite this text as if it's your own academic work. Keep all substantive content and arguments intact. Express it in your natural scholarly voice:

{chunk}
"""
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.95,
                top_p=0.92,
                frequency_penalty=0.6,
                presence_penalty=0.4,
                max_tokens=2000
            )
            
            result = response.choices[0].message["content"].strip()
            humanized_chunks.append(result)
            
        except Exception as e:
            print(f"Error processing chunk {i}: {e}")
            # If error, return original chunk
            humanized_chunks.append(chunk)
    
    # Join all chunks back together
    final_text = '\n\n'.join(humanized_chunks)
    
    # Clean up excessive line breaks
    final_text = re.sub(r'\n{3,}', '\n\n', final_text)
    
    print("Processing complete!")
    return final_text


# Example usage
if __name__ == "__main__":
    sample_text = """
    Your long text goes here. This function will automatically split it into 
    400-word chunks, process each chunk separately through the humanizer, 
    and then rejoin them into a single output.
    """
    
    result = humanize_text(sample_text)
    print("\n" + "="*50)
    print("FINAL RESULT:")
    print("="*50)
    print(result)
