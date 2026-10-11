#!/usr/bin/env python3
"""
Generate animated GIFs for each TruthOps claim card.
Uses real data from the JSON reports. Matches the site's dark theme.
"""

import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).parent.parent
SITE_DIR = BASE / "site"
GIF_DIR = SITE_DIR / "gifs"

# Colors (matching the site's dark theme)
BG = (15, 23, 42)          # #0f172a
CARD_BG = (30, 41, 59)     # #1e293b
TEXT = (226, 232, 240)     # #e2e8f0
MUTED = (100, 116, 139)    # #64748b
GREEN = (34, 197, 94)
ORANGE = (249, 115, 22)
RED = (239, 68, 68)
YELLOW = (234, 179, 8)
BLUE = (96, 165, 250)

VERDICT_COLORS = {
    "pants_on_fire": RED,
    "false": RED,
    "mostly_false": ORANGE,
    "half_true": YELLOW,
    "mostly_true": GREEN,
    "true": GREEN,
}

# Try to load a decent font, fall back to default
def get_font(size):
    for path in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]:
        try:
            return ImageFont.truetype(path, size)
        except:
            continue
    return ImageFont.load_default()

def wrap_text(text, font, max_width, draw):
    """Wrap text to fit max_width."""
    words = text.split()
    lines = []
    current = []
    for word in words:
        test = " ".join(current + [word])
        if draw.textlength(test, font=font) <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines

def generate_gif(claim_data, output_path):
    """Generate an animated GIF for a single claim."""
    n = claim_data["n"]
    statement = claim_data["statement"]
    verdict = claim_data["verdict"]
    score = claim_data["score"]
    confidence = claim_data["confidence"]
    evidence_count = claim_data["evidence_count"]
    trace_id = claim_data["trace_id"]

    W, H = 600, 700
    verdict_color = VERDICT_COLORS.get(verdict, MUTED)
    verdict_text = verdict.upper().replace("_", " ")

    font_title = get_font(22)
    font_verdict = get_font(26)
    font_body = get_font(18)
    font_small = get_font(15)
    font_label = get_font(13)

    frames = []

    # Animation: 4 phases
    # Phase 1: Card appears with claim text (frames 0-9)
    # Phase 2: Verdict badge pops in (frames 10-19)
    # Phase 3: Score bar animates (frames 20-39)
    # Phase 4: Pipeline steps appear one by one (frames 40-69)
    # Phase 5: Hold (frames 70-79)

    steps = [
        ("Sniff Test", "Cloudflare Clef-flash gate", GREEN),
        ("Evidence", f"{evidence_count} sources gathered and scored", GREEN),
        ("Photo Forensics", "C2PA + Sightengine AI detection", GREEN),
        ("Contrarian Review", "Adversarial challenge", GREEN),
        ("Director Verdict", f"{verdict_text} at {score}/100", GREEN),
        ("Human Gate", "BLOCKED — needs approval", ORANGE),
    ]

    total_frames = 80

    for frame_idx in range(total_frames):
        # No card border — fill entire frame with card bg so it blends into the site card
        img = Image.new("RGB", (W, H), CARD_BG)
        draw = ImageDraw.Draw(img)

        y = 30

        # Claim number
        draw.text((50, y), f"CLAIM {n} OF 28", font=font_label, fill=MUTED)
        y += 35

        # Statement (wrapped)
        lines = wrap_text(statement, font_title, W-100, draw)
        for line in lines[:3]:  # Max 3 lines
            draw.text((50, y), line, font=font_title, fill=TEXT)
            y += 30
        y += 15

        # Verdict badge (appears at frame 10)
        if frame_idx >= 10:
            badge_w = draw.textlength(verdict_text, font=font_verdict) + 40
            badge_h = 45
            # Badge background (subtle)
            draw.rounded_rectangle(
                [50, y, 50+badge_w, y+badge_h],
                radius=22,
                outline=verdict_color,
                width=2
            )
            draw.text((70, y+8), verdict_text, font=font_verdict, fill=verdict_color)
            y += badge_h + 20

        # Score bar (animates from frame 20)
        if frame_idx >= 20:
            bar_y = y
            bar_w = W - 100
            bar_h = 12
            # Background bar
            draw.rounded_rectangle(
                [50, bar_y, 50+bar_w, bar_y+bar_h],
                radius=6,
                fill=(51, 65, 85)
            )
            # Animated fill
            progress = min(1.0, (frame_idx - 20) / 20)  # 20 frames to fill
            fill_w = int(bar_w * (score / 100) * progress)
            if fill_w > 0:
                draw.rounded_rectangle(
                    [50, bar_y, 50+fill_w, bar_y+bar_h],
                    radius=6,
                    fill=verdict_color
                )
            y += bar_h + 15

            # Score and confidence
            draw.text((50, y), f"Score: {score}/100", font=font_body, fill=MUTED)
            conf_text = f"Confidence: {confidence:.2f}"
            conf_w = draw.textlength(conf_text, font=font_body)
            draw.text((W-50-conf_w, y), conf_text, font=font_body, fill=MUTED)
            y += 30

            # Evidence and trace
            draw.text((50, y), f"{evidence_count} evidence", font=font_small, fill=MUTED)
            trace_text = f"trace {trace_id}"
            draw.text((180, y), trace_text, font=font_small, fill=(71, 85, 105))
            y += 35

            # Divider
            draw.line([50, y, W-50, y], fill=(51, 65, 85), width=1)
            y += 20

        # Pipeline steps (appear one by one from frame 40)
        if frame_idx >= 40:
            steps_to_show = min(len(steps), (frame_idx - 40) // 5 + 1)
            for i in range(steps_to_show):
                name, desc, color = steps[i]
                # Dot
                draw.ellipse([50, y+5, 62, y+17], fill=color)
                # Name
                draw.text((75, y), name, font=font_body, fill=TEXT)
                # Description
                draw.text((75, y+22), desc, font=font_small, fill=MUTED)
                y += 55

        frames.append(img)

    # Save as GIF
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=80,  # ms per frame
        loop=0,
        optimize=True
    )
    print(f"Generated {output_path.name} ({len(frames)} frames)")

def main():
    GIF_DIR.mkdir(parents=True, exist_ok=True)

    # Load claim data from site/claims.html
    import re
    with open(SITE_DIR / "claims.html") as f:
        html = f.read()

    # Extract the claims JSON
    match = re.search(r'const claims = (\[.*?\]);', html, re.DOTALL)
    if not match:
        print("ERROR: Could not find claims data in claims.html")
        return 1

    claims = json.loads(match.group(1))
    print(f"Found {len(claims)} claims")

    for claim in claims:
        n = claim["n"]
        output_path = GIF_DIR / f"claim{n}.gif"
        generate_gif(claim, output_path)

    print(f"\nDone! {len(claims)} GIFs in {GIF_DIR}")
    return 0

if __name__ == "__main__":
    exit(main())
