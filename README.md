# Kaybee 📖

> A local, private knowledge base powered by your own AI. No cloud. No subscription. No data leaving your machine.

---

## What is Kaybee?

Kaybee (KB — Knowledge Base) is a lightweight, self-hosted AI reference tool built for developers who are tired of alt-tabbing to Stack Overflow, digging through man pages, or feeding their code to a cloud API just to remember how to do something they've done a hundred times.

It runs entirely on your local machine. Ask it anything. It answers. Nothing leaves your box.

```
$ "how do I traverse a CSV file in bash again?"
```

That's it. That's the whole pitch.

---

## Why Kaybee?

Every major IDE is racing to bundle AI assistance — but they're all cloud-based, subscription-gated, and sending your code somewhere else. Kaybee is the opposite:

- **Local** — runs on your hardware, period
- **Private** — zero telemetry, zero phone home
- **Free** — no API keys, no usage limits, no credit card
- **Fast** — no round trips to a data center

---

## How It Works

Kaybee is a thin web UI wrapping [Ollama](https://ollama.com) and a code-focused model ([Qwen2.5-Coder](https://ollama.com/library/qwen2.5-coder) by default). Ask questions in plain English, get answers in plain English (or code). Everything runs in Docker.

```
Browser → Kaybee UI → FastAPI → Ollama (local) → Qwen2.5-Coder
```

---

## Requirements

- Docker
- ~6GB disk space (for the model)
- 8GB+ RAM recommended

---

## Quickstart

```bash
# Clone the repo
git clone https://github.com/yourusername/kaybee.git
cd kaybee

# Start everything
docker compose up -d

# Pull the model (one time, ~4.7GB)
docker exec kaybee-ollama ollama pull qwen2.5-coder:7b

# Open the UI
open http://localhost:8080
```

---

## Configuration

Edit `docker-compose.yml` to swap models. Any Ollama-compatible model works:

```yaml
environment:
  - MODEL=qwen2.5-coder:7b   # swap to codellama:7b, deepseek-coder:6.7b, etc.
```

---

## Stack

| Layer | Tech |
|---|---|
| Frontend | HTML / CSS / JS (no framework) |
| Backend | Python / FastAPI |
| AI Runtime | Ollama |
| Default Model | Qwen2.5-Coder 7B |
| Container | Docker Compose |

---

## Philosophy

Kaybee exists because developer knowledge tooling shouldn't require an internet connection, a subscription, or trust that some company isn't reading your code.

Your questions are yours. Your answers are yours. Your box is yours.

---

## Roadmap

- [ ] Conversation history
- [ ] Context-aware file input (paste a file, ask about it)
- [ ] Model switcher in UI
- [ ] Keyboard-first interface
- [ ] CLI wrapper (`kb "how do I..."`)

---

## Contributing

PRs welcome. Keep it simple. Keep it local.

---

## License

AGPL v3 — free to use, modify, and distribute. Any derivative work or service built on Kaybee must also be open source under the same license.
