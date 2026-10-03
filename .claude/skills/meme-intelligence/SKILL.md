---
name: meme-intelligence
description: Meme and multimodal analysis specialist. Use for media typing (image/gif/video/gallery), transient preview fetching with SSRF guard, perceptual hashing, text-masked meme template clustering, originality labels (original/template_reuse/remix/repost), Tesseract OCR (eng+hin), Groq vision explanations, and meme concept generation.
when_to_use: Triggers on "meme", "template", "pHash", "repost detection", "OCR", "vision model", "image analysis", "humour", "meme concept".
paths: "backend/app/meme_analysis/**"
---

# Meme Intelligence

Source of truth: `docs/MEME_INTELLIGENCE.md`.

## Responsibilities
- Derive `content_type` and `media_assets` rows from `post_hint`, `is_gallery`, `is_video`, `domain`, `preview`, `media_metadata`.
- Fetch the smallest preview ≥ 320 px **into memory only**, compute a 64-bit pHash (`imagehash`), and discard the image.
- Template matching: mask OCR text boxes → pHash → Hamming distance (`bit_count(phash # q)` in Postgres). Repost ≤ 6, template ≤ 12.
- OCR only for trending meme posts. Vision explanation only for the top-N per day (`VISION_DAILY_LIMIT`, default 20) via `structured(task="vision", ...)` → `qwen/qwen3.8-27b` on Groq (≤ 3 images/request, 2,048 tokens per image).

## Execution
1. Pure functions first (`typing.py`, `phash.py`, `match.py`), tested with tiny **synthetic** images generated in tests (PIL shapes and text). Never test with real memes from Reddit.
2. Fetcher with an SSRF allow-list (`preview.redd.it`, `i.redd.it`, `external-preview.redd.it`, `v.redd.it`, `i.imgur.com`), 5 MB cap, 10 s timeout, no off-list redirects.
3. Vision output must match the schema in the doc. Label it as an *interpretation* in the API/UI.

## Constraints
- **Never store or rehost media binaries** (ADR-006). Only URLs + derived features.
- **Never present an existing meme as original.** With no match found, the label reads "no match found in collected data", never "verified original".
- Generated meme output is **text only** (template recommendation marked as an existing template, image description, captions). No image generation.
- No video downloading or frame extraction in MVP; use the thumbnail/preview frame only.
- Respect Groq vision quota. Skip, don't fail, when the daily vision cap is reached.

## Examples
- *"Same Drake template with different captions isn't clustering."* → check that OCR boxes are masked before hashing; add a synthetic test with the same base image and two captions, expecting Hamming ≤ 12.
- *"Suggest a meme for r/developersIndia about layoffs."* → pick an existing template from `meme_templates` with a matching tone, mark it "existing template: X", give 3–5 caption variants, check sub rules (meme flair/days), and list the sensitivity risk.
