"""
Video generation module for the AI Content Engine.
Generates promotional videos from hero images using the Runway API.
"""

import time
from typing import Optional

import requests

from config import (
    RUNWAY_API_KEY,
    RUNWAY_BASE_URL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_DELAY_SECONDS,
    REQUEST_TIMEOUT_SECONDS,
)


def generate_promotional_video(
    image_url: str,
    motion_prompt: str = "Slow cinematic push-in. Soft light shifts gently. Background mostly still.",
    product_name: str = "",
    tagline: str = "",
    brand_tone: str = "",
    max_retries: int = DEFAULT_MAX_RETRIES,
) -> Optional[dict]:
    """
    Generate a 5-8 second promotional video from a hero image
    using the Runway Gen-3 / image-to-video API.

    If Runway API key is not configured, returns a placeholder video URL.

    Args:
        image_url: URL of the source hero image.
        motion_prompt: Description of the desired motion/camera movement.
        product_name: Product name (for logging/context).
        tagline: Campaign tagline (for logging/context).
        brand_tone: Brand tone (for logging/context).
        max_retries: Number of retry attempts.

    Returns:
        Dict with video URL and metadata, or None on failure.
    """
    # If no Runway API key or key is an OpenRouter key (sk-or-), return a placeholder
    if not RUNWAY_API_KEY or RUNWAY_API_KEY.startswith("sk-or-"):
        return {
            "video_url": "",
            "task_id": "",
            "motion_prompt": motion_prompt,
            "product_name": product_name,
            "tagline": tagline,
            "placeholder": True,
        }

    headers = {
        "Authorization": f"Bearer {RUNWAY_API_KEY}",
        "Content-Type": "application/json",
    }

    # Step 1: Create an image-to-video task
    payload = {
        "image_url": image_url,
        "prompt": motion_prompt,
        "duration": 7,  # Target 5-8 seconds
        "model": "gen3a_turbo",
    }

    for attempt in range(1, max_retries + 1):
        try:
            # Initiate generation
            response = requests.post(
                f"{RUNWAY_BASE_URL}/image_to_video",
                headers=headers,
                json=payload,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            task_data = response.json()
            task_id = task_data.get("id")

            if not task_id:
                raise RuntimeError("No task ID returned from Runway API.")

            # Step 2: Poll for completion
            video_url = _poll_runway_task(task_id, headers)
            if video_url:
                return {
                    "video_url": video_url,
                    "task_id": task_id,
                    "motion_prompt": motion_prompt,
                    "product_name": product_name,
                    "tagline": tagline,
                    "placeholder": False,
                }

        except requests.exceptions.RequestException as e:
            if attempt == max_retries:
                raise RuntimeError(
                    f"Video generation failed after {max_retries} attempts: {e}"
                )
            time.sleep(DEFAULT_RETRY_DELAY_SECONDS * attempt)

    return None


def _poll_runway_task(
    task_id: str,
    headers: dict,
    poll_interval: int = 5,
    max_polls: int = 60,
) -> Optional[str]:
    """
    Poll Runway task status until complete or failed.

    Args:
        task_id: The task ID from Runway.
        headers: Request headers with auth.
        poll_interval: Seconds between polls.
        max_polls: Maximum number of polling attempts.

    Returns:
        Video URL string, or None if failed.
    """
    for _ in range(max_polls):
        try:
            response = requests.get(
                f"{RUNWAY_BASE_URL}/tasks/{task_id}",
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()
            status_data = response.json()
            status = status_data.get("status", "").lower()

            if status == "completed":
                output = status_data.get("output", {})
                return output.get("video_url", output.get("url", ""))

            if status in ("failed", "error"):
                error_msg = status_data.get("error", "Unknown error")
                raise RuntimeError(f"Runway task failed: {error_msg}")

            # Still processing — wait and retry
            time.sleep(poll_interval)

        except requests.exceptions.RequestException:
            time.sleep(poll_interval)

    raise RuntimeError("Runway task polling timed out.")