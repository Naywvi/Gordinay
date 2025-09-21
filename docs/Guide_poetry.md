# Guide Setup Projet RAT avec Poetry

## 1. Installation de Poetry

### Windows
```bash
# Via PowerShell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -

# Ou via pip
pip install poetry
```

### Linux/macOS
```bash
# Via curl
curl -sSL https://install.python-poetry.org | python3 -

# Ou via pip
pip install poetry
```

Redémarrez votre terminal après installation.

## 2. Initialisation du projet

```bash
# Créer le dossier du projet
mkdir projet-rat
cd projet-rat

# Initialiser Poetry (répondez aux questions)
poetry init

# Ou créer directement avec une structure de base
poetry new . --name rat-project
```

## 3. Configuration Poetry

Modifiez le fichier `pyproject.toml` généré :

```toml
[tool.poetry]
name = "rat-project"
version = "0.1.0"
description = "Remote Administration Tool en Python"
authors = ["Votre Nom <email@example.com>", "Membre 2 <email2@example.com>"]
readme = "README.md"
packages = [{include = "src"}]

[tool.poetry.dependencies]
python = "^3.9"
cryptography = "^41.0.0"  # Pour le chiffrement SSL/TLS
pynput = "^1.7.6"         # Pour le keylogger
pillow = "^10.0.0"        # Pour les screenshots
opencv-python = "^4.8.0"  # Pour webcam
pyaudio = "^0.2.11"       # Pour l'audio
psutil = "^5.9.0"         # Pour les infos système

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-cov = "^4.1.0"
black = "^23.7.0"
flake8 = "^6.0.0"
pre-commit = "^3.3.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
addopts = "--cov=src --cov-report=html --cov-report=term-missing"

[tool.black]
line-length = 88
target-version = ['py39']
```

## 4. Arborescence du projet

```
projet-rat/
├── src/
│   ├── __init__.py
│   ├── common/
│   │   ├── __init__.py
│   │   ├── crypto.py          # Fonctions de chiffrement
│   │   ├── protocol.py        # Protocole de communication
│   │   └── utils.py           # Utilitaires communs
│   ├── server/
│   │   ├── __init__.py
│   │   ├── main.py            # Point d'entrée serveur
│   │   ├── server.py          # Classe serveur principal
│   │   ├── session_manager.py # Gestion des sessions clients
│   │   └── cli.py             # Interface ligne de commande
│   └── client/
│       ├── __init__.py
│       ├── main.py            # Point d'entrée client
│       ├── client.py          # Classe client principal
│       ├── commands/
│       │   ├── __init__.py
│       │   ├── file_ops.py    # download, upload, search
│       │   ├── system_info.py # ipconfig, shell
│       │   ├── media.py       # screenshot, webcam, audio
│       │   ├── security.py    # hashdump
│       │   └── keylogger.py   # keylogger
│       └── utils/
│           ├── __init__.py
│           └── platform_utils.py # Détection OS
├── tests/
│   ├── __init__.py
│   ├── test_server/
│   │   ├── __init__.py
│   │   ├── test_server.py
│   │   └── test_session_manager.py
│   ├── test_client/
│   │   ├── __init__.py
│   │   ├── test_client.py
│   │   └── test_commands/
│   │       ├── __init__.py
│   │       ├── test_file_ops.py
│   │       └── test_system_info.py
│   └── test_common/
│       ├── __init__.py
│       ├── test_crypto.py
│       └── test_protocol.py
├── docs/
├── scripts/
│   ├── run_server.py
│   └── run_client.py
├── .pre-commit-config.yaml
├── .gitignore
├── pyproject.toml
├── README.md
└── demo_video/
```

## 5. Commandes Poetry essentielles

```bash
# Installer les dépendances
poetry install

# Activer l'environnement virtuel
poetry shell

# Ajouter une dépendance
poetry add requests

# Ajouter une dépendance de développement
poetry add --group dev pytest

# Exécuter une commande dans l'environnement
poetry run python src/server/main.py

# Mettre à jour les dépendances
poetry update

# Voir les dépendances
poetry show

# Créer le requirements.txt (si besoin)
poetry export -f requirements.txt --output requirements.txt
```

## 6. Configuration Pre-commit

Créez `.pre-commit-config.yaml` :

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
        language_version: python3.9

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

Installer pre-commit :
```bash
poetry run pre-commit install
```

## 7. Exemples de tests de base

### `tests/test_common/test_crypto.py`
```python
import pytest
from src.common.crypto import encrypt_message, decrypt_message

class TestCrypto:
    def test_encrypt_decrypt(self):
        """Test basique de chiffrement/déchiffrement"""
        message = "Hello World"
        key = "ma_cle_secrete"

        encrypted = encrypt_message(message, key)
        decrypted = decrypt_message(encrypted, key)

        assert decrypted == message
        assert encrypted != message

    def test_encrypt_empty_message(self):
        """Test avec message vide"""
        message = ""
        key = "ma_cle_secrete"

        encrypted = encrypt_message(message, key)
        decrypted = decrypt_message(encrypted, key)

        assert decrypted == message
```

### `tests/test_server/test_server.py`
```python
import pytest
import socket
import threading
from src.server.server import RATServer

class TestRATServer:
    def setup_method(self):
        """Setup avant chaque test"""
        self.server = RATServer(host="127.0.0.1", port=8888)

    def test_server_initialization(self):
        """Test d'initialisation du serveur"""
        assert self.server.host == "127.0.0.1"
        assert self.server.port == 8888
        assert self.server.clients == []

    def test_server_start_stop(self):
        """Test de démarrage/arrêt du serveur"""
        # Démarrer en thread pour ne pas bloquer
        server_thread = threading.Thread(target=self.server.start)
        server_thread.daemon = True
        server_thread.start()

        # Vérifier que le serveur écoute
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            result = sock.connect_ex(("127.0.0.1", 8888))
            assert result == 0  # Connexion réussie

        self.server.stop()
```

### `tests/test_client/test_commands/test_file_ops.py`
```python
import pytest
import tempfile
import os
from src.client.commands.file_ops import FileOperations

class TestFileOperations:
    def setup_method(self):
        """Setup avant chaque test"""
        self.file_ops = FileOperations()
        self.temp_dir = tempfile.mkdtemp()

    def test_file_search(self):
        """Test de recherche de fichier"""
        # Créer un fichier temporaire
        test_file = os.path.join(self.temp_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("test content")

        # Chercher le fichier
        results = self.file_ops.search_file("test.txt", self.temp_dir)

        assert len(results) == 1
        assert test_file in results[0]

    def test_file_upload_download(self):
        """Test d'upload/download de fichier"""
        # Créer un fichier source
        source_file = os.path.join(self.temp_dir, "source.txt")
        with open(source_file, "w") as f:
            f.write("test upload content")

        # Simuler upload puis download
        # TODO: Implémenter les vraies fonctions
        assert os.path.exists(source_file)
```

## 8. Exécution des tests

```bash
# Exécuter tous les tests
poetry run pytest

# Exécuter avec couverture de code
poetry run pytest --cov=src

# Exécuter un test spécifique
poetry run pytest tests/test_common/test_crypto.py

# Exécuter avec verbose
poetry run pytest -v

# Générer rapport HTML de couverture
poetry run pytest --cov=src --cov-report=html
```

## 9. Structure des fichiers principaux

### `src/server/main.py`
```python
#!/usr/bin/env python3
import logging
from server import RATServer

def main():
    logging.basicConfig(level=logging.INFO)
    server = RATServer(host="0.0.0.0", port=8888)

    try:
        server.start()
    except KeyboardInterrupt:
        logging.info("Arrêt du serveur...")
        server.stop()

if __name__ == "__main__":
    main()
```

### `src/client/main.py`
```python
#!/usr/bin/env python3
import logging
from client import RATClient

def main():
    logging.basicConfig(level=logging.INFO)
    client = RATClient(server_host="127.0.0.1", server_port=8888)

    try:
        client.connect()
        client.run()
    except Exception as e:
        logging.error(f"Erreur client: {e}")

if __name__ == "__main__":
    main()
```

## 10. Commandes de démarrage

```bash
# Installer tout
poetry install

# Activer l'environnement
poetry shell

# Formatter le code
poetry run black src/ tests/

# Lancer les tests
poetry run pytest

# Démarrer le serveur
poetry run python src/server/main.py

# Démarrer le client (autre terminal)
poetry run python src/client/main.py
```

Voilà ! Vous avez maintenant une base solide pour démarrer votre projet RAT avec Poetry, une arborescence propre et des tests configurés. 🚀
