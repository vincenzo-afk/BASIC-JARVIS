---
project: basic-jarvis-showcase
format: landscape
width: 1920
height: 1080
duration: 18
flow: autonomous
---

# BASIC-JARVIS showcase storyboard

## Video direction

The piece feels like a living local control surface: quiet, technical, and confident. Keep the existing renderer’s near-black surfaces and cyan status language. Use cyan for active signals and green only for connected/ready states. Scene changes are clean horizontal wipes and panel morphs rather than generic gradient dissolves. No narration, music, or captions; all copy is on-screen and editable.

## Scene 1 — Local by design

- `id`: `intro`
- `start`: `0`
- `duration`: `3.2`
- `asset_candidates`: `../../electron-app/public/icon.png`
- `transition_in`: `cut`
- `message`: Establish BASIC-JARVIS as a local-first desktop AI assistant. Show the repository name, the Electron + FastAPI + Ollama stack, and a live local status readout.
- `motion`: logo reveal, signal pulse, staggered stack labels.

## Scene 2 — Chat with your local model

- `id`: `chat`
- `start`: `3.2`
- `duration`: `3.8`
- `asset_candidates`: none; authored interface panel
- `transition_in`: `wipe-left`
- `message`: Show a prompt flowing into a local Ollama model and returning a response. Mention streaming and model choice without claiming a hosted API.
- `motion`: prompt types in, response panel expands, model badge locks into connected state.

## Scene 3 — See and hear the desktop

- `id`: `perception`
- `start`: `7`
- `duration`: `3.8`
- `asset_candidates`: none; authored interface panel
- `transition_in`: `wipe-left`
- `message`: Show the screen/OCR and voice surfaces side by side: monitor capture, Tesseract OCR, Whisper transcription, and Piper speech output.
- `motion`: scan line travels across screen card, waveform rises, capability labels resolve.

## Scene 4 — Workflows and plugins

- `id`: `automation`
- `start`: `10.8`
- `duration`: `3.8`
- `asset_candidates`: none; authored interface panel
- `transition_in`: `wipe-left`
- `message`: Show the agent action graph and plugin lifecycle. Keep the framing grounded in the implemented agent and Python plugin routes.
- `motion`: nodes connect in sequence, plugin modules slide into a running state, green check appears.

## Scene 5 — A desktop assistant you can inspect

- `id`: `closing`
- `start`: `14.6`
- `duration`: `3.4`
- `asset_candidates`: `../../electron-app/public/icon.png`
- `transition_in`: `wipe-left`
- `message`: Close with the local stack and a repository call to action: inspect the code, run it locally, and build on the project.
- `motion`: architecture line draws, repository URL rises, final signal breathes.
