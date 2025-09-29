# requirements: openai==0.28.1 (legacy SDK)
# pip install "openai==0.28.1"

import os
import re
import time
import random
import openai

openai.api_key = os.environ.get("OPENAI_API_KEY")

DEFAULT_MODELS = ["gpt-4.1"]

# --- MULTI-PASS SYSTEM PROMPTS ---
PASS_1_PROMPT = """
You're a university student rewriting your own academic draft. You understand the content deeply but you're reworking it for better flow while maintaining formal academic tone.

Write like you're thinking through the material formally - not translating or simplifying, but genuinely re-expressing your understanding in proper academic language. Some sentences will be longer when building complex arguments, shorter when stating clear points. You'll occasionally rephrase for clarity because that's natural in academic writing.

Maintain formal academic standards throughout. Don't artificially vary anything. Just write how the ideas connect logically.
""".strip()

PASS_2_PROMPT = """
You're editing this academic draft one final time. The content is solid but you're refining for clarity while preserving formality:

- Ensure all language maintains academic tone
- Remove any phrasing that sounds artificially stiff or robotic
- If arguments feel overexplained, make them more concise
- If transitions feel abrupt, strengthen the logical connections
- Keep the formal scholarly voice consistent

You're not following a template - you're ensuring this reads as credible academic work.
""".strip()


def chunk_text(text: str, max_chunk_size: int = 800) -> list:
    """Split text into chunks by paragraphs, staying under max_chunk_size."""
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = []
    current_size = 0
    
    for para in paragraphs:
        para_size = len(para)
        if current_size + para_size > max_chunk_size and current_chunk:
            chunks.append('\n\n'.join(current_chunk))
            current_chunk = [para]
            current_size = para_size
        else:
            current_chunk.append(para)
            current_size += para_size
    
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))
    
    return chunks


def call_openai(
    prompt: str,
    system_prompt: str,
    model: str,
    temperature: float,
    frequency_penalty: float,
    presence_penalty: float,
    max_tokens: int = 1600,
) -> str:
    """Single API call with error handling."""
    resp = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=0.96,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
    )
    return resp["choices"][0]["message"]["content"].strip()


def humanize_text(
    text: str,
    models: list = None,
    max_retries: int = 3,
    retry_backoff_seconds: float = 2.0,
) -> str:
    """
    TWO-PASS humanization with chunking for better results.
    """
    
    if not openai.api_key:
        raise RuntimeError("OPENAI_API_KEY is not set in environment.")
    
    if models is None:
        models = DEFAULT_MODELS
    
    print(f"Starting humanization with model(s): {models}")
    
    # Split into manageable chunks
    chunks = chunk_text(text, max_chunk_size=800)
    print(f"Split text into {len(chunks)} chunks")
    
    last_error = None
    
    for model in models:
        for attempt in range(1, max_retries + 1):
            try:
                # PASS 1: Initial rewrite with high variation
                pass1_chunks = []
                print(f"Starting PASS 1 with {len(chunks)} chunks...")
                for i, chunk in enumerate(chunks):
                    print(f"Processing chunk {i+1}/{len(chunks)}")
                    # Vary temperature per chunk slightly for inconsistency
                    temp_variation = random.uniform(0.88, 0.98)
                    freq_variation = random.uniform(0.5, 0.7)
                    
                    result = call_openai(
                        prompt=f"Rewrite this section in your own words:\n\n{chunk}",
                        system_prompt=PASS_1_PROMPT,
                        model=model,
                        temperature=temp_variation,
                        frequency_penalty=freq_variation,
                        presence_penalty=0.3,
                    )
                    pass1_chunks.append(result)
                    
                    # Small delay between chunks to vary request patterns
                    if i < len(chunks) - 1:
                        time.sleep(random.uniform(0.3, 0.8))
                
                pass1_full = '\n\n'.join(pass1_chunks)
                print("PASS 1 complete. Starting PASS 2...")
                
                # PASS 2: Polish pass with different temperature profile
                final_result = call_openai(
                    prompt=f"Give this one final polish to make it sound natural:\n\n{pass1_full}",
                    system_prompt=PASS_2_PROMPT,
                    model=model,
                    temperature=random.uniform(0.75, 0.85),  # Lower temp for polish
                    frequency_penalty=0.3,
                    presence_penalty=0.1,
                    max_tokens=2500,
                )
                
                print("PASS 2 complete. Returning result.")
                # Clean up excessive whitespace
                return re.sub(r"\n{3,}", "\n\n", final_result)
                
            except openai.error.RateLimitError as e:
                last_error = e
                time.sleep(retry_backoff_seconds * attempt)
                
            except (openai.error.APIError, openai.error.Timeout, openai.error.APIConnectionError) as e:
                last_error = e
                time.sleep(retry_backoff_seconds * attempt)
                
            except openai.error.InvalidRequestError as e:
                last_error = e
                break
                
            except Exception as e:
                last_error = e
                break
    
    raise RuntimeError(f"All model attempts failed. Last error: {last_error!r}")


# --- Example usage ---
if __name__ == "__main__":
    sample = """
    Artificial intelligence has transformed modern computing in unprecedented ways. 
    Machine learning algorithms can now process vast amounts of data with remarkable 
    efficiency. These systems continue to evolve and improve over time.
    """
    try:
        print(humanize_text(sample))
    except Exception as exc:
        print(f"Error: {exc}")
