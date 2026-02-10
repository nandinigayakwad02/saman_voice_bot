# Quick Reference - WhatsApp Voice Bot

## Run Commands

```bash
# Quick Start (after first setup)
source .venv/bin/activate && python3 run.py

# With tunnel (for Meta webhook)
# Terminal 1:
source .venv/bin/activate && python3 run.py

# Terminal 2:
lt --port 8000
```

## Installation (One-Time Setup)

```bash
cd /home/pc/Documents/Nitu\'s\ folder/Josh_voice_bot
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

## Check Status

```bash
# Server running?
curl http://localhost:8000/health

# View logs (if background)
tail -f logs/app.log  # if logging to file

# Or check terminal output
```

## Restart Server

```bash
# Stop: Ctrl+C
# Start: python3 run.py
```

## Update Dependencies

```bash
source .venv/bin/activate
uv pip install -r requirements.txt --upgrade
```

---

See `SETUP_GUIDE.md` for full documentation.
