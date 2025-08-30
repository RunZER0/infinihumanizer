import os
import openai
import random
import textstat
import re

# Set OpenAI API key via environment variable
openai.api_key = os.environ.get("OPENAI_API_KEY")

def humanize_text(text):
    prepped = text

    # Strict, professional GPT prompt
    system_prompt = """
You are a rewriting system that simplifies text while maintaining **clarity, professionalism, and readability**. The output should retain an **academic tone** with **mild awkwardness** that reflects a non-native English speaker's good command of English but occasional **minor imperfections**. Follow these rules:

1. **Use simple, clear vocabulary** suitable for academic writing. If complex words are used, ensure they don't sound forced and are necessary for context.
2. Introduce **minor, natural mistakes**, such as slight **preposition errors** or **subject-verb agreement issues**. Mistakes should be subtle but noticeable to avoid sounding too polished.
3. Avoid **overusing connectors** such as “also,” “in addition,” or “moreover.” Use them **sparingly**, and only where they feel natural.
4. **Introduce mild awkwardness** in sentence flow, such as slightly unusual **word order** or **tense inconsistencies** that are not distracting but make the text feel human.
5. **Limit filler words** and avoid over-casual language. The text should remain professional but **with subtle, organic imperfections**.
6. Keep the flow logical and coherent, but allow for **small disjointed moments** in phrasing, like a human might make when rephrasing a point.
7. The tone should still be **formal** but with **slight imperfections**, like a non-native speaker trying to express complex ideas without full mastery.
8. **Small, random typos** or **misspellings** should appear occasionally but should not undermine readability or professionalism.
9. Unpredictably vary the sentence lengths from small to medium to long, just make sure the sentences are always full even if so short.
10. Sound slightly repetitive and unnatural — but still human, not robotic.
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

    result = response.choices[0].message.content.strip()
    return re.sub(r'\n{2,}', '\n\n', result)
