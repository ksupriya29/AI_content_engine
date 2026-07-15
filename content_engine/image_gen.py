"""
Image generation module for the AI Content Engine.
Generates hero images using OpenRouter's image generation capabilities.
"""

import time
import hashlib
from typing import Optional

import requests

from config import (
    OPENROUTER_BASE_URL,
    OPENROUTER_API_KEY,
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_DELAY_SECONDS,
    REQUEST_TIMEOUT_SECONDS,
)


def build_image_prompt(
    product_name: str,
    tagline: str,
    brand_tone: str,
    style: str = "Modern, clean, photorealistic",
    composition: str = "Centered product shot with ample negative space",
    constraints: str = "No text overlays, no watermarks, 16:9 aspect ratio",
) -> str:
    """
    Build a detailed image generation prompt using the image prompt formula:
    subject + style (from tone) + composition + constraints.

    Args:
        product_name: Name of the product/service.
        tagline: Campaign tagline.
        brand_tone: Desired brand tone.
        style: Visual style description.
        composition: Composition/layout description.
        constraints: Visual constraints to avoid.

    Returns:
        A detailed prompt string for the image model.
    """
    tone_style_map = {
        "playful": "bright flat illustration with vibrant colors, whimsical feel",
        "premium": "photorealistic, studio lighting, luxury finish",
        "luxurious": "photorealistic, studio lighting, luxury finish, rich textures",
        "eco": "watercolour, natural tones, organic textures",
        "friendly": "warm, inviting, soft lighting, approachable",
        "bold": "dramatic, high contrast, striking, dynamic composition",
        "innovative": "futuristic, sleek, modern, tech-forward aesthetic",
        "minimalist": "clean, simple, ample whitespace, minimalist design",
        "professional": "clean corporate style, sharp, well-lit, authoritative",
        "authoritative": "strong, confident, professional, imposing yet elegant",
    }

    tone_lower = brand_tone.lower().strip()
    visual_style = tone_style_map.get(tone_lower, "clean modern, professional")

    prompt = (
        f"A professional hero banner image for {product_name}. "
        f"Visual style: {visual_style}. "
        f"Composition: {composition}. "
        f"Constraints: {constraints}. "
        f"The campaign tagline is '{tagline}'. "
        f"16:9 aspect ratio, ultra high quality, suitable for a website hero section."
    )
    return prompt


def _generate_placeholder_image_url(product_name: str, brand_tone: str) -> str:
    """Generate a placeholder image URL with product name and tone."""
    # Use a deterministic color based on the product name
    hash_val = int(hashlib.md5(product_name.encode()).hexdigest()[:8], 16)
    colors = [
        "1a73e8", "0d47a1", "00695c", "e65100", "4a148c",
        "c62828", "2e7d32", "f57f17", "37474f", "01579b"
    ]
    color = colors[hash_val % len(colors)]
    # Use placehold.co for a clean placeholder
    return f"https://placehold.co/1792x1024/{color}/white?text={product_name.replace(' ', '+')}"


def generate_hero_image(
    product_name: str,
    tagline: str,
    brand_tone: str,
    style: str = "Modern, clean, photorealistic",
    composition: str = "Centered product shot with ample negative space",
    constraints: str = "No text overlays, no watermarks, 16:9 aspect ratio",
    max_retries: int = DEFAULT_MAX_RETRIES,
) -> Optional[dict]:
    """
    Generate a hero image prompt using OpenRouter.
    Returns a refined prompt and a placeholder image URL.

    Args:
        product_name: Name of the product/service.
        tagline: Campaign tagline.
        brand_tone: Desired brand tone.
        style: Visual style description.
        composition: Composition/layout description.
        constraints: Visual constraints.
        max_retries: Number of retry attempts.

    Returns:
        Dict with 'url' (placeholder) and 'revised_prompt' (refined prompt).
    """
    image_prompt = build_image_prompt(
        product_name=product_name,
        tagline=tagline,
        brand_tone=brand_tone,
        style=style,
        composition=composition,
        constraints=constraints,
    )

    # Generate a placeholder image URL
    placeholder_url = _generate_placeholder_image_url(product_name, brand_tone)

    # Use OpenRouter to refine the prompt
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    refine_payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "You are an expert image prompt engineer. Refine the given prompt into a detailed, vivid image description suitable for any image generation model (like Midjourney, DALL-E, Stable Diffusion). Make it specific, visual, and rich in detail. Return ONLY the refined prompt text, no explanation."
            },
            {
                "role": "user",
                "content": f"Refine this image prompt into a detailed, professional description ideal for generating a hero banner image:\n\n{image_prompt}"
            },
        ],
        "temperature": 0.7,
        "max_tokens": 500,
    }

    refined_prompt = image_prompt  # default fallback

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(
                f"{OPENROUTER_BASE_URL}/chat/completions",
                headers=headers,
                json=refine_payload,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            data = response.json()
            refined_prompt = data["choices"][0]["message"]["content"].strip()
            break
        except requests.exceptions.RequestException:
            if attempt == max_retries:
                pass
            time.sleep(DEFAULT_RETRY_DELAY_SECONDS * attempt)

    return {
        "url": placeholder_url,
        "revised_prompt": refined_prompt,
        "prompt_only": False,  # We have a placeholder URL
    }