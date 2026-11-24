# Designing Innovative Products & Business: course videos

Narrated lesson videos for the six sessions of the course (ESEIAAT – UPC), generated from text scripts. The visual style matches the course slides.

Each session has **one script**, **one notebook** and **one video**. The notebook runs in Google Colab and saves the MP4 to **My Drive / Curs Design**.

## Sessions

| Session | Notebook (opens in Colab) | Script | Approx. length |
|---|---|---|---|
| 1 · Innovation, Blue Ocean & Open Innovation | [Open](https://colab.research.google.com/github/jordicusidoroura-stack/design_innovation_course/blob/main/notebooks/Session1_Innovation_Blue_Ocean.ipynb) | `sessions/session1_innovation_blue_ocean.json` | 9–10 min |
| 2 · Design Thinking | [Open](https://colab.research.google.com/github/jordicusidoroura-stack/design_innovation_course/blob/main/notebooks/Session2_Design_Thinking.ipynb) | `sessions/session2_design_thinking.json` | 7 min |
| 3 · Business Model Canvas & Lean Startup | [Open](https://colab.research.google.com/github/jordicusidoroura-stack/design_innovation_course/blob/main/notebooks/Session3_BMC_Lean_Startup.ipynb) | `sessions/session3_bmc_lean_startup.json` | 15 min |
| 4 · Value Proposition Design | [Open](https://colab.research.google.com/github/jordicusidoroura-stack/design_innovation_course/blob/main/notebooks/Session4_Value_Proposition_Design.ipynb) | `sessions/session4_value_proposition_design.json` | 6 min |
| 5 · Testing Business Ideas & Agile | [Open](https://colab.research.google.com/github/jordicusidoroura-stack/design_innovation_course/blob/main/notebooks/Session5_Testing_Business_Ideas_Agile.ipynb) | `sessions/session5_testing_business_ideas_agile.json` | 8 min |
| 6 · From Innovation to Scalable Value | [Open](https://colab.research.google.com/github/jordicusidoroura-stack/design_innovation_course/blob/main/notebooks/Session6_Innovation_to_Scalable_Value.ipynb) | `sessions/session6_innovation_to_scalable_value.json` | 7–8 min |

## Making a video

1. Click **Open** for the session.
2. In Colab: **Runtime → Run all**, and accept the Google Drive permission.
3. After 10–15 minutes the video is in **My Drive / Curs Design**.

## Changing the content

Edit the session's JSON file on GitHub (pencil icon), commit, and run the notebook again. The notebook always downloads the latest version. Only the sentences you changed are synthesised again; the rest come from the cache in `Curs Design/_tts_cache`.

A script is a list of **scenes**. Each scene has **beats**: one or two spoken sentences (`say`) and the elements that appear on screen while they are spoken (`show`).

```json
{
  "type": "cards",
  "label": "02 · Principles",
  "title": "Three principles behind Design Thinking",
  "cards": [{"title": "Empathy", "text": "Design based on a deep understanding of people."}],
  "beats": [{"say": "Design Thinking rests on three principles...", "show": "card0"}]
}
```

Voice settings are in `meta` (`voice`, `rate`), or can be overridden in the notebook.

### Scene types

| Type | Use it for | Fields | Element ids for `show` |
|---|---|---|---|
| `title` | Opening slide | `label`, `title`, `subtitle` | (automatic) |
| `statement` | A big idea or a quote, on dark background | `label`, `text`, `sub` | `sub` |
| `cards` | 2–4 concepts side by side | `cards[{tag?, title, text}]`, `banner?` | `card0`…, `banner` |
| `steps` | A process (2–8 steps; two rows if more than 5) | `steps[{tag?, title, text?}]`, `banner?` | `s0`…, `banner` |
| `cycle` | A loop (3–6 nodes) | `nodes[{title, text}]`, `center?`, `banner?` | `n0`…, `center` |
| `quad` | 2×2 matrix, optional axes and centre | `quads[4×{tag?, title, text or items}]`, `x_axis?`, `y_axis?`, `highlight?`, `center?`, `banner?` | `q0`…`q3`, `banner` |
| `table` | Comparison | `headers[2 or 3]`, `rows[[…]]`, `banner?` | `r0`…, `banner` |
| `list` | Up to 10 items in one or two columns | `items[{title, text?}]`, `style: number/check`, `banner?` | `i0`…, `banner` |
| `stats` | 2–4 big numbers | `stats[{value, label, highlight?}]`, `banner?` | `st0`…, `banner` |
| `template` | Fill-in templates (POV, test card, user story) | `cards[{head, dark?, rows[{lead, fill}]}]`, `example?`, `example_label?` | `card0`, `card1`, `example` |
| `canvas` | Business Model Canvas (or Lean Canvas with `labels`) | `labels?` | `kp ka kr vp cr ch cs cost rev`, `sides` |
| `block` | One BMC block in detail | `block`, `questions[3]`, `mistake`, `example` | `q0`…, `mistake`, `example` |
| `split` | Key vs not key | `left{head, items}`, `right{head, items}`, `banner` | `lhead l0… rhead r0…`, `banner` |
| `vpc` | Value Proposition Canvas | `items{jobs, gains, pains, products, gain_creators, pain_relievers}?` | `shape`, those keys, `fit` |
| `strategy` | Blue Ocean strategy canvas | `factors`, `curves[{name, color: ink/amber, values 0–5}]`, `note?` | `curve0`, `curve1` |
| `errc` | ERRC grid | `quads[4×{question, items}]`, `banner?` | `q0`…`q3`, `banner` |

Elements that no beat mentions appear at the start of the scene.

### Drafting a new script with an AI assistant

Attach the session slides and one of the existing JSON files, and ask:

> Write the video script for this session in exactly the same JSON format as the attached example. Use only the scene types and fields listed in the README of the repo. Each beat is one or two spoken sentences in "say", and "show" lists the element ids that appear when it is spoken. Keep on-screen text short and put the explanation in the narration. Target 7–9 minutes (about 1,100 words of narration). Return only the JSON.

## Training Ground (web game)

`web/` holds a small static web game for students: one quiz mission per session (questions, instant explanations, stars, XP and badges) and a 60-second **Demo Day Rush** that mixes questions from every session. Progress is saved in each student's browser; there are no accounts and no server-side data.

- **Questions** live in `web/quizzes.js`. Each question has four options, the index of the right one (`answer`) and a short explanation (`why`). Options are shuffled when shown.
- **Video links**: put the Moodle link of each session in its `video` field and a "Watch the video" link appears on the mission.

### Deploy to Cloud Run

From [Google Cloud Shell](https://shell.cloud.google.com) in your project:

```bash
git clone https://github.com/jordicusidoroura-stack/design_innovation_course
cd design_innovation_course/web
bash deploy.sh
```

The first time, `gcloud` asks to enable Cloud Run, Cloud Build and Artifact Registry and to create an image repository: answer `Y`. At the end it prints the public URL. To publish changes (new questions, video links), `git pull` and run `bash deploy.sh` again.

Cost: the service scales to zero when nobody uses it (`--min-instances 0`) and is capped at 2 instances. A class of students stays far inside Cloud Run's monthly free tier (2 million requests). The only other costs are storing a ~20 MB container image and a one-minute build per deploy: cents per month at most.

To try it locally: `cd web && python3 -m http.server 8000` and open http://localhost:8000.

## Working locally (optional)

Requires Python 3, Pillow and ffmpeg.

```bash
python tools/preview.py sessions/session2_design_thinking.json          # contact sheet of all scenes
python tools/preview.py sessions/session2_design_thinking.json 6        # one scene at full size
python tools/preview.py sessions/session2_design_thinking.json --video  # silent preview video
python tools/make_notebooks.py                                          # regenerate notebooks
```

## Structure

```
videokit/      the video engine (layouts, narration, rendering)
sessions/      one script per session (JSON)
notebooks/     one Colab notebook per session
tools/         local preview and notebook generator
web/           Training Ground web game (static, deployable to Cloud Run)
```
