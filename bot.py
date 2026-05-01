import os
import socket
import subprocess
import logging
from functools import wraps

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

load_dotenv()

BOT_TOKEN = os.environ["BOT_TOKEN"]
ALLOWED_USER_ID = int(os.environ["ALLOWED_USER_ID"])
PC_MAC = os.environ["PC_MAC"]
PC_IP = os.environ["PC_IP"]

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


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
        s.sendto(magic, ("<broadcast>", 9))


def is_online(ip: str) -> bool:
    result = subprocess.run(
        ["ping", "-c", "1", "-W", "2", ip],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


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
    online = is_online(PC_IP)
    if online:
        await update.message.reply_text("🟢 Онлайн")
    else:
        await update.message.reply_text("🔴 Офлайн")


def main() -> None:
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("wake", cmd_wake))
    app.add_handler(CommandHandler("status", cmd_status))
    logger.info("Bot started, polling…")
    app.run_polling()


if __name__ == "__main__":
    main()
