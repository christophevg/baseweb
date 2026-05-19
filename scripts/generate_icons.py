#!/usr/bin/env python3
"""
Generate placeholder PWA icons for baseweb.

This script creates simple placeholder icons in all required sizes
for PWA manifest compatibility. Icons are simple colored squares with
a "B" letter for baseweb branding.

Usage:
    uv run python scripts/generate_icons.py

Requirements:
    - Pillow (PIL) library
"""

import os
from pathlib import Path

try:
  from PIL import Image, ImageDraw, ImageFont
except ImportError:
  print("Pillow is required. Install with: uv pip install Pillow")
  raise

# Icon sizes required by PWA manifest
ICON_SIZES = [72, 96, 128, 144, 152, 180, 192, 384, 512]

# Colors
BACKGROUND_COLOR = "#1976D2"  # Material Blue
TEXT_COLOR = "#FFFFFF"  # White


def create_placeholder_icon(size: int, output_path: Path) -> None:
  """Create a placeholder icon with the given size.

  Args:
    size: Width and height of the icon in pixels
    output_path: Path to save the icon
  """
  # Create image with background color
  img = Image.new("RGB", (size, size), color=BACKGROUND_COLOR)
  draw = ImageDraw.Draw(img)

  # Calculate font size based on icon size
  # Use a font size that's roughly 60% of the icon size
  font_size = int(size * 0.6)

  # Try to use a system font, fall back to default
  try:
    # Try common system fonts
    font_paths = [
      "/System/Library/Fonts/Helvetica.ttc",  # macOS
      "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
      "C:\\Windows\\Fonts\\arial.ttf",  # Windows
    ]
    font = None
    for font_path in font_paths:
      if os.path.exists(font_path):
        font = ImageFont.truetype(font_path, font_size)
        break
    if font is None:
      # Fall back to default font
      font = ImageFont.load_default()
  except Exception:
    font = ImageFont.load_default()

  # Draw "B" letter in center
  text = "B"

  # Calculate text position to center it
  # Use textbbox to get actual text dimensions
  bbox = draw.textbbox((0, 0), text, font=font)
  text_width = bbox[2] - bbox[0]
  text_height = bbox[3] - bbox[1]

  x = (size - text_width) // 2
  y = (size - text_height) // 2

  draw.text((x, y), text, fill=TEXT_COLOR, font=font)

  # Save the image
  img.save(output_path, "PNG")
  print(f"Created: {output_path}")


def main() -> None:
  """Generate all placeholder icons."""
  # Get the baseweb static directory
  script_dir = Path(__file__).parent
  project_root = script_dir.parent
  icons_dir = project_root / "src" / "baseweb" / "static" / "images" / "icons"

  # Create icons directory if it doesn't exist
  icons_dir.mkdir(parents=True, exist_ok=True)

  print(f"Generating placeholder icons in: {icons_dir}")
  print(f"Sizes: {ICON_SIZES}")
  print()

  # Generate each icon
  for size in ICON_SIZES:
    output_path = icons_dir / f"icon-{size}x{size}.png"
    create_placeholder_icon(size, output_path)

  print()
  print(f"Generated {len(ICON_SIZES)} icons successfully!")


if __name__ == "__main__":
  main()