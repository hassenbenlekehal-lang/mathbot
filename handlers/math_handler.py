"""
Handler principal : traitement des messages mathématiques.
Vérifie la limite, appelle le solveur, propose le mode entraînement.
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ChatAction

from utils.database import (
    register_user,
    can_use,
    increment_usage,
    get_remaining,
    FREE_DAILY_LIMIT,
)
from utils.solver import solve_problem

logger = logging.getLogger(__name__)

# Stockage temporaire du dernier problème par utilisateur (en mémoire)
# Pour de la persistance, on pourrait l'ajouter dans SQLite
last_problem: dict[int, str] = {}


async def handle_math_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Reçoit un problème, résout et explique."""
    user = update.effective_user
    problem = update.message.text.strip()

    # Enregistrement de l'utilisateur si nouveau
    register_user(user.id, user.username, user.first_name)

    # ── Vérification de la limite ─────────────────────────────────────────────
    if not can_use(user.id):
        remaining_msg = (
            "⛔ **Limite quotidienne atteinte !**\n\n"
            f"Tu as utilisé tes {FREE_DAILY_LIMIT} questions gratuites pour aujourd'hui.\n\n"
            "⏰ Reviens demain — le compteur se remet à zéro à minuit !\n\n"
            "⭐ Pour un accès illimité, passe en **Premium**.\n"
            "Contacte @admin pour en savoir plus 😊"
        )
        await update.message.reply_text(remaining_msg, parse_mode="Markdown")
        return

    # ── Validation minimale de la longueur ───────────────────────────────────
    if len(problem) < 5:
        await update.message.reply_text(
            "🤔 Ton message est un peu court...\n"
            "Envoie-moi un exercice complet et je t'aide ! 😊"
        )
        return

    if len(problem) > 2000:
        await update.message.reply_text(
            "📝 Ton exercice est très long ! Essaie de l'envoyer en plusieurs parties."
        )
        return

    # ── Indicateur de frappe ──────────────────────────────────────────────────
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action=ChatAction.TYPING
    )

    # ── Incrément du compteur ─────────────────────────────────────────────────
    increment_usage(user.id)
    remaining = get_remaining(user.id)

    # ── Appel au solveur ──────────────────────────────────────────────────────
    logger.info(f"Résolution pour user {user.id} : {problem[:80]}...")
    solution = await solve_problem(problem)

    # ── Stockage du problème pour mode entraînement ───────────────────────────
    last_problem[user.id] = problem

    # ── Envoi de la solution ──────────────────────────────────────────────────
    # Telegram a une limite de 4096 caractères par message
    if len(solution) > 4000:
        # Découper en deux messages
        mid = solution[:4000].rfind("\n")
        await update.message.reply_text(solution[:mid], parse_mode="Markdown")
        await update.message.reply_text(solution[mid:], parse_mode="Markdown")
    else:
        await update.message.reply_text(solution, parse_mode="Markdown")

    # ── Bouton mode entraînement ──────────────────────────────────────────────
    keyboard = [
        [
            InlineKeyboardButton(
                "🏋️ Exercice similaire pour m'entraîner", callback_data="training"
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Message de suivi avec le compteur restant
    if remaining == 0:
        suivi = (
            "⚠️ C'était ta **dernière question** du jour !\n"
            "Reviens demain pour continuer 💪"
        )
    elif remaining == 1:
        suivi = f"💬 Il te reste **1 question** aujourd'hui."
    else:
        suivi = f"💬 Il te reste **{remaining} questions** aujourd'hui."

    await update.message.reply_text(
        suivi,
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )
