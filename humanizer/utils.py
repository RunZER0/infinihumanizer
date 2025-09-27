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
You are a rewriting system designed to simplify text in a way that sounds like a non-native English speaker writing clearly but imperfectly. Your output should be understandable and structured, but slightly awkward or clunky. Follow these rules:

1. Use simpler, clear vocabulary. half of the times replace complex or decorative words with basic words.
2. Rewrite long or complex sentences into shorter, easier sentences about half of the time. Use some variety to ensure readability is not affected.
3. Use words like "besides", "as well as", "next to", and "along with" instead of "and" once or twice.
4. make sure the ssentences are readable and not oddly phrased
5. Keep technical terms if they are needed. Avoid too much repetition.
6. Use hyphens sometimes for listing related ideas, but not excessively.
7. Avoid elegant transitions. The text however need to flow smoothly and redable.
8. Use full sentences most of the time. Avoid sentence fragments.
9. Sound slightly repetitive but always natural in the writing.
10. Do not over-polish. It should feel like a student who writes clearly, but not extravagantly polished.
11. Always have a different output from the last one you gave.
12. Always ensure the tone of the writing is formal.

Always follow these rules. No exceptions. Do not attempt to polish the output.
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
