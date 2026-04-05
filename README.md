# 🤖 MathBot — Bot Telegram d'aide aux maths

Bot pédagogique Telegram pour les élèves de collège et lycée en France.
Il explique les exercices **étape par étape** en français simple — il ne donne jamais juste la réponse.

---

## ✨ Fonctionnalités

| Fonctionnalité | Détail |
|---|---|
| 🧮 Résolution étape par étape | Algèbre, géométrie, fonctions, stats... |
| 🇫🇷 Français simple (A2-B1) | Ton amical, adapté aux ados |
| 🏋️ Mode entraînement | Génère un exercice similaire |
| 📊 Système freemium | 3 questions/jour en gratuit |
| 💾 Base de données SQLite | Suivi des utilisateurs |
| 🚀 Déployable sur Railway | Prêt en 5 minutes |

---

## 📁 Structure du projet

```
mathbot/
├── bot.py                  # Point d'entrée principal
├── requirements.txt        # Dépendances Python
├── .env.example            # Modèle de configuration
├── Procfile                # Pour Railway / Heroku
├── railway.toml            # Config Railway
├── .gitignore
├── handlers/
│   ├── __init__.py
│   ├── commands.py         # /start, /help, /limit
│   ├── math_handler.py     # Traitement des questions
│   └── training.py         # Mode entraînement
└── utils/
    ├── __init__.py
    ├── database.py         # SQLite — users & compteurs
    └── solver.py           # Appel API Anthropic (Claude)
```

---

## 🚀 Installation locale

### 1. Prérequis
- Python 3.11+
- Un bot Telegram (créé via [@BotFather](https://t.me/BotFather))
- Une clé API Anthropic ([console.anthropic.com](https://console.anthropic.com))

### 2. Cloner et installer

```bash
# Cloner le projet
git clone https://github.com/ton-user/mathbot.git
cd mathbot

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate        # Linux/Mac
# OU
venv\Scripts\activate           # Windows

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Configurer les variables d'environnement

```bash
cp .env.example .env
# Ouvre .env et remplis :
# TELEGRAM_TOKEN=...
# ANTHROPIC_API_KEY=...
```

### 4. Lancer le bot

```bash
python bot.py
```

---

## 🚂 Déploiement sur Railway

Railway est la façon la plus simple de garder le bot actif 24h/24.

### Étapes :

1. **Crée un compte** sur [railway.app](https://railway.app)

2. **Nouveau projet** → "Deploy from GitHub repo"
   - Connecte ton compte GitHub
   - Sélectionne le repo de MathBot

3. **Variables d'environnement** (dans Settings → Variables) :
   ```
   TELEGRAM_TOKEN     = ton_token_telegram
   ANTHROPIC_API_KEY  = ta_cle_anthropic
   FREE_DAILY_LIMIT   = 3
   ```

4. **Volume persistant** (pour la base de données) :
   - Dans Railway → ton service → "Add Volume"
   - Mount path : `/app/data`
   - Mets à jour `DB_PATH=data/users.db` dans les variables

5. **Déploie** — Railway build et lance automatiquement !

> 💡 **Astuce** : Railway offre 5$ de crédits gratuits par mois, largement suffisant pour un bot personnel.

---

## ⚙️ Configuration avancée

### Changer la limite gratuite
Dans `.env` ou les variables Railway :
```
FREE_DAILY_LIMIT=5
```

### Passer un utilisateur en Premium
Dans la base SQLite :
```sql
UPDATE users SET is_premium = 1 WHERE user_id = 123456789;
```

Ou ajoute une commande admin dans `handlers/commands.py` (ex: `/setpremium`).

---

## 📌 Commandes du bot

| Commande | Description |
|---|---|
| `/start` | Message de bienvenue |
| `/help` | Aide et liste des sujets couverts |
| `/limit` | Questions restantes aujourd'hui |

---

## 🔒 Éthique & pédagogie

MathBot ne donne **jamais** une réponse sans explication.
Le prompt système force Claude à toujours :
- Reformuler le problème
- Rappeler la règle ou formule utilisée
- Expliquer chaque étape
- Donner une astuce mnémotechnique

L'objectif est d'**aider les élèves à comprendre**, pas à tricher.

---

## 🛠️ Dépendances

| Package | Version | Rôle |
|---|---|---|
| `python-telegram-bot` | 21.6 | SDK Telegram |
| `httpx` | 0.27.2 | Appels API async |
| `python-dotenv` | 1.0.1 | Gestion `.env` |

---

## 📜 Licence

Projet open-source — libre de l'utiliser et de le modifier pour ton usage pédagogique.
