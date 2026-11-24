"""Generates one Colab notebook per session script:  python tools/make_notebooks.py"""
import glob, json, os

REPO = "jordicusidoroura-stack/design_innovation_course"
ROOT = os.path.join(os.path.dirname(__file__), "..")


def md(src):
    return {"cell_type": "markdown", "metadata": {}, "source": src}


def code(src):
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": src}


def notebook(script_rel, meta, nb_name):
    title = meta["session"]
    out = meta["output"]
    colab = f"https://colab.research.google.com/github/{REPO}/blob/main/notebooks/{nb_name}"
    cells = [
        md(f"""# {title}
**{meta['course']}** · video generator

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)]({colab})

Run the cells in order (**Runtime → Run all** also works). The finished video is saved to **My Drive / Curs Design / {out}**.

- The script (narration and on-screen text) is `{script_rel}` in the GitHub repo. To change a sentence, edit that file on GitHub and run this notebook again: it always downloads the latest version.
- Narration clips are cached in `Curs Design/_tts_cache` on your Drive, so re-rendering after a small change only synthesises the sentences that changed.
- Rendering takes about 10–15 minutes."""),
        md("## 1 · Setup\nConnects your Google Drive (accept the permission pop-up) and downloads the latest version of the course repo."),
        code(f"""SCRIPT = "{script_rel}"
DRIVE_FOLDER = "/content/drive/MyDrive/Curs Design"

from google.colab import drive
drive.mount("/content/drive")

import os
if os.path.exists("/content/design_innovation_course"):
    !git -C /content/design_innovation_course fetch -q && git -C /content/design_innovation_course reset -q --hard origin/main
else:
    !git clone -q https://github.com/{REPO} /content/design_innovation_course
%cd /content/design_innovation_course
!pip -q install edge-tts nest_asyncio
!apt-get -qq install -y fonts-liberation > /dev/null
os.makedirs(DRIVE_FOLDER, exist_ok=True)
print("Ready.")"""),
        md("## 2 · (Optional) Look at one scene\nShows the last frame of a scene in a few seconds, without rendering the video. Change the number to see another scene (0 is the title)."),
        code("""import importlib, videokit as v
importlib.reload(v)
from IPython.display import Image, display
display(Image(v.still(SCRIPT, 0, out="/content/frame.png"), width=960))"""),
        md("""## 3 · Voice
- **Edge** (default): free, no key needed. Other English voices: `en-GB-SoniaNeural`, `en-US-AndrewMultilingualNeural`, `en-US-AvaMultilingualNeural`.
- **Gemini**: set `TTS = "gemini"` and a voice such as `Charon`, `Kore` or `Puck`. It needs a `GEMINI_API_KEY` in Colab's 🔑 *Secrets* panel (get one at aistudio.google.com). The free tier allows about 10 sentences per minute, so the notebook paces itself automatically: count on 15–20 extra minutes."""),
        code("""TTS = "edge"                 # "edge" or "gemini"
VOICE = "en-GB-RyanNeural"   # Gemini example: "Charon"

if TTS == "gemini":
    !pip -q install google-genai
    from google.colab import userdata
    os.environ["GEMINI_API_KEY"] = userdata.get("GEMINI_API_KEY")"""),
        md("## 4 · Render and save to Drive"),
        code("""import importlib, json, shutil, videokit as v
importlib.reload(v)
name = json.load(open(SCRIPT, encoding="utf-8"))["meta"]["output"]
local = v.render(SCRIPT, f"/content/out/{name}", tts=TTS, voice=VOICE,
                 workdir="/content/build", cache_dir=f"{DRIVE_FOLDER}/_tts_cache")
shutil.copy(local, f"{DRIVE_FOLDER}/{name}")
print("Saved to Drive:", f"{DRIVE_FOLDER}/{name}")"""),
    ]
    return {"cells": cells,
            "metadata": {"colab": {"provenance": [], "name": nb_name},
                         "kernelspec": {"name": "python3", "display_name": "Python 3"},
                         "language_info": {"name": "python"}},
            "nbformat": 4, "nbformat_minor": 0}


def main():
    os.makedirs(os.path.join(ROOT, "notebooks"), exist_ok=True)
    rows = []
    for path in sorted(glob.glob(os.path.join(ROOT, "sessions", "session*.json"))):
        meta = json.load(open(path, encoding="utf-8"))["meta"]
        script_rel = "sessions/" + os.path.basename(path)
        nb_name = meta["output"].replace(".mp4", ".ipynb")
        nb = notebook(script_rel, meta, nb_name)
        with open(os.path.join(ROOT, "notebooks", nb_name), "w", encoding="utf-8") as f:
            json.dump(nb, f, ensure_ascii=False, indent=1)
        rows.append((meta["session"], nb_name, script_rel))
        print("wrote", nb_name)
    return rows


if __name__ == "__main__":
    main()
