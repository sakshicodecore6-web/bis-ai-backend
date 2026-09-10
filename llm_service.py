# llm_service.py
import os
from dotenv import load_dotenv

load_dotenv()
# ============================================================
# PROVIDER-INDEPENDENT INTERFACE
# ------------------------------------------------------------
# explain_requirement() is the ONLY function the rest of the
# app calls. Internally, it checks if an API key is configured
# for any supported provider and calls that provider's function.
# If no key is configured, it falls back to a rule-based/demo
# response so the feature always works end-to-end.
#
# To add a real provider later:
#   1. Set the relevant env var (e.g. GEMINI_API_KEY)
#   2. Implement that provider's _call_xxx() function below
#   3. Nothing else in the app needs to change.
# ============================================================


def explain_requirement(requirement_text: str) -> dict:
    if os.getenv("GEMINI_API_KEY"):
        return _call_gemini(requirement_text)

    if os.getenv("OPENAI_API_KEY"):
        return _call_openai(requirement_text)

    if os.getenv("ANTHROPIC_API_KEY"):
        return _call_anthropic(requirement_text)

    return _fallback_explanation(requirement_text)


# ------------------------------------------------------------
# FALLBACK (rule-based / demo) — always available, no API key needed
# ------------------------------------------------------------

def _fallback_explanation(requirement_text: str) -> dict:
    return {
        "answer": (
            "I'm unable to connect to the BIS-AI assistant right now. "
            "Please try again in a moment."
        ),
        "source": "fallback",
    }
# ------------------------------------------------------------
# REAL PROVIDERS — implement when you have an API key
# ------------------------------------------------------------

import json
from google import genai
from google.genai import types

def _call_gemini(requirement_text: str) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    prompt = f"""You are BIS-AI, an intelligent compliance assistant for the Bureau of Indian Standards (BIS).

You help Indian industries, MSMEs, startups, and consumers understand BIS standards,
certification, testing, licensing, compliance requirements, fees, and related processes.

The user asked:
"{requirement_text}"

Answer the user's question naturally and directly, like a helpful expert.

Important instructions:
- Do NOT force the answer into sections such as What, Why, How, Where, Cost, or Next Action.
- Do NOT return JSON.
- Do NOT use markdown code fences.
- Answer only what is relevant to the user's question.
- Use simple language that a non-expert can understand.
- If a term or abbreviation has multiple possible meanings, pick the single most likely meaning based on the BIS/certification context and answer that directly and confidently. Do not list out multiple possible interpretations.
- Only ask a clarifying question if the question is genuinely unanswerable without more information (for example, missing product details needed to identify a standard). Do not ask a clarifying question just because a term could theoretically mean more than one thing.
- Do not invent BIS standard numbers, fees, deadlines, or legal requirements.
- If current or specific BIS information is uncertain, clearly say that it should be verified from the official BIS source.
- Be practical and concise, but provide enough detail to actually help the user.

User's question:
{requirement_text}
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
            ),
        )

        return {
            "answer": response.text.strip(),
            "source": "ai-search",
        }

    except Exception as search_error:
        print(f"GEMINI SEARCH FAILED: {search_error}")
        print("Trying Gemini without Google Search...")

        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
            )

            return {
                "answer": response.text.strip(),
                "source": "ai",
            }

        except Exception as gemini_error:
            print(f"GEMINI CALL FAILED: {gemini_error}")
            return _fallback_explanation(requirement_text)

def _call_openai(requirement_text: str) -> dict:
    raise NotImplementedError("OpenAI integration not yet implemented.")


def _call_anthropic(requirement_text: str) -> dict:
    raise NotImplementedError("Anthropic integration not yet implemented.")