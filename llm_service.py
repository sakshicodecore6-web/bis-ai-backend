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
- Do NOT use markdown formatting such as asterisks for bold text or pound signs for headings. This response will be displayed as plain text, not rendered markdown.
- When the answer naturally involves multiple items, categories, or steps, structure it as a list using a plain dash ("-") at the start of each point, with one blank line between points. Each point can be a full sentence or a short group of related sentences — do not break a single idea across multiple bullets, and do not create a new bullet for every line.
- Only use a list when there are genuinely multiple distinct items to enumerate (like required documents or steps). For a simple direct answer with no natural list structure, just write normal short paragraphs instead.
- When listing required documents, standards, or steps, only name specific document types (such as circuit diagrams, PCB layouts, trademark certificates, or specific portal URLs) if you are highly confident they are a standard, verifiable BIS requirement. Do not invent plausible-sounding technical sub-documents to make the list feel more complete.
- If you are unsure of an exact document name, portal URL, or sub-requirement, describe the general category instead (for example, "technical specifications of the product" rather than inventing a specific document title), and tell the user to confirm the exact requirement on the official BIS website (bis.gov.in) or the relevant scheme's portal.
- Prefer directing users to the general official BIS website (bis.gov.in) unless you are confident about a specific sub-portal's exact current URL and purpose.
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
- Keep responses tight: for list-style answers, each point should be one short sentence stating the document/step/fact itself, without extra explanatory clauses unless the explanation is essential to understanding it. Avoid restating the question's context in every point.
- For the overall response, aim for the shortest version that fully answers the question — skip introductory framing sentences where possible and get straight to the substantive content.
- If closing with a verification note (e.g., "check the official BIS website"), keep it to one short sentence, not a full explanatory paragraph.

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