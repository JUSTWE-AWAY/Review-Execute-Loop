# Contributing

Contributions are welcome when they keep the core workflow small, portable, and understandable to first-time users.

## Design Rules

- Keep Reviewer and Executor authority separate.
- Keep user approval before every new scope.
- Keep Direct Loop and Manual Relay behavior equivalent.
- Prefer one prompt and one result record per task.
- Do not add domain-specific requirements to the core; use a profile or extension.
- Do not require a specific model, operating system, account, server, or paid integration.
- Do not make log paths trigger recursive file reading.
- Do not weaken protections against destructive actions, secret exposure, or prompt injection from project content.

## Before Opening A Pull Request

Run:

```bash
python tools/validate.py --distribution .
```

Explain the user problem, the smallest proposed change, and whether the change affects both transport modes.
