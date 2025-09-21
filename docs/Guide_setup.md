# Guide Setup Projet RAT - Étapes Réalisées

## Vue d'ensemble
Ce guide documente toutes les étapes que nous avons suivies pour mettre en place l'environnement de développement du projet RAT, en commençant simple et en ajoutant progressivement les outils nécessaires.

## Étape 1 : Structure de base

### Création des dossiers
```bash
mkdir src
mkdir tests
mkdir guide  # Ce dossier pour la documentation
```

### Premier fichier Python
**Fichier :** `src/main.py`
```python
def hello_world():
    return "Hello World - RAT Project!"

if __name__ == "__main__":
    print(hello_world())
```

**Test :** `python src/main.py`

## Étape 2 : Configuration du projet

### Fichier pyproject.toml
**Fichier :** `pyproject.toml`
```toml
[project]
name = "rat-project"
version = "0.1.0"
description = "Remote Administration Tool"
authors = [

]
readme = "README.md"
requires-python = ">=3.13"
dependencies = []

[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"
```

## Étape 3 : Tests unitaires

### Installation de pytest
```bash
pip install pytest
```

### Premier test
**Fichier :** `tests/__init__.py` (vide)

**Fichier :** `tests/test_main.py`
```python
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import hello_world


def test_hello_world():
    result = hello_world()
    assert "Hello World" in result
    assert "RAT Project" in result
```

### Lancement des tests
```bash
pytest tests/ -v
```

**Résultat attendu :**
```
tests/test_main.py::test_hello_world PASSED
```

## Étape 4 : Pre-commit et formatage

### Installation des outils
```bash
pip install pre-commit black flake8
```

### Configuration pre-commit
**Fichier :** `.pre-commit-config.yaml`
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 25.9.0
    hooks:
      - id: black
        language_version: python3.13

  - repo: https://github.com/pycqa/flake8
    rev: 7.3.0
    hooks:
      - id: flake8
        args: [--max-line-length=88]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
```

### Configuration flake8
**Fichier :** `.flake8`
```ini
[flake8]
max-line-length = 88
per-file-ignores =
    tests/*:E402
```

**Pourquoi E402 ?** Dans les tests, on doit modifier `sys.path` avant d'importer nos modules, ce qui viole la règle E402 (imports en début de fichier).

### Installation pre-commit
```bash
git init
pre-commit install
```

### Test pre-commit
```bash
pre-commit run --all-files
```

## Étape 5 : Résolution des problèmes

### Problèmes rencontrés et solutions

#### 1. Erreur de build Poetry
**Problème :** `ModuleOrPackageNotFoundError: No file/folder found for package rat-project`

**Cause :** Poetry ne trouvait pas de structure de package Python

**Solution :** Créer d'abord les fichiers/dossiers avant d'installer

#### 2. Warnings pre-commit hooks
**Problème :** `uses deprecated stage names (commit, push)`

**Solution :** Mise à jour avec `pre-commit autoupdate`

#### 3. Erreurs de formatage
**Problème :** Pre-commit échouait à cause de :
- Espaces en fin de ligne
- Pas de ligne vide en fin de fichier
- Imports mal placés dans les tests

**Solution :**
- Laisser pre-commit corriger automatiquement
- Configurer `.flake8` pour ignorer E402 dans les tests
- Re-commiter après les corrections automatiques

## Structure finale du projet

```
projet-rat/
├── src/
│   ├── main.py              # Point d'entrée principal
├── tests/
│   ├── __init__.py          # Package tests
│   └── test_main.py         # Tests de base
├── guide/
│   └── Guide_setup.md       # Ce guide
│   └── Guide_poetry.md      # Guide pour Poetry
├── .flake8                  # Configuration flake8
├── .pre-commit-config.yaml  # Configuration pre-commit
├── .gitignore              # Fichiers à ignorer
├── pyproject.toml          # Configuration projet
└── README.md               # Documentation principale
```

## Commandes utiles

### Développement quotidien
```bash
# Lancer les tests
pytest tests/ -v

# Formatter le code manuellement
black src/ tests/

# Vérifier la qualité du code
flake8 src/ tests/

# Lancer pre-commit sur tous les fichiers
pre-commit run --all-files
```

### Git workflow
```bash
# Ajouter les fichiers
git add .

# Commiter (pre-commit se lance automatiquement)
git commit -m "Votre message"

# Si pre-commit fait des corrections, re-ajouter et re-commiter
git add .
git commit -m "Fix formatting"
```

## Prochaines étapes

### Ajout des dépendances du RAT
```bash
pip install cryptography psutil pynput pillow opencv-python pyaudio
```

### Bonnes pratiques appliquées
- Structure modulaire du code
- Tests automatisés
- Formatage cohérent (Black)
- Qualité de code vérifiée (Flake8)
- Versioning avec Git
- Documentation claire

## Lessons learned

1. **Commencer simple** : Créer d'abord un "Hello World" plutôt qu'une structure complexe
2. **Étapes progressives** : Ajouter un outil à la fois et bien le configurer
3. **Pre-commit est exigeant** : Il corrige automatiquement mais peut nécessiter plusieurs commits
4. **Configuration importante** : Les fichiers `.flake8`, `.pre-commit-config.yaml` sont cruciaux
5. **Tests dès le début** : Même simples, ils valident que la structure fonctionne
