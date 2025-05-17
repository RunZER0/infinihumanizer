import openai
import os
import random
import textstat
import re
from dotenv import load_dotenv

load_dotenv()  # Load from .env

openai.api_key = os.getenv("OPENAI_API_KEY")
# Step 1: Vocab simplification dictionary
SYNONYMS = {
    "utilize": "use",
    "therefore": "so",
    "subsequently": "then",
    "prioritize": "focus on",
    "implementation": "doing",
    "prohibit": "stop",
    "facilitate": "help",
    "demonstrate": "show",
    "significant": "important",
    "furthermore": "also",
    "approximately": "about",
    "individuals": "people",
    "components": "parts",
    "eliminate": "remove",
    "require": "need",
    "crucial": "important",
    "complex": "complicated",
    "vehicle": "car",
    "performance": "how it works",
    "enhanced": "better",
    "transmitting": "moving",
    "torsional": "twisting",
}

def downgrade_vocab(text):
    for word, replacement in SYNONYMS.items():
        text = re.sub(rf"\b{word}\b", replacement, text, flags=re.IGNORECASE)
    return text

def light_split(text):
    return re.sub(r'(?<=[.!?])\s+(?=[A-Z])', '. ', text)

def humanize_text(text):
    simplified = downgrade_vocab(text)
    prepped = light_split(simplified)

    prompt = (
        "You rewrite text in basic, fourth grade English. Do not smooth the text or improve grammar unless it is broken. Keep sentence structure choppy with long sentences only for readability. Add slight repetition on key phrases. Do not add transitions, polish, or rhetorical flair. Preserve the original structure and ideas but rephrase the wording. Do not explain anything or summarize. Do not simplify concepts. You write like a college student with average fluency and effort. Do not sound fluent or elegant. Introduce small errors. No rhetorical questions. No formatting. Just plain sentences. Use short complete sentences and include some repetitive or awkward phrasing. the reading style of the output should be human - like.\n\n"
        f"{prepped}"
    )

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": """You are a professional human writer and editor. Rewrite the following text to make it sound natural, human-written, and free from the patterns typical of AI-generated content.

Guidelines:
- Use a casual but clear tone.
- Vary sentence structure and length—avoid patterns.
- Replace overly formal or common AI-generated phrases with natural, real-life equivalents.
- Simplify complex vocabulary with more familiar synonyms, unless a technical term is essential.
- Break up long sentences into shorter, conversational ones.
- Avoid robotic phrasing, generic intros, or conclusions.
- Keep the meaning the same but express it in a unique and engaging way."""
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.4,
        max_tokens=1600
    )

    result = response.choices[0].message.content.strip()
    return re.sub(r'\n{2,}', '\n\n', result)
