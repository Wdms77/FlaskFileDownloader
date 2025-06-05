# 📦 Flask File Downloader (Dockerisé)

Application web légère développée avec Flask, permettant de **lister**, **télécharger** et **vérifier l’intégrité (SHA-256)** des fichiers présents dans un dossier monté via Docker.

L’interface est responsive, dotée de **tri dynamique**, **recherche instantanée**, et d’un **rafraîchissement automatique** à chaque ajout, suppression ou modification de fichier.


## 🚀 Fonctionnalités

- 🗂️ Affichage dynamique des fichiers disponibles dans un dossier
- 🔍 Barre de recherche instantanée
- ↕️ Tri dynamique (nom, taille, date) avec indicateurs visuels
- 📥 Téléchargement direct depuis l’interface web
- 🔄 Rafraîchissement automatique via Server-Sent Events (SSE)
- 🛡️ Hash SHA-256 de chaque fichier avec copie rapide
- 📊 Monitoring Prometheus exposé via /metrics
- 🧪 Tests automatisés (Pytest)
- 🐳 Application conteneurisée avec Docker


## ⚙️ Prérequis

- [Docker](https://docs.docker.com/get-docker/) installé sur votre machine
- Un dossier local contenant les fichiers à exposer


## 🛠️ Installation & Lancement

1. Cloner le dépôt

git clone https://github.com/ton-utilisateur/flask-file-downloader.git
	cd flask-file-downloader

2. Construire et lancer le conteneur

	docker build -t flask-file-downloader . && \
	docker run -it --rm -p 5000:5000 \
  -v $(pwd)/logs:/logs \
  -v $(pwd)/files:/data \
  flask-file-downloader

OR

	make
	make run

3. Accéder à l’application

	👉 http://localhost:5000


# 🔍 Endpoints disponibles

Méthode	Route	Description
GET	/	Interface web HTML
GET	/api/files	Liste JSON des fichiers avec métadonnées
GET	/download/<nom>	Téléchargement direct du fichier
GET	/events	Flux SSE pour les mises à jour en direct
GET /metrics Métriques Prometheus


# 📦 Exemple d’appel API

	curl http://127.0.0.1:5000/api/files | jq '.[].name'


# 📊 Vérifier les métriques Prometheus

	curl http://localhost:5000/metrics


# 🧪 Exécuter les tests

	docker run -it --rm \
	  -v $(pwd):/app \
	  -w /app \
	  python:3.11 \
	  sh -c "pip install -r requirements.txt && pytest"


# 📁 Arborescence minimale du projet
	
	flask-file-downloader/
	│
	├── app/                    # Code source Flask
	│   ├── __init__.py
	│   ├── routes.py
	│   └── watcher.py
	│
	├── static/                 # Fichiers JS / CSS
	├── templates/              # HTML
	├── Dockerfile              # Dockerfile
	├── requirements.txt        # Dépendances
	├── tests/                  # Tests Pytest
	│
	├── files/                  # 📂 Dossier monté en tant que volume
	└── logs/                   # 📂 Logs persistants


# 🧠 Bonus UI/UX
	• Icônes de tri interactifs (⬆️/⬇️) visibles sur les colonnes cliquables
	• Barre de recherche réactive avec mise à jour immédiate du tableau
	• Boutons SHA-256 avec aperçu au survol et copie au clic
