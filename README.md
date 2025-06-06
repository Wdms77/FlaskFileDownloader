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
```bash
git clone https://github.com/Wdms77/flask-file-downloader.git
cd flask-file-downloader
```

4. Construire et lancer le conteneur
```bash
docker build -t flask-file-downloader . && \
docker run -it --rm -p 5000:5000 \
  -v $(pwd)/files:/data \
  flask-file-downloader
```
OR
```bash
make
make run
```

3. Accéder à l’application
```bash
👉 http://localhost:5000
```

# 🔍 Endpoints disponibles
```bash
GET	/			Interface web HTML
GET	/api/files		Liste JSON des fichiers avec métadonnées
GET	/download/<nom>		Téléchargement direct du fichier
GET	/events			Flux SSE pour les mises à jour en direct
GET 	/metrics 		Métriques Prometheus
```

# 📦 Exemple d’appel API
```bash
# Récupérer la liste des fichiers présents
curl http://127.0.0.1:5000/api/files | jq '.[].name'

# Récupérer un fichier
wget http://127.0.0.1:5000/download/helloworld.txt
```

# 📊 Vérifier les métriques Prometheus
```bash
curl http://localhost:5000/metrics
```

# 🧪 Exécuter les tests
```bash
docker build -t flask-file-downloader .
docker run --rm -d --name ffd_test -p 5000:5000 -v $(PWD)/files:/data flask-file-downloader
docker exec ffd_test pytest tests -v
docker stop ffd_test
```
OR
```bash
make test
```

# 📁 Arborescence minimale du projet
```bash
flask-file-downloader/
│
├── app/                    # Code source Flask
│   ├── static/ 			# Fichiers JS / CSS
│	├── templates/          # HTML
│	├── __init__.py
│   ├── routes.py
│   └── watcher.py
│   
├── run.py
├── requirements.txt        # Dépendances
├── Dockerfile              # Dockerfile
├── Makefile
├── tests/                  # Tests Pytest
│
└── files/                  # 📂 Dossier monté en tant que volume
```

# 🧠 Bonus UI/UX
	• Icônes de tri interactifs (⬆️/⬇️) visibles sur les colonnes cliquables
	• Barre de recherche réactive avec mise à jour immédiate du tableau
	• Boutons SHA-256 avec copie au clic
