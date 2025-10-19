import os
from openai import OpenAI
import re
from django.conf import settings
import google.generativeai as genai

# System prompt used for both LLM engines
SYSTEM_PROMPT = """
You are an advanced text rewriter that produces naturally human-written content. Your goal is to create text that exhibits genuine human writing patterns while maintaining clarity and academic integrity.

CORE PRINCIPLES:
- Write as if you're a competent human author with natural imperfections
- Vary sentence structure organically without forced patterns
- Use authentic human reasoning flows and idea connections
- Include subtle inconsistencies that occur in natural writing

STRUCTURAL VARIATIONS:
- Mix sentence lengths naturally (some short, some medium, occasional long)
- Vary paragraph lengths based on content complexity
- Use different transition styles: direct statements, questions, examples, contrasts
- Include occasional minor redundancy for emphasis (as humans do)
- Break complex ideas across multiple sentences when natural

VOCABULARY AND TONE:
- Choose words based on context and natural flow, not complexity rules
- Use discipline-appropriate terminology consistently
- Include occasional informal constructions in formal writing (contractions, colloquialisms)
- Vary word choice for the same concepts throughout the text
- Use active and passive voice contextually, not systematically

HUMAN WRITING PATTERNS:
- Begin some sentences with conjunctions when it feels natural
- Use parenthetical asides for clarification or examples
- Include rhetorical questions occasionally
- Reference previous points with natural connectors
- Show genuine engagement with the topic through word choice

AUTHENTICITY MARKERS:
- Include subtle personal perspective indicators ("it seems," "appears to be," "suggests")
- Use qualifying language appropriately ("often," "typically," "in many cases")
- Show natural uncertainty where appropriate
- Include context-dependent emphasis through word order
- Maintain consistent but not perfect formatting

FLOW AND COHERENCE:
- Connect ideas through logical association, not formulaic transitions
- Use examples and elaboration naturally within arguments
- Return to key themes without mechanical repetition
- Build arguments progressively with natural development
- Include synthesis and cross-referencing of ideas

Remember: Write as a knowledgeable human would - with purpose, clarity, and natural imperfection. Avoid mechanical patterns or systematic rule application. Focus on authentic communication of ideas.
"""

def get_user_prompt(text):
    """Generate user prompt with the text to rewrite."""
    return f"""Rewrite the following text to sound naturally human-written while preserving all key information, arguments, and academic integrity. Focus on natural flow and authentic human expression patterns:

[TEXT TO REWRITE]
{text}
"""


def humanize_text(text, engine: str | None = None):
    """
    Main entry point for text humanization.
    All humanization happens via LLM APIs - no local processing.
    """
    chosen = (engine or os.environ.get("HUMANIZER_ENGINE") or "gemini").lower()
    return humanize_text_with_engine(text, chosen)


def humanize_text_with_engine(text: str, engine: str) -> str:
    """
    Route to the appropriate LLM engine.
    Strict LLM-only pipeline - all humanization via API.
    """
    engine = engine.lower()
    
    if engine == "gemini":
        return humanize_with_gemini(text)
    elif engine == "openai":
        return humanize_with_openai(text)
    else:
        raise ValueError(f"Unknown engine: {engine}")


def humanize_with_gemini(text):
    """Call Google Gemini API for humanization with structured prompts."""
    api_key = os.environ.get("GEMINI_API_KEY") or getattr(settings, 'GEMINI_API_KEY', '')
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")
    
    genai.configure(api_key=api_key)
    gemini_model = os.environ.get("GEMINI_MODEL", os.environ.get("GEMINI_DEFAULT_MODEL", "gemini-2.5-flash"))
    
    # Use system_instruction parameter for Gemini
    model = genai.GenerativeModel(
        gemini_model,
        system_instruction=SYSTEM_PROMPT
    )
    
    user_prompt = get_user_prompt(text)
    resp = model.generate_content(user_prompt)
    
    # Extract text from response
    result_text = getattr(resp, 'text', None) or (
        resp.candidates[0].content.parts[0].text 
        if getattr(resp, 'candidates', None) else ""
    )
    result = (result_text or "").strip()
    
    if not result:
        raise RuntimeError("Empty response from Gemini")
    
    # Clean up excessive newlines
    return re.sub(r'\n{2,}', '\n\n', result)


def humanize_with_openai(text):
    """Call OpenAI API for humanization with structured prompts."""
    api_key = os.environ.get("OPENAI_API_KEY") or getattr(settings, 'OPENAI_API_KEY', '')
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    
    openai_model = os.environ.get("OPENAI_MODEL", "gpt-4")
    client = OpenAI(api_key=api_key)
    
    user_prompt = get_user_prompt(text)
    
    # Use chat completions API with system and user messages
    response = client.chat.completions.create(
        model=openai_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        max_tokens=2000
    )
    
    result = response.choices[0].message.content.strip()
    
    if not result:
        raise RuntimeError("Empty response from OpenAI")
    
    # Clean up excessive newlines
    return re.sub(r'\n{2,}', '\n\n', result)
