#!/data/data/com.termux/files/usr/bin/bash
termux-wake-lock
cd "$(dirname "$0")"
source .venv/bin/activate
python bot.py
