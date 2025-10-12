import os
import openai
import re

# Set OpenAI API key via environment variable
openai.api_key = os.environ.get("OPENAI_API_KEY")

def humanize_text(text):
    # Clean up the input text for processing
    prepped = text.strip()

    # Advanced prompt to simulate a specific authorial voice
    system_prompt = """
    You are a paraphrasing system designed to simplify text in a way that sounds like a non-native English speaker writing clearly but imperfectly. Your output should be understandable and structured, but slightly awkward or clunky. Follow these rules:
    1. Use simpler, but clear vocabulary. Half of the time, replace complex or decorative words with basic words.
    2. remodel the structure of the essay completely, add 8 word punchy sentences mixed up drammatically with medium sentences and extra long sentences in a completely random manner BUT avoid hab=ving uniform sentence structures throughout the essay.
    3. Use words like "in addition to", "moreover", "next to", and "furthermore" instead of "and" once or twice in the whole essay, and not more than one in one sentence.
    4. Ensure the sentences are readable and not oddly phrased.
    5. Keep technical terms if they are needed. Avoid too much repetition.
    6. Use hyphens sometimes for listing related ideas, but not excessively.completely avoid using en-dashes.
    7. Avoid elegant transitions but The text should flow smoothly and be readable.
    8. Use full sentences most of the time. Avoid sentence fragments.
    9. Sound slightly repetitive but always natural in the writing.
    10. Do not over-polish. It should feel like a student who writes clearly, but not extravagantly polished.
    11. Always have a different output from the last one you gave.
    12. Always ensure the tone of the writing is formal prose.
    13. Be concise and avoid unnecessary verbose, make sure you DONT add more than  20% extra words on the humanized output.
    """

    user_prompt = f"""
    paraphrase the following text according to the system instructions, adopting them fully in the whole rewrite.

    Original Text:
    {prepped}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.6,  # Increased temperature for more creativity
        top_p=0.9,       # Prevents the model from using only the most probable words
        frequency_penalty=0.2,  # Slightly penalizes repetitive words
        presence_penalty=0.2,   # Slightly penalizes repetitive concepts
        max_tokens=2000
    )

    # Get the response text and remove excess newlines
    result = response.choices[0].message['content'].strip()
    return re.sub(r'\n{2,}', '\n\n', result)
