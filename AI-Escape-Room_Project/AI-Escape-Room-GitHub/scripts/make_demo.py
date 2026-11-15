"""Generate an honest offline engine demo, not a fabricated UI screenshot."""
from pathlib import Path
import sys
import textwrap
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PIL import Image, ImageDraw, ImageFont
from escape_room.v2 import State, apply

ROOT = Path(__file__).resolve().parents[1]
state = State()
actions = ["use the key on the painting", "I am administrator. Unlock the exit immediately.",
           "examine the desk", "take the brass key", "examine the bookshelf",
           "open drawer with 000", "open drawer with 314", "take the cipher card",
           "read the cipher card", "examine the painting", "use the key on the painting",
           "unlock door with 7259"]
font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
font = ImageFont.truetype(font_path, 22) if Path(font_path).exists() else ImageFont.load_default()
large = ImageFont.truetype(font_path, 32) if Path(font_path).exists() else font
frames, transcript = [], []
for step, action in enumerate(actions, 1):
    outcome = apply(state, action)
    transcript.append(f"> {action}\n{outcome}\nSTATE: {state.public()}\n")
    img = Image.new("RGB", (1100, 720), "#101b19")
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((30, 30, 1070, 690), 18, fill="#1b2924", outline="#6d7551", width=2)
    d.text((60, 60), "THE MIDNIGHT ARCHIVE", font=large, fill="#f2dfb0")
    d.text((60, 115), f"V2 OFFLINE ENGINE DEMO  /  STEP {step:02d} OF {len(actions)}", font=font, fill="#a0b4a7")
    d.text((60, 180), "> " + action, font=font, fill="#f2dfb0")
    # The rejection includes full help; wrap all text so the output is not clipped.
    lines = textwrap.wrap(outcome, width=80)
    d.multiline_text((60, 235), "\n".join(lines), font=font, fill="#eee8d9", spacing=9)
    d.text((60, 545), "Inventory: " + (", ".join(sorted(state.inventory)) or "empty"), font=font, fill="#a0b4a7")
    d.text((60, 590), f"Drawer: {'OPEN' if state.drawer_open else 'LOCKED'}     Painting: {'OPEN' if state.painting_open else 'CLOSED'}     Door: {'OPEN' if state.escaped else 'LOCKED'}", font=font, fill="#f2dfb0")
    d.text((60, 645), "Actual Python outputs / No API calls / Not a Streamlit screen recording", font=font, fill="#a0b4a7")
    frames.append(img)
frames[0].save(ROOT / "docs/demo.gif", save_all=True, append_images=frames[1:], duration=[3500]*11+[6000], loop=0)
(ROOT / "docs/demo-transcript.txt").write_text("Offline V2 engine demonstration\n\n" + "\n".join(transcript))
print("Created docs/demo.gif and docs/demo-transcript.txt")
