# Contributing to BASIC-JARVIS

Thank you for helping improve BASIC-JARVIS. Contributions should preserve the project’s local-first design, document user-facing behavior, and include the safest practical validation for the affected area.

## Development prerequisites

Install Python 3.8+, Node.js 16+, Git, and Ollama. Screen, voice, and desktop-control changes may also require Tesseract OCR, Piper, audio drivers, and platform-specific permissions.

## Local setup

```bash
git clone https://github.com/vincenzo-afk/BASIC-JARVIS.git
cd BASIC-JARVIS
chmod +x scripts/*.sh
./scripts/install_all.sh
cp backend/.env.example backend/.env
```

Start the backend and Electron shell in separate terminals:

```bash
./scripts/run_backend.sh
./scripts/start_electron.sh
```

On Windows, use `scripts\\install_all.bat`, `scripts\\run_backend.bat`, and `scripts\\start_electron.bat`.

## Branches and commits

Create a focused branch from `main` using one of these prefixes:

| Change | Branch prefix |
|---|---|
| New behavior | `feature/` |
| Bug fix | `fix/` |
| Documentation | `docs/` |
| Refactor | `refactor/` |
| Tests or maintenance | `test/` or `chore/` |

Use concise [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) such as `feat(voice): add language detection` or `fix(electron): load the development server`.

## Validation

Run the checks relevant to your change before opening a pull request:

```bash
python -m compileall -q backend scripts test_features.py
cd electron-app
npm ci
npm run build
```

The integration scripts require a running backend and may also require Ollama or native desktop capabilities:

```bash
python test_features.py
python scripts/test_api.py
```

If a check cannot run in your environment, explain why in the pull request rather than silently omitting it.

## Pull requests

Pull requests should explain the problem, summarize the implementation, identify security or privacy implications, and list the commands that were run. Include screenshots or recordings for visible Electron changes. Keep unrelated formatting or dependency changes out of focused pull requests.

The repository uses GitHub Actions for Python compilation and the Electron production build. A pull request should leave those checks passing.

## Security-sensitive changes

Changes involving screen capture, microphone input, system control, plugin execution, file access, or network exposure require additional care. Do not add credentials or private user data to the repository. Report suspected vulnerabilities privately using the process in [`SECURITY.md`](SECURITY.md) instead of opening a public issue.

## Questions

For normal bugs and feature requests, use the repository’s issue templates. For security concerns, use the private reporting path in [`SECURITY.md`](SECURITY.md).
