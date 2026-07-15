"""
Text generation module for the AI Content Engine.
Handles campaign taglines, blog introductions, and social media posts
via the OpenRouter API.
"""

import json
import re
import time
from typing import Optional

import requests

from config import (
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    OPENROUTER_MODEL,
    OPENROUTER_FALLBACK_MODEL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_DELAY_SECONDS,
    REQUEST_TIMEOUT_SECONDS,
    TEMP_CREATIVE,
    TEMP_PRECISE,
)

# ─── Helpers ─────────────────────────────────────────────────────────────────


def _call_openrouter(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.7,
    max_retries: int = DEFAULT_MAX_RETRIES,
) -> Optional[str]:
    """
    Send a prompt to OpenRouter with retry logic.

    Args:
        system_prompt: System-level instruction.
        user_prompt: The user message.
        temperature: Model temperature (0.0-1.0).
        max_retries: Number of retry attempts on failure.

    Returns:
        Generated text content, or None if all retries fail.
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "max_tokens": 4096,
    }

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(
                f"{OPENROUTER_BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"].strip()
            return content
        except requests.exceptions.RequestException as e:
            if attempt == max_retries:
                return _call_with_fallback(system_prompt, user_prompt, temperature)
            time.sleep(DEFAULT_RETRY_DELAY_SECONDS * attempt)
    return None


def _call_with_fallback(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.7,
    max_retries: int = 2,
) -> Optional[str]:
    """
    Retry using the fallback model.
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": OPENROUTER_FALLBACK_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "max_tokens": 4096,
    }
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(
                f"{OPENROUTER_BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except requests.exceptions.RequestException:
            if attempt == max_retries:
                return None
            time.sleep(DEFAULT_RETRY_DELAY_SECONDS * attempt)
    return None

# ─── Public Generators ───────────────────────────────────────────────────────


def generate_tagline(
    product_name: str,
    target_audience: str,
    brand_tone: str,
) -> Optional[str]:
    """
    Generate a campaign tagline using few-shot prompting.
    Maximum 10 words, matching the selected brand tone.

    Args:
        product_name: Name of the product/service.
        target_audience: Intended audience description.
        brand_tone: Desired brand voice (e.g. professional, playful).

    Returns:
        Generated tagline string, or None on failure.
    """
    system_prompt = (
        "You are an expert advertising copywriter. "
        "You create memorable, punchy campaign taglines. "
        "You always respond with ONLY the tagline — no explanation, no quotes, no extra text."
    )

    # Few-shot examples calibrated by tone
    few_shot_examples = f"""
Examples of effective taglines:

Product: Nike running shoes, Audience: Athletes, Tone: Motivational
Tagline: Just Do It.

Product: Apple iPhone, Audience: Creative professionals, Tone: Innovative
Tagline: Think Different.

Product: Coca-Cola, Audience: Everyone, Tone: Friendly
Tagline: Open Happiness.

Product: Tesla, Audience: Eco-conscious drivers, Tone: Forward-thinking
Tagline: Accelerate the Future.

Product: Rolex, Audience: Luxury consumers, Tone: Premium
Tagline: A Crown for Every Achievement.

Product: Patagonia, Audience: Outdoor enthusiasts, Tone: Eco-friendly
Tagline: We're in Business to Save Our Home.
    """

    user_prompt = (
        f"{few_shot_examples}\n\n"
        f"Now create a tagline for:\n"
        f"Product: {product_name}\n"
        f"Target Audience: {target_audience}\n"
        f"Brand Tone: {brand_tone}\n\n"
        f"Constraints:\n"
        f"- Maximum 10 words\n"
        f"- Match the '{brand_tone}' tone precisely\n"
        f"- Be memorable and punchy\n"
        f"- Output ONLY the tagline text, no quotes, no explanation"
    )

    return _call_openrouter(system_prompt, user_prompt, temperature=TEMP_CREATIVE)


def generate_blog_introduction(
    product_name: str,
    target_audience: str,
    brand_tone: str,
    tagline: str,
) -> Optional[str]:
    """
    Generate a blog introduction using role-based prompting.
    Exactly 200 words, using the generated tagline as context.

    Args:
        product_name: Name of the product/service.
        target_audience: Intended audience.
        brand_tone: Desired brand voice.
        tagline: The previously generated campaign tagline.

    Returns:
        Blog intro text (~200 words), or None on failure.
    """
    system_prompt = (
        "You are a senior content strategist and blog writer at a top marketing agency. "
        "You specialize in crafting compelling blog introductions that hook readers immediately. "
        "You write with the brand's voice consistently throughout. "
        "You always write exactly 200 words — no more, no less. "
        "You count your words carefully before responding."
    )

    user_prompt = (
        f"Write a blog introduction (exactly 200 words) for the following:\n\n"
        f"Product/Service: {product_name}\n"
        f"Target Audience: {target_audience}\n"
        f"Brand Tone: {brand_tone}\n"
        f"Campaign Tagline: \"{tagline}\"\n\n"
        f"The introduction should:\n"
        f"- Use the tagline \"{tagline}\" as a central theme woven naturally into the narrative\n"
        f"- Address the {target_audience} audience directly and make them feel understood\n"
        f"- Maintain a {brand_tone} tone throughout\n"
        f"- Be exactly 200 words (count carefully)\n"
        f"- End with a compelling hook that makes readers want to continue reading\n"
        f"- Start with a strong opening sentence that grabs attention"
    )

    return _call_openrouter(system_prompt, user_prompt, temperature=TEMP_PRECISE)


def generate_social_posts(
    product_name: str,
    target_audience: str,
    brand_tone: str,
    tagline: str,
) -> Optional[dict]:
    """
    Generate social media posts for Twitter, Instagram, and LinkedIn.
    Returns ONLY a JSON object.

    Args:
        product_name: Name of the product/service.
        target_audience: Intended audience.
        brand_tone: Desired brand voice.
        tagline: The campaign tagline.

    Returns:
        Dict with keys 'twitter', 'instagram', 'linkedin', or None on failure.
    """
    system_prompt = (
        "You are a social media manager who creates platform-optimized content. "
        "You ALWAYS respond with valid JSON only — no markdown, no explanation, no code fences. "
        "Your response must be parseable by json.loads() directly. "
        "You carefully respect character limits for each platform."
    )

    user_prompt = (
        f"Generate social media posts for the following campaign:\n\n"
        f"Product/Service: {product_name}\n"
        f"Target Audience: {target_audience}\n"
        f"Brand Tone: {brand_tone}\n"
        f"Campaign Tagline: \"{tagline}\"\n\n"
        f"Return ONLY a JSON object with exactly three keys:\n"
        f"{{\n"
        f'  "twitter": "Post text for Twitter (max 280 characters, {brand_tone} tone, include the tagline, be concise and impactful)",\n'
        f'  "instagram": "Post text for Instagram (max 2200 characters, {brand_tone} tone, include the tagline, add 3-5 relevant hashtags, be engaging and visual)",\n'
        f'  "linkedin": "Post text for LinkedIn (max 700 characters, {brand_tone} but professional tone, include the tagline, end with a call-to-action, be thought-leadership style)"\n'
        f"}}\n\n"
        f"Constraints:\n"
        f"- Twitter: ≤ 280 characters (count carefully)\n"
        f"- Instagram: ≤ 2200 characters, include 3-5 relevant hashtags\n"
        f"- LinkedIn: ≤ 700 characters, professional tone with CTA\n"
        f"- Output ONLY valid JSON, no other text, no markdown formatting"
    )

    result = _call_openrouter(system_prompt, user_prompt, temperature=TEMP_CREATIVE)
    if result is None:
        return None

    # Attempt to parse JSON — handle markdown code fences just in case
    cleaned = result.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        cleaned = "\n".join(
            line for line in lines if not line.startswith("```")
        )

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        json_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                return None
        return None