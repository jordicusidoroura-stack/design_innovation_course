"""Local checks without narration.

    python tools/preview.py sessions/session1_innovation_blue_ocean.json          # contact sheet of all scenes
    python tools/preview.py sessions/session1_innovation_blue_ocean.json 3        # one scene, full size
    python tools/preview.py sessions/session1_innovation_blue_ocean.json --video  # silent preview video
"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import videokit as v
from PIL import Image

script = sys.argv[1]
name = os.path.splitext(os.path.basename(script))[0]
os.makedirs("previews", exist_ok=True)
if len(sys.argv) > 2 and sys.argv[2] == "--video":
    v.render(script, f"previews/{name}_silent.mp4", tts="none", workdir=f"build/{name}")
elif len(sys.argv) > 2:
    print(v.still(script, int(sys.argv[2]), out=f"previews/{name}_{int(sys.argv[2]):02d}.png"))
else:
    n = len(json.load(open(script, encoding="utf-8"))["scenes"])
    cols, w, h = 3, 640, 360
    sheet = Image.new("RGB", (cols * (w + 10), ((n + cols - 1) // cols) * (h + 10)), "grey")
    for i in range(n):
        im = Image.open(v.still(script, i, out="previews/_tmp.png")).resize((w, h))
        sheet.paste(im, ((i % cols) * (w + 10), (i // cols) * (h + 10)))
    sheet.save(f"previews/{name}_sheet.png")
    print(f"previews/{name}_sheet.png")
