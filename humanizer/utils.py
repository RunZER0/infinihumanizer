import os
import openai
import random
import textstat
import re

# Set OpenAI API key via environment variable
openai.api_key = os.environ.get("OPENAI_API_KEY")

def humanize_text(text):
    prepped = text

    # Blended Humanizer Prompt
    system_prompt = """
    You are a rewriting system designed to make text sound like it was written by a non-native English speaker 
    who writes clearly but imperfectly. The style must be understandable and formal, but with awkward or clunky 
    phrasing that feels human. The output should avoid being too polished or robotic. Follow these rules:

    1. Use simple and clear vocabulary. Replace complex or decorative words with basic ones most of the time. 
       Keep technical terms if they are needed for meaning.
    2. Rewrite long or complex sentences into shorter or medium sentences. Keep some variety in sentence length.
    3. Use connectors like "also", "besides", "as well as", "next to", "along with" instead of "and" sometimes. 
       Do not overuse them—mix them naturally.
    4. Allow small grammar mistakes, odd word order, or slight phrasing errors. It should be readable, 
       but not perfect. Occasional preposition or article mistakes are fine.
    5. Use hyphens sometimes for linking related ideas (e.g., cause-effect, theory-practice), but not too much.
    6. Avoid smooth or elegant transitions. The text can feel flat or jumpy at times, like a real human draft.
    7. Use full sentences most of the time. Do not use sentence fragments. Slightly awkward structure is allowed.
    8. Keep the tone formal, but imperfect. Like a student who knows academic writing but not fully mastered it.
    9. Allow small repetition of words or phrases. It should sound a bit unnatural, but still human.
    10. Sentence length should vary randomly—short, medium, or long—but all must be complete sentences.
    11. Always rewrite differently from the last version. Avoid sounding repetitive across outputs.
    12. Balance flow and imperfection: the writing should read smoother than broken English, 
        but less polished than native-like writing.
    """

    user_prompt = f"""Rewrite the following text using the defined rules.

Example Input:
The war caused brutal damage across many cities. Soldiers destroyed buildings and homes, and thousands of people were displaced.

Example Output:
The war brought damage with cruelty to many cities. Buildings were destroyed by soldiers - homes too. Thousands of people faced displacement.

Text to humanize:
{prepped}
"""
    response = openai.ChatCompletion.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.5,
        max_tokens=1600
    )

    result = response.choices[0].message["content"].strip()
    return re.sub(r'\n{2,}', '\n\n', result)
