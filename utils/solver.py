"""
Moteur de résolution des problèmes mathématiques via Claude (Anthropic API).
Retourne une explication étape par étape en français simple (niveau collège/lycée).
"""

import os
import httpx
import json
import logging

logger = logging.getLogger(__name__)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MODEL = "claude-sonnet-4-5"
API_URL = "https://api.anthropic.com/v1/messages"

SYSTEM_PROMPT = """Tu es MathBot, un assistant pédagogique pour les élèves de collège et lycée en France.

Ton rôle : aider les élèves à COMPRENDRE les maths, pas juste avoir la réponse.

Règles ABSOLUES :
1. Toujours expliquer ÉTAPE PAR ÉTAPE, clairement.
2. Utiliser un français simple, niveau A2-B1. Pas de mots compliqués inutiles.
3. Être sympa et encourageant, comme un prof cool.
4. NE JAMAIS donner uniquement la réponse sans explication.
5. Utiliser des emojis avec modération pour rendre le texte vivant.
6. Si la question n'est pas un problème de maths, dire gentiment que tu n'es là que pour les maths.

Format de ta réponse :
🔍 **Analyse du problème**
[Reformuler le problème en une phrase simple]

📚 **Ce qu'il faut savoir**
[Rappel de la règle ou formule utile, en 1-3 lignes]

🪜 **Résolution étape par étape**
**Étape 1 :** [...]
**Étape 2 :** [...]
... (autant d'étapes que nécessaire)

✅ **Réponse finale**
[La réponse claire]

💡 **Astuce pour retenir**
[Un conseil ou moyen mnémotechnique en 1 phrase]"""

TRAINING_SYSTEM_PROMPT = """Tu es MathBot. Un élève vient de résoudre un exercice.
Génère UN exercice similaire (même notion, difficulté légèrement différente).
Réponds UNIQUEMENT en JSON valide, sans markdown, sans explication :
{
  "enonce": "L'énoncé de l'exercice en français",
  "niveau": "Facile | Moyen | Difficile",
  "notion": "La notion mathématique travaillée"
}"""


async def solve_problem(problem: str) -> str:
    """
    Envoie le problème à Claude et retourne l'explication complète.
    Gère les erreurs proprement.
    """
    if not ANTHROPIC_API_KEY:
        return (
            "⚠️ Le bot n'est pas encore configuré avec une clé API.\n"
            "Contacte l'administrateur !"
        )

    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    payload = {
        "model": MODEL,
        "max_tokens": 1500,
        "system": SYSTEM_PROMPT,
        "messages": [
            {"role": "user", "content": f"Aide-moi à résoudre cet exercice :\n\n{problem}"}
        ],
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(API_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["content"][0]["text"]

    except httpx.TimeoutException:
        logger.warning("Timeout lors de l'appel à l'API Anthropic")
        return "⏰ Le serveur met trop de temps à répondre. Réessaie dans quelques secondes !"

    except httpx.HTTPStatusError as e:
        logger.error(f"Erreur HTTP API : {e.response.status_code}")
        if e.response.status_code == 401:
            return "🔑 Clé API invalide. Contacte l'administrateur."
        return "❌ Une erreur est survenue. Réessaie plus tard."

    except Exception as e:
        logger.exception(f"Erreur inattendue : {e}")
        return "❌ Oups, quelque chose s'est mal passé. Réessaie !"


async def generate_similar_exercise(original_problem: str) -> dict | None:
    """
    Génère un exercice similaire pour le mode entraînement.
    Retourne un dict {enonce, niveau, notion} ou None si erreur.
    """
    if not ANTHROPIC_API_KEY:
        return None

    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    payload = {
        "model": MODEL,
        "max_tokens": 400,
        "system": TRAINING_SYSTEM_PROMPT,
        "messages": [
            {
                "role": "user",
                "content": f"Exercice original : {original_problem}\nGénère un exercice similaire.",
            }
        ],
    }

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(API_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            text = data["content"][0]["text"].strip()
            # Nettoyage au cas où il y aurait des backticks
            text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)

    except Exception as e:
        logger.warning(f"Erreur génération exercice similaire : {e}")
        return None
