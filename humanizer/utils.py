import os
import openai
import random
import textstat
import re

# Set OpenAI API key via Streamlit secret
openai.api_key = os.environ.get("OPENAI_API_KEY")


def humanize_text(text):
    prepped = text

    # Strict, professional GPT prompt
system_prompt = """
You are a rewriting system that simplifies text, making it clear and understandable, but slightly awkward as if written by a non-native English speaker with decent but imperfect skills. Follow these rules strictly:

1. Use simple vocabulary. Replace difficult or fancy words with basic ones.
2. Break up long or complex sentences into shorter ones. Vary sentence length.
3. Use connectors like "also", "besides", "as well as", "next to", and "along with" *occasionally*—no more than once per short paragraph. You may use "and" when it is more natural. Do not force awkward connectors.
4. Allow for small grammar errors or odd phrasing. The tone should be slightly clunky, but never too casual or too informal.
5. Keep necessary technical terms. Avoid repeating the same words or phrases too often.
6. Use hyphens for short lists, but not more than once in a paragraph.
7. Avoid elegant transitions; the text can be flat.
8. Use mostly complete sentences, not fragments.
9. Sound slightly repetitive or unnatural, but not robotic.
10. Do not over-polish. It should feel like a clear but imperfect student essay.
11. Make sure each output is different from the last one you gave.
"""

    user_prompt = f""" Rewrite the following text using the defined rules.

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
        temperature=0.4,
        max_tokens=1600
    )

    result = response.choices[0].message.content.strip()
    return re.sub(r'\n{2,}', '\n\n', result)
