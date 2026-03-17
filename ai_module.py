"""
ai_module.py - Hugging Face API integration for AI resume feedback
Uses google/flan-t5-base via Hugging Face Inference API
"""

import os
import requests
from utils import truncate_text

HF_API_URL = "https://router.huggingface.co/hf-inference/models/mistralai/Mistral-7B-Instruct-v0.2"
MAX_RESUME_CHARS = 1200
REQUEST_TIMEOUT = 30


def _get_api_key() -> str:
    """Retrieve the Hugging Face API key from environment variables."""
    key = os.environ.get("HF_API_KEY", "").strip()
    return key


def _call_hf_api(prompt: str) -> str:
    """
    Make a single call to the Hugging Face Inference API.
    Returns the generated text or raises an exception with a user-friendly message.
    """
    api_key = _get_api_key()
    if not api_key:
        raise ValueError("HF_API_KEY environment variable is not set.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 200,
            "temperature": 0.7,
            "do_sample": True
        }
    }

    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=REQUEST_TIMEOUT)
    except requests.exceptions.Timeout:
        raise ConnectionError("Request timed out. The AI model may be loading. Please try again.")
    except requests.exceptions.ConnectionError:
        raise ConnectionError("Could not connect to the AI service. Check your internet connection.")

    if response.status_code == 401:
        raise PermissionError("Invalid API key (401). Please check your HF_API_KEY secret.")
    elif response.status_code == 403:
        raise PermissionError("Access forbidden (403). Your API key may not have the required permissions.")
    elif response.status_code == 404:
        raise ValueError("Model not found (404). The AI endpoint may have changed.")
    elif response.status_code == 503:
        raise ConnectionError("AI model is loading (503). Please wait a moment and try again.")
    elif response.status_code == 429:
        raise ConnectionError("Rate limit reached (429). Please wait before trying again.")
    elif response.status_code != 200:
        raise RuntimeError(f"API error ({response.status_code}): {response.text[:200]}")

    try:
        result = response.json()
        if isinstance(result, list) and len(result) > 0:
            return result[0].get("generated_text", "").strip()
        elif isinstance(result, dict):
            return result.get("generated_text", "").strip()
        return str(result)
    except Exception:
        return response.text.strip()


def get_ai_feedback(resume_text: str, job_desc: str = "") -> dict:
    """
    Generate structured AI feedback for the resume.
    Returns dict with keys: strengths, weaknesses, improvements, rewrite_tips, error
    """
    if not resume_text:
        return {"error": "No resume text provided for AI analysis."}

    short_resume = truncate_text(resume_text, MAX_RESUME_CHARS)

    feedback = {
        "strengths": "",
        "weaknesses": "",
        "improvements": "",
        "rewrite_tips": "",
        "job_alignment": "",
        "error": None
    }

    try:
        # Prompt 1: Strengths
        prompt_strengths = (
            f"Analyze this resume and list 3 key strengths in bullet points:\n\n{short_resume}\n\nStrengths:"
        )
        feedback["strengths"] = _call_hf_api(prompt_strengths)

        # Prompt 2: Weaknesses
        prompt_weaknesses = (
            f"Analyze this resume and list 3 weaknesses or gaps in bullet points:\n\n{short_resume}\n\nWeaknesses:"
        )
        feedback["weaknesses"] = _call_hf_api(prompt_weaknesses)

        # Prompt 3: Improvements
        prompt_improve = (
            f"Suggest 3 specific improvements for this resume in bullet points:\n\n{short_resume}\n\nImprovements:"
        )
        feedback["improvements"] = _call_hf_api(prompt_improve)

        # Prompt 4: Rewrite tips
        prompt_rewrite = (
            f"Give 3 resume writing tips to make this resume more impactful:\n\n{short_resume}\n\nTips:"
        )
        feedback["rewrite_tips"] = _call_hf_api(prompt_rewrite)

        # Prompt 5: Job alignment (if JD provided)
        if job_desc:
            short_jd = truncate_text(job_desc, 400)
            prompt_alignment = (
                f"How well does this resume match this job description? Give advice in 2-3 sentences.\n\n"
                f"Resume: {short_resume[:600]}\n\nJob Description: {short_jd}\n\nAlignment:"
            )
            feedback["job_alignment"] = _call_hf_api(prompt_alignment)

    except (ValueError, PermissionError, ConnectionError, RuntimeError) as e:
        feedback["error"] = str(e)

    return feedback


def generate_improve_section(resume_text: str) -> str:
    """
    Generate an 'improved' version suggestion for the resume summary/intro.
    """
    if not resume_text:
        return ""
    short = truncate_text(resume_text, 600)
    prompt = (
        f"Rewrite the professional summary of this resume to be more impactful and ATS-friendly:\n\n"
        f"{short}\n\nImproved Summary:"
    )
    try:
        return _call_hf_api(prompt)
    except Exception as e:
        return f"Could not generate improvement: {str(e)}"
