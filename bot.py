"""
MathBot — Bot Telegram d'aide aux devoirs pour collégiens/lycéens
Point d'entrée principal
"""

import logging
import os
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from dotenv import load_dotenv

from handlers.commands import start, help_command, limit_command
from handlers.math_handler import handle_math_question
from handlers.training import handle_training_callback

# ── Chargement des variables d'environnement ──────────────────────────────────
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN manquant dans le fichier .env !")

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Lance le bot."""
    logger.info("🚀 Démarrage de MathBot...")

    app = Application.builder().token(TOKEN).build()

    # Commandes
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("limit", limit_command))

    # Messages texte → résolution de problème
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_math_question)
    )

    # Boutons inline (mode entraînement)
    app.add_handler(CallbackQueryHandler(handle_training_callback))

    logger.info("✅ Bot prêt. En attente de messages...")
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
