#!/usr/bin/env python3
"""One-shot diagnostic: list image-capable models available on this GEMINI_API_KEY.
Use to find the correct model name when generate-hero-image-gemini.py fails with 404."""
import os, sys
from google import genai

if not os.environ.get("GEMINI_API_KEY"):
    print("GEMINI_API_KEY not set", file=sys.stderr)
    sys.exit(1)

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
print("All available models:\n")
for m in client.models.list():
    methods = getattr(m, "supported_actions", None) or getattr(m, "supported_generation_methods", None) or []
    name = m.name
    if "imagen" in name.lower() or "image" in name.lower() or "generate_images" in str(methods).lower() or "predict" in str(methods).lower():
        print(f"  {name}")
        print(f"    display_name: {getattr(m, 'display_name', None)}")
        print(f"    methods: {methods}")
        print()
