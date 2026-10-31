# CIAT PILOTAGE
Tableau de bord décisionnel intelligent du CIAT — projet pédagogique.

## Prérequis
- Python 3.12+
- Windows 10/11 ou Linux

## Installation Windows PowerShell
```powershell
cd CIAT_PILOTAGE
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item backend\.env.example backend\.env
cd backend
python manage.py makemigrations projects
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver
```
Ouvrir http://127.0.0.1:8000/

## Assistant IA
Par défaut, l'assistant fonctionne en mode démonstration à partir des statistiques calculées en base.
Pour activer OpenAI, renseigner `OPENAI_API_KEY` dans `backend/.env` et installer la dépendance déjà listée dans requirements.

## Données
La commande `python manage.py seed_demo` crée des données entièrement fictives, identifiées comme telles, et peut être relancée sans créer de doublons.

## Rôles
Créer les utilisateurs depuis l'administration Django puis leur attribuer un groupe :
- Administrateur : accès complet (superutilisateur ou groupe Administrateur)
- Coordonnateur : gestion des données
- Analyste : consultation des statistiques et rapports

## Tests
```powershell
python manage.py test
```

## Remarques
Ce projet est une base applicative pédagogique fonctionnelle à compléter et valider avec les données officielles du CIAT avant toute utilisation réelle. Les chiffres de démonstration ne décrivent pas les activités réelles du CIAT.


## Déploiement Render (accès public pour le jury)

Le dépôt contient désormais un fichier `render.yaml` et un script `build.sh` pour déployer Django avec Gunicorn, WhiteNoise et PostgreSQL.

1. Publier le contenu du dossier `CIAT_PILOTAGE` dans un dépôt GitHub. Ne jamais envoyer un fichier `.env` réel ni une base SQLite contenant des données privées.
2. Dans Render, créer un **New Blueprint** et connecter le dépôt GitHub contenant `render.yaml`.
3. Lors de la synchronisation, renseigner `CIAT_ADMIN_PASSWORD` avec un mot de passe fort. Le compte de démonstration prévu est `jury`; son mot de passe doit être transmis séparément au jury.
4. Laisser Render créer le service web et la base PostgreSQL définis dans `render.yaml`.
5. Suivre les journaux de déploiement. Le script installe les dépendances, applique les migrations, collecte les fichiers statiques, charge les données fictives et crée/met à jour le compte utilisateur du jury.
6. À la fin, ouvrir l’URL HTTPS `*.onrender.com` fournie par Render et tester la connexion, les projets, le tableau de bord, les filtres et les exports.

Render renseigne automatiquement `RENDER_EXTERNAL_HOSTNAME` et `RENDER_EXTERNAL_URL`; les paramètres Django les utilisent pour les hôtes autorisés et les origines CSRF.

### Limites du forfait gratuit

Le service web gratuit peut se mettre en veille après une période sans trafic. La base PostgreSQL gratuite Render expire après 30 jours. Ce montage convient à une démonstration temporaire ; pour conserver les données au-delà, prévoir une offre payante ou exporter/sauvegarder les données avant expiration. Vérifier les conditions actuelles dans la documentation Render avant de déployer.
