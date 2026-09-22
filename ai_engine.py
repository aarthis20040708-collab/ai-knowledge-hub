import os
from dotenv import load_dotenv
from groq import Groq, APIError

# Load environment variables
load_dotenv()

import streamlit as st

def get_groq_client():
    """Initializes and returns a Groq client instance with environment or Streamlit secrets."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        try:
            if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
                api_key = st.secrets["GROQ_API_KEY"]
        except Exception:
            pass

    if not api_key:
        raise ValueError("GROQ_API_KEY not found. Please set it in your .env file or Streamlit Secrets.")
    return Groq(api_key=api_key)


def get_available_models():
    """
    Fetches available models from Groq or provides recommended options.
    Filters out models that require specialized tool payloads.
    """
    default_models = [
        "openai/gpt-oss-20b",
        "openai/gpt-oss-120b",
        "qwen/qwen3.8-27b",
        "allam-2-7b"
    ]
    try:
        client = get_groq_client()
        raw_models = [m.id for m in client.models.list().data]
        # Filter for text chat models, excluding whisper, guard, and compound routers
        valid = [
            m for m in raw_models 
            if not m.startswith("whisper") 
            and "guard" not in m 
            and "compound" not in m
            and "orpheus" not in m
        ]
        return valid if valid else default_models
    except Exception:
        return default_models


def stream_chat_response(
    messages: list, 
    model: str, 
    system_prompt: str = None, 
    document_context: str = None,
    search_context: str = None
):
    """
    Streams the AI response chunk by chunk with multi-dimensional temporal reasoning,
    live web grounding, and societal impact synthesis.
    Includes automated fallback for seamless execution.
    """
    client = get_groq_client()

    # Core System Capabilities
    core_instructions = (
        "You are an advanced AI Intelligence & Societal Impact Assistant. "
        "You provide holistic, comprehensive, and high-impact insights.\n\n"
        "Key Operating Principles:\n"
        "1. **Temporal Depth (Past, Present & Future)**: When analyzing questions or trends, bridge historical roots (Past), current state-of-the-art developments (Present), and strategic future forecasts or projections (Future).\n"
        "2. **Societal Impact & Responsibility**: Highlight practical, ethical, and positive impacts on society, education, economy, technology, and sustainability.\n"
        "3. **No Code Dumps for Document Exports**: If the user asks to 'generate into pdf', 'export report', or 'create a document', do NOT output Python or shell code. Instead, generate a well-structured, formatted executive report with clear sections, bullet points, and actionable takeaways. The system will automatically convert it to a PDF file.\n"
        "4. **Direct Markdown Output**: Do not output function calls, tool tags, or <tool_call> tokens. Output all responses directly as clean, human-readable markdown.\n"
        "5. **Truthfulness & Precision**: Use live web grounding facts and uploaded document context whenever provided."
    )

    base_persona = system_prompt or "You are a versatile, knowledgeable, and proactive AI consultant."
    system_sections = [core_instructions, f"**Active Persona Role:** {base_persona}"]

    # Attach Live Web Search Grounding if available
    if search_context:
        system_sections.append(f"{search_context}")

    # Attach Uploaded Document Context if available
    if document_context:
        system_sections.append(f"**UPLOADED REFERENCE DOCUMENTS:**\n{document_context}")

    full_system_prompt = "\n\n---\n\n".join(system_sections)

    payload = [{"role": "system", "content": full_system_prompt}]
    payload.extend(messages)

    # Attempt Streaming with specified model, with fallback to primary stable model
    models_to_try = [model]
    if model != "openai/gpt-oss-20b":
        models_to_try.append("openai/gpt-oss-20b")
    if "qwen/qwen3.8-27b" not in models_to_try:
        models_to_try.append("qwen/qwen3.8-27b")

    stream_success = False
    last_err = None

    for candidate_model in models_to_try:
        try:
            stream = client.chat.completions.create(
                messages=payload,
                model=candidate_model,
                stream=True,
            )
            for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, 'content') and delta.content:
                        yield delta.content
            stream_success = True
            break
        except (APIError, Exception) as e:
            last_err = e
            continue

    if not stream_success:
        # If all streaming attempts encounter API issues, provide direct completion fallback
        try:
            resp = client.chat.completions.create(
                messages=payload,
                model="openai/gpt-oss-20b",
                stream=False
            )
            yield resp.choices[0].message.content
        except Exception as final_e:
            yield f"⚠️ Notice: The model encountered a temporary API response issue ({str(last_err or final_e)}). Please try submitting your question again."
