"""
Handlers pour les commandes Telegram : /start, /help, /limit
"""

from telegram import Update
from telegram.ext import ContextTypes

from utils.database import register_user, get_remaining, FREE_DAILY_LIMIT, is_premium


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Message de bienvenue chaleureux pour les élèves."""
    user = update.effective_user
    register_user(user.id, user.username, user.first_name)

    prenom = user.first_name or "toi"

    message = (
        f"👋 Salut {prenom} ! Je suis **MathBot** 🤖\n\n"
        "Je suis là pour t'aider à *comprendre* tes exercices de maths "
        "— pas juste te donner les réponses 😄\n\n"
        "📝 **Comment ça marche ?**\n"
        "Envoie-moi un exercice de maths directement ici, et je vais :\n"
        "  • Analyser le problème\n"
        "  • Te l'expliquer étape par étape\n"
        "  • Te donner une astuce pour retenir\n\n"
        "**Exemple :** _Calcule l'aire d'un triangle de base 6 cm et de hauteur 4 cm._\n\n"
        f"🎁 Tu as **{FREE_DAILY_LIMIT} questions gratuites** par jour.\n\n"
        "Tape /help si tu as besoin d'aide. C'est parti ! 🚀"
    )

    await update.message.reply_text(message, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Explique comment utiliser le bot."""
    message = (
        "📚 **Aide — MathBot**\n\n"
        "**Ce que je sais faire :**\n"
        "✅ Algèbre (équations, inéquations, factorisation)\n"
        "✅ Géométrie (périmètre, aire, volume, théorèmes)\n"
        "✅ Calcul littéral\n"
        "✅ Statistiques & probabilités\n"
        "✅ Fonctions & graphiques\n"
        "✅ Trigonométrie\n"
        "✅ Arithmétique (PGCD, nombres premiers…)\n\n"
        "**Comment l'utiliser ?**\n"
        "Envoie ton exercice en message normal. Sois précis !\n\n"
        "💡 *Bon exemple :* Résous l'équation 2x + 5 = 13\n"
        "😅 *Moins bon :* aide moi\n\n"
        "**Commandes disponibles :**\n"
        "/start — Recommencer\n"
        "/help — Cette aide\n"
        "/limit — Voir tes questions restantes\n\n"
        "❗ Je suis un assistant pédagogique : j'explique toujours, "
        "je ne fais pas les devoirs à ta place 😉"
    )

    await update.message.reply_text(message, parse_mode="Markdown")


async def limit_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Affiche le nombre de questions restantes aujourd'hui."""
    user = update.effective_user
    register_user(user.id, user.username, user.first_name)

    remaining = get_remaining(user.id)
    premium = is_premium(user.id)

    if premium:
        message = (
            "⭐ **Compte Premium**\n\n"
            "Tu as un accès **illimité** — pose autant de questions que tu veux ! 🎉"
        )
    elif remaining > 0:
        emoji = "🟢" if remaining == FREE_DAILY_LIMIT else ("🟡" if remaining > 1 else "🔴")
        message = (
            f"📊 **Tes questions du jour**\n\n"
            f"{emoji} Il te reste **{remaining} question{'s' if remaining > 1 else ''}** "
            f"sur {FREE_DAILY_LIMIT} aujourd'hui.\n\n"
            "Le compteur se remet à zéro chaque jour à minuit 🕛"
        )
    else:
        message = (
            "⛔ **Limite atteinte pour aujourd'hui**\n\n"
            f"Tu as utilisé tes {FREE_DAILY_LIMIT} questions gratuites.\n\n"
            "🔄 Le compteur repart à zéro demain à minuit.\n\n"
            "⭐ **Passe en Premium** pour un accès illimité !\n"
            "Contacte @admin pour plus d'infos."
        )

    await update.message.reply_text(message, parse_mode="Markdown")
