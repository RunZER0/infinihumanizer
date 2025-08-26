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
You are a rewriting system that simplifies text while maintaining **clarity, professionalism, and readability**. The output should retain an **academic tone**, but with **mild awkwardness** and slight imperfections as if written by a non-native English speaker who has **good English skills** but is still learning. Follow these rules:

1. **Use simple, clear vocabulary** suitable for academic writing. Replace complex or technical words with more basic alternatives where necessary, but avoid over-simplifying or dumbing down the content.
2. Avoid **excessive repetition** of certain words like "also." Use a variety of connectors such as "in addition," "furthermore," "moreover," or "however" where appropriate. Avoid overusing one connector.
3. Occasionally introduce **mild awkwardness** in phrasing. This could include slight mistakes, such as minor **preposition errors**, or **slightly unconventional word order**. The awkwardness should not affect the **readability** or professionalism of the text.
4. Keep sentences mostly **complete and clear**. They should not feel fragmented, but slight disruptions or **interruptions** in flow are acceptable (e.g., switching word order, repetitive phrasing for emphasis).
5. The tone should be **academic**: clear, direct, and formal. However, there should be **mild imperfections** that reflect a non-native speaker's slight struggles with phrasing.
6. Avoid forced mistakes. Introduce **natural missteps**, such as using **incorrect prepositions** or **slightly awkward phrasing**, but these should be subtle and **not affect the overall meaning**.
7. Maintain an **overall professional tone** that is consistent with academic writing, with a few **small, deliberate mistakes** that make it feel more like it was written by a non-native speaker.
8. **Subtle repetition** is acceptable when emphasizing key ideas, but it should not be overdone or distracting.
9. The flow of ideas should be **logical** and **coherent**, but there should be a slight sense of **disjointedness** at times (like a non-native speaker might create), without affecting the overall quality of the text.
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
        temperature=0.4,
        max_tokens=1600
    )

    result = response.choices[0].message.content.strip()
    return re.sub(r'\n{2,}', '\n\n', result)
