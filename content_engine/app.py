"""
Main Streamlit application for the AI Content Engine.
Provides a two-column UI for generating marketing content:
taglines, blog intros, social posts, hero images, and promotional videos.
"""

import os
import sys
from typing import Optional

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import validate_config
from text_gen import generate_tagline, generate_blog_introduction, generate_social_posts
from image_gen import generate_hero_image
from video_gen import generate_promotional_video

# ─── Page Configuration ──────────────────────────────────────────────────────

st.set_page_config(
    page_title="AI Content Engine",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ──────────────────────────────────────────────────────────────

st.markdown(
    """
    <style>
    .main-header { font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem; color: #1E88E5; }
    .sub-header { font-size: 1rem; color: #666; margin-bottom: 2rem; }
    .success-box { padding: 1rem; border-radius: 0.5rem; background-color: #e8f5e9; border-left: 4px solid #4CAF50; margin-bottom: 1rem; }
    .info-box { padding: 0.75rem; border-radius: 0.5rem; background-color: #e3f2fd; border-left: 4px solid #1E88E5; margin-bottom: 1rem; }
    .warning-box { padding: 0.75rem; border-radius: 0.5rem; background-color: #fff3e0; border-left: 4px solid #FF9800; margin-bottom: 1rem; }
    .error-box { padding: 0.75rem; border-radius: 0.5rem; background-color: #ffebee; border-left: 4px solid #f44336; margin-bottom: 1rem; }
    .section-title { font-size: 1.3rem; font-weight: 600; margin-top: 1rem; margin-bottom: 0.5rem; color: #333; border-bottom: 2px solid #f0f0f0; padding-bottom: 0.3rem; }
    .technique-badge { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 1rem; font-size: 0.75rem; font-weight: 600; background-color: #e3f2fd; color: #1565C0; margin-left: 0.5rem; }
    .asset-card { background: #fafafa; border: 1px solid #e0e0e0; border-radius: 0.5rem; padding: 1rem; margin-bottom: 1rem; }
    .asset-card:hover { border-color: #1E88E5; box-shadow: 0 2px 8px rgba(30,136,229,0.1); }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─── Session State Initialisation ────────────────────────────────────────────

_DEFAULT_STATE = {
    "tagline": None,
    "blog_intro": None,
    "social_posts": None,
    "hero_image_url": None,
    "hero_image_prompt": None,
    "video_url": None,
    "video_placeholder": False,
    "generated": False,
    "generating": False,
}

for key, default in _DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─── Sidebar ─────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(
        '<div class="main-header" style="font-size: 1.8rem;">⚙️ Content Engine</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="sub-header">Configure your campaign</div>', unsafe_allow_html=True)
    st.markdown("---")

    product_name = st.text_input(
        "🏷️ Product Name",
        value=st.session_state.get("product_name", ""),
        placeholder="e.g. EcoCharge Pro",
    )
    st.session_state["product_name"] = product_name

    target_audience = st.text_input(
        "🎯 Target Audience",
        value=st.session_state.get("target_audience", ""),
        placeholder="e.g. Eco-conscious millennials",
    )
    st.session_state["target_audience"] = target_audience

    brand_tone = st.selectbox(
        "🎨 Brand Tone",
        options=[
            "Professional", "Playful", "Luxurious", "Bold",
            "Minimalist", "Friendly", "Innovative", "Authoritative",
        ],
        index=0,
    )
    st.session_state["brand_tone"] = brand_tone

    st.markdown("---")

    with st.expander("🎬 Image & Video Settings (Optional)"):
        image_style = st.text_input("Image Style", value="Modern, clean, photorealistic")
        composition = st.text_input("Composition", value="Centered product shot with ample negative space")
        constraints = st.text_input("Constraints", value="No text overlays, no watermarks, 16:9 aspect ratio")
        motion_prompt = st.text_input("Motion Prompt", value="Slow cinematic zoom with subtle pan")
        # Store in session state for pipeline access
        st.session_state["image_style"] = image_style
        st.session_state["composition"] = composition
        st.session_state["constraints"] = constraints
        st.session_state["motion_prompt"] = motion_prompt

    missing_keys = validate_config()
    if missing_keys:
        st.markdown(
            '<div class="warning-box">⚠️ Missing API keys: '
            + ", ".join(missing_keys)
            + "<br>Add them to the <code>.env</code> file.</div>",
            unsafe_allow_html=True,
        )

    generate_disabled = (
        not product_name
        or not target_audience
        or not brand_tone
        or bool(missing_keys)
        or st.session_state.get("generating", False)
    )

    if st.button("🚀 Generate", type="primary", use_container_width=True, disabled=generate_disabled):
        if product_name and target_audience and brand_tone:
            st.session_state["generating"] = True
            st.session_state["generated"] = False
            st.rerun()
        else:
            st.error("Please fill in all required fields.")

    if st.session_state["generated"]:
        if st.button("🔄 Reset", use_container_width=True, type="secondary"):
            for key in _DEFAULT_STATE:
                st.session_state[key] = _DEFAULT_STATE[key]
            st.session_state["generating"] = False
            st.rerun()

    st.markdown("---")
    st.markdown("<small style='color: #999;'>Built with Streamlit + OpenRouter + GPT Image + Runway</small>", unsafe_allow_html=True)

# ─── Main Pipeline Execution ─────────────────────────────────────────────────

def run_pipeline(
    product_name: str,
    target_audience: str,
    brand_tone: str,
    image_style: str = "Modern, clean, photorealistic",
    composition: str = "Centered product shot with ample negative space",
    constraints: str = "No text overlays, no watermarks, 16:9 aspect ratio",
    motion_prompt: str = "Slow cinematic zoom with subtle pan",
) -> None:
    """
    Execute the full content generation pipeline:
    Tagline → Blog, Tagline + Product → Image, Image → Video
    """
    # Step 1: Tagline
    with st.status("📝 Generating campaign tagline...", expanded=True) as status:
        st.write("Using few-shot prompting with brand tone context...")
        tagline = generate_tagline(
            product_name=product_name,
            target_audience=target_audience,
            brand_tone=brand_tone,
        )
        if tagline:
            st.session_state["tagline"] = tagline
            status.update(label=f'✅ Tagline generated: "{tagline}"', state="complete", expanded=False)
        else:
            status.update(label="❌ Tagline generation failed", state="error", expanded=True)
            st.error("Tagline generation failed. Check your API key and try again.")
            st.session_state["generating"] = False
            return

    # Step 2: Blog Introduction
    with st.status("📄 Writing blog introduction...", expanded=True) as status:
        st.write("Using role-based prompting with tagline as context...")
        blog_intro = generate_blog_introduction(
            product_name=product_name,
            target_audience=target_audience,
            brand_tone=brand_tone,
            tagline=tagline,
        )
        if blog_intro:
            st.session_state["blog_intro"] = blog_intro
            status.update(label="✅ Blog introduction written (200 words)", state="complete", expanded=False)
        else:
            status.update(label="❌ Blog introduction failed", state="error", expanded=True)
            st.error("Blog introduction generation failed.")
            st.session_state["generating"] = False
            return

    # Step 3: Social Media Posts
    with st.status("📱 Generating social media posts...", expanded=True) as status:
        st.write("Creating platform-optimized posts for Twitter, Instagram, and LinkedIn...")
        social_posts = generate_social_posts(
            product_name=product_name,
            target_audience=target_audience,
            brand_tone=brand_tone,
            tagline=tagline,
        )
        if social_posts and isinstance(social_posts, dict):
            st.session_state["social_posts"] = social_posts
            status.update(label="✅ Social media posts generated", state="complete", expanded=False)
        else:
            status.update(label="❌ Social media generation failed", state="error", expanded=True)
            st.error("Social media post generation failed.")
            st.session_state["generating"] = False
            return

    # Step 4: Hero Image
    with st.status("🎨 Generating hero image...", expanded=True) as status:
        st.write("Building prompt from product name, tagline, and brand tone...")
        try:
            image_result = generate_hero_image(
                product_name=product_name,
                tagline=tagline,
                brand_tone=brand_tone,
                style=image_style,
                composition=composition,
                constraints=constraints,
            )
            if image_result:
                if image_result.get("url"):
                    st.session_state["hero_image_url"] = image_result["url"]
                    st.session_state["hero_image_prompt"] = image_result.get("revised_prompt", "")
                    status.update(label="✅ Hero image generated", state="complete", expanded=False)
                elif image_result.get("prompt_only"):
                    st.session_state["hero_image_prompt"] = image_result.get("revised_prompt", "")
                    status.update(
                        label="✅ Image prompt generated (use with external image generator)",
                        state="complete",
                        expanded=False,
                    )
                else:
                    raise RuntimeError("No image result returned.")
            else:
                raise RuntimeError("No image result returned.")
        except Exception as e:
            status.update(label="❌ Hero image generation failed", state="error", expanded=True)
            st.error(f"Image generation failed: {e}")
            st.info("Continuing without hero image...")

    # Step 5: Promotional Video
    if st.session_state.get("hero_image_url"):
        with st.status("🎬 Generating promotional video...", expanded=True) as status:
            st.write("Using hero image as input for Runway image-to-video...")
            try:
                video_result = generate_promotional_video(
                    image_url=st.session_state["hero_image_url"],
                    motion_prompt=motion_prompt,
                    product_name=product_name,
                    tagline=tagline,
                    brand_tone=brand_tone,
                )
                if video_result and video_result.get("video_url"):
                    st.session_state["video_url"] = video_result["video_url"]
                    st.session_state["video_placeholder"] = False
                    status.update(label="✅ Promotional video generated (5-8 seconds)", state="complete", expanded=False)
                elif video_result and video_result.get("placeholder"):
                    st.session_state["video_url"] = ""
                    st.session_state["video_placeholder"] = True
                    status.update(
                        label="⏳ Video generation requires Runway API key (see .env)",
                        state="complete",
                        expanded=False,
                    )
                else:
                    raise RuntimeError("No video URL returned.")
            except Exception as e:
                status.update(label="❌ Video generation failed", state="error", expanded=True)
                st.error(f"Video generation failed: {e}")
                st.info("Continuing without promotional video...")
    else:
        st.info("Skipping video generation (no hero image available).")

    st.session_state["generated"] = True
    st.session_state["generating"] = False
    st.success("✅ All content generated successfully!")
    st.rerun()

# ─── Main Content Area ───────────────────────────────────────────────────────

st.markdown('<div class="main-header">🚀 AI Content Engine</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Generate complete marketing assets — taglines, blog intros, '
    "social posts, hero images, and promotional videos — in one click.</div>",
    unsafe_allow_html=True,
)

# Run pipeline if generating
if st.session_state.get("generating", False):
    run_pipeline(
        product_name=st.session_state["product_name"],
        target_audience=st.session_state["target_audience"],
        brand_tone=st.session_state["brand_tone"],
        image_style=st.session_state.get("image_style", "Modern, clean, photorealistic"),
        composition=st.session_state.get("composition", "Centered product shot with ample negative space"),
        constraints=st.session_state.get("constraints", "No text overlays, no watermarks, 16:9 aspect ratio"),
        motion_prompt=st.session_state.get("motion_prompt", "Slow cinematic zoom with subtle pan"),
    )

# Display results if generated
if st.session_state["generated"]:

    left_col, right_col = st.columns(2, gap="large")

    # ─── LEFT COLUMN: Text Content ────────────────────────────────────────
    with left_col:
        st.markdown('<div class="section-title">📝 Text Content</div>', unsafe_allow_html=True)

        if st.session_state["tagline"]:
            with st.container():
                st.markdown(
                    '<div class="asset-card">'
                    '<strong>🏷️ Campaign Tagline</strong> '
                    '<span class="technique-badge">Few-shot Prompting</span>'
                    '</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div class="success-box">"{st.session_state["tagline"]}"</div>',
                    unsafe_allow_html=True,
                )

        if st.session_state["blog_intro"]:
            with st.container():
                st.markdown(
                    '<div class="asset-card">'
                    '<strong>📄 Blog Introduction</strong> '
                    '<span class="technique-badge">Role-based Prompting</span>'
                    '</div>',
                    unsafe_allow_html=True,
                )
                word_count = len(st.session_state["blog_intro"].split())
                with st.expander(f"📖 Read ({word_count} words)"):
                    st.write(st.session_state["blog_intro"])

        if st.session_state["social_posts"]:
            with st.container():
                st.markdown(
                    '<div class="asset-card">'
                    '<strong>📱 Social Media Posts</strong> '
                    '<span class="technique-badge">Structured Output</span>'
                    '</div>',
                    unsafe_allow_html=True,
                )
                posts = st.session_state["social_posts"]

                twitter_text = posts.get("twitter", "")
                if twitter_text:
                    char_count = len(twitter_text)
                    with st.expander(f"🐦 Twitter ({char_count}/280 characters)"):
                        st.info(twitter_text)
                        if char_count <= 280:
                            st.success(f"✅ {char_count} characters")
                        else:
                            st.error(f"❌ {char_count} chars exceeds 280")

                instagram_text = posts.get("instagram", "")
                if instagram_text:
                    char_count = len(instagram_text)
                    with st.expander(f"📸 Instagram ({char_count}/2200 characters)"):
                        st.info(instagram_text)
                        if char_count <= 2200:
                            st.success(f"✅ {char_count} characters")
                        else:
                            st.error(f"❌ {char_count} chars exceeds 2200")

                linkedin_text = posts.get("linkedin", "")
                if linkedin_text:
                    char_count = len(linkedin_text)
                    with st.expander(f"💼 LinkedIn ({char_count}/700 characters)"):
                        st.info(linkedin_text)
                        if char_count <= 700:
                            st.success(f"✅ {char_count} characters")
                        else:
                            st.error(f"❌ {char_count} chars exceeds 700")

    # ─── RIGHT COLUMN: Visual Content ──────────────────────────────────────
    with right_col:
        st.markdown('<div class="section-title">🎨 Visual Content</div>', unsafe_allow_html=True)

        if st.session_state["hero_image_url"]:
            with st.container():
                st.markdown(
                    '<div class="asset-card">'
                    '<strong>🖼️ Hero Image</strong> '
                    '<span class="technique-badge">Image Prompt Formula</span>'
                    '</div>',
                    unsafe_allow_html=True,
                )
                st.image(
                    st.session_state["hero_image_url"],
                    caption="Generated Hero Image (16:9)",
                    width="stretch",
                )
                if st.session_state.get("hero_image_prompt"):
                    with st.expander("📝 Image Prompt Used"):
                        st.info(st.session_state["hero_image_prompt"])

        if st.session_state["video_url"]:
            with st.container():
                st.markdown(
                    '<div class="asset-card">'
                    '<strong>🎬 Promotional Video (5-8 seconds)</strong> '
                    '<span class="technique-badge">Motion Prompt</span>'
                    '</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<video width="100%" controls><source src="{st.session_state["video_url"]}" type="video/mp4">Your browser does not support the video tag.</video>',
                    unsafe_allow_html=True,
                )

        if st.session_state.get("video_placeholder"):
            with st.container():
                st.markdown(
                    '<div class="asset-card">'
                    '<strong>🎬 Promotional Video (5-8 seconds)</strong> '
                    '<span class="technique-badge">Motion Prompt</span>'
                    '</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    '<div class="warning-box">⚠️ Runway API key required for video generation. '
                    'Add a valid Runway API key in <code>.env</code> (get one from https://runwayml.com).</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div class="info-box">🎥 <strong>Motion prompt:</strong> "Slow cinematic push-in. Soft light shifts gently. Background mostly still."</div>',
                    unsafe_allow_html=True,
                )

        if st.session_state.get("hero_image_prompt") and not st.session_state["hero_image_url"]:
            with st.container():
                st.markdown(
                    '<div class="asset-card">'
                    '<strong>🖼️ Hero Image Prompt</strong> '
                    '<span class="technique-badge">Image Prompt Formula</span>'
                    '</div>',
                    unsafe_allow_html=True,
                )
                with st.expander("📝 Refined Image Prompt (use with DALL-E / Midjourney)"):
                    st.info(st.session_state["hero_image_prompt"])

        if not st.session_state["hero_image_url"] and not st.session_state["video_url"]:
            st.markdown(
                '<div class="info-box">ℹ️ Visual content will appear here after generation. '
                "Ensure your GPT Image and Runway API keys are configured.</div>",
                unsafe_allow_html=True,
            )

elif not st.session_state["generating"]:
    st.markdown(
        '<div class="info-box">'
        "ℹ️ Enter your campaign details in the sidebar and click **Generate** to start.<br><br>"
        "The pipeline will:<br>"
        "1️⃣ Generate a campaign tagline (few-shot prompting, ≤10 words)<br>"
        "2️⃣ Write a blog introduction (role-based, ~200 words)<br>"
        "3️⃣ Create social media posts (Twitter, Instagram, LinkedIn)<br>"
        "4️⃣ Generate a hero image (GPT Image API)<br>"
        "5️⃣ Create a promotional video (Runway image-to-video)<br>"
        "</div>",
        unsafe_allow_html=True,
    )

    with st.expander("📋 Example Workflow Preview"):
        st.markdown(
            """**Inputs:**
- **Product:** EcoCharge Pro
- **Audience:** Eco-conscious millennials
- **Tone:** Bold

**Outputs:**
1. **Tagline:** *"Power Your Tomorrow, Sustainably."*
2. **Blog:** 200-word intro weaving the tagline into a compelling narrative.
3. **Social:** Platform-optimized posts with character-limit validation.
4. **Image:** Photorealistic hero banner of the product in a natural setting.
5. **Video:** 7-second cinematic clip with a slow zoom effect."""
        )