import os
import socket
import threading
import time
import logging
from functools import wraps

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

load_dotenv()

BOT_TOKEN = os.environ["BOT_TOKEN"]
ALLOWED_USER_ID = int(os.environ["ALLOWED_USER_ID"])
PC_MAC = os.environ["PC_MAC"]
PROXY = os.environ.get("PROXY")

HEARTBEAT_PORT = 7779
# Если за 45 секунд не было пакета — ПК выключен (агент шлёт каждые 20с)
HEARTBEAT_TIMEOUT = 45

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

last_heartbeat: float = 0.0


def heartbeat_listener() -> None:
    """Фоновый поток: слушает UDP-пакеты от pc_agent.py и обновляет last_heartbeat."""
    global last_heartbeat
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("0.0.0.0", HEARTBEAT_PORT))
        logger.info("Heartbeat listener started on UDP :%s", HEARTBEAT_PORT)
        while True:
            try:
                s.recvfrom(64)
                last_heartbeat = time.monotonic()
            except OSError:
                break


def is_online() -> bool:
    if last_heartbeat == 0.0:
        return False
    return (time.monotonic() - last_heartbeat) < HEARTBEAT_TIMEOUT


def authorized_only(handler):
    @wraps(handler)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != ALLOWED_USER_ID:
            logger.warning("Unauthorized access attempt from user_id=%s", update.effective_user.id)
            return
        return await handler(update, context)
    return wrapper


def send_wol(mac: str) -> None:
    mac_bytes = bytes.fromhex(mac.replace(":", "").replace("-", ""))
    magic = b"\xff" * 6 + mac_bytes * 16
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        for target in [("<broadcast>", 9), ("192.168.0.255", 9)]:
            s.sendto(magic, target)


@authorized_only
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Команды:\n"
        "/wake — включить ПК\n"
        "/status — проверить, онлайн ли ПК"
    )


@authorized_only
async def cmd_wake(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        send_wol(PC_MAC)
        logger.info("WoL packet sent to %s", PC_MAC)
        await update.message.reply_text("Пакет отправлен ✅")
    except Exception as e:
        logger.error("Failed to send WoL packet: %s", e)
        await update.message.reply_text(f"Ошибка: {e}")


@authorized_only
async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if is_online():
        await update.message.reply_text("🟢 Онлайн")
    else:
        await update.message.reply_text("🔴 Офлайн")


def main() -> None:
    t = threading.Thread(target=heartbeat_listener, daemon=True)
    t.start()

    builder = ApplicationBuilder().token(BOT_TOKEN)
    if PROXY:
        builder = builder.proxy(PROXY).get_updates_proxy(PROXY)
    app = builder.build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("wake", cmd_wake))
    app.add_handler(CommandHandler("status", cmd_status))
    logger.info("Bot started, polling…")
    app.run_polling()


if __name__ == "__main__":
    main()
