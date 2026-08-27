# Security Policy

## Scope

BASIC-JARVIS runs a local FastAPI service that can interact with Ollama, screenshots, audio devices, input devices, applications, and Python plugins. Security reports are especially valuable when they demonstrate unintended access, remote exposure, unsafe file handling, privilege escalation, or execution outside the requested workflow.

## Supported code

Security fixes are evaluated against the latest commit on the default `master` branch. Older revisions may not receive fixes independently.

## Reporting a vulnerability

Please report suspected vulnerabilities privately by emailing **itsmebk2007@gmail.com** with the subject line `BASIC-JARVIS security report`. Include the affected file or endpoint, reproduction steps, expected behavior, actual behavior, and any relevant logs with secrets removed.

Do not publish an issue or pull request containing an unpatched vulnerability, access token, private screenshot, audio recording, or other sensitive data.

## Operational guidance

Keep the backend bound to `127.0.0.1` unless you have added authentication and a deliberate network boundary. Review `ENABLE_SYSTEM_CONTROL`, plugin contents, CORS settings, upload handling, and local OS permissions before using the assistant on sensitive systems.
