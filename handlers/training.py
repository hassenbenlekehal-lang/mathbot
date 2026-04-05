"""
Mode entraînement : génère un exercice similaire à celui que l'élève vient de faire.
Activé via le bouton inline "Exercice similaire".
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ChatAction

from utils.database import can_use, increment_usage, get_remaining
from utils.solver import generate_similar_exercise
from handlers.math_handler import last_problem

logger = logging.getLogger(__name__)

NIVEAU_EMOJI = {
    "Facile": "🟢",
    "Moyen": "🟡",
    "Difficile": "🔴",
}


async def handle_training_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gère le clic sur le bouton 'Exercice similaire'."""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    # ── Vérification de la limite ─────────────────────────────────────────────
    if not can_use(user_id):
        await query.message.reply_text(
            "⛔ Tu as atteint ta limite quotidienne.\n"
            "Reviens demain pour t'entraîner ! 💪"
        )
        return

    # ── Récupération du dernier problème ─────────────────────────────────────
    problem = last_problem.get(user_id)
    if not problem:
        await query.message.reply_text(
            "🤔 Je n'ai pas trouvé ton exercice précédent.\n"
            "Envoie-moi d'abord un problème !"
        )
        return

    # ── Génération de l'exercice ──────────────────────────────────────────────
    await context.bot.send_chat_action(
        chat_id=query.message.chat_id, action=ChatAction.TYPING
    )

    exercise = await generate_similar_exercise(problem)

    if not exercise:
        await query.message.reply_text(
            "😅 Je n'ai pas réussi à générer un exercice similaire.\n"
            "Réessaie dans quelques secondes !"
        )
        return

    # ── Incrément du compteur ─────────────────────────────────────────────────
    increment_usage(user_id)
    remaining = get_remaining(user_id)

    # ── Formatage et envoi ────────────────────────────────────────────────────
    niveau = exercise.get("niveau", "Moyen")
    notion = exercise.get("notion", "")
    enonce = exercise.get("enonce", "")
    emoji = NIVEAU_EMOJI.get(niveau, "🟡")

    message = (
        f"🏋️ **Mode entraînement**\n\n"
        f"📌 Notion : _{notion}_\n"
        f"{emoji} Niveau : _{niveau}_\n\n"
        f"**Essaie cet exercice :**\n\n"
        f"_{enonce}_\n\n"
        f"💡 Essaie de le résoudre seul d'abord !\n"
        f"Quand tu es prêt, envoie-le moi et je vérifierai ta démarche 😊"
    )

    # Bouton pour envoyer l'exercice directement
    keyboard = [
        [
            InlineKeyboardButton(
                "✏️ Résoudre cet exercice", callback_data=f"solve_training:{enonce[:200]}"
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.reply_text(
        message, parse_mode="Markdown", reply_markup=reply_markup
    )

    if remaining == 0:
        await query.message.reply_text(
            "⚠️ C'était ta **dernière question** du jour !", parse_mode="Markdown"
        )
