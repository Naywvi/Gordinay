# Projet Final - RAT (Remote Administration Tool)

## Description
Système de RAT (Remote Administration Tool) développé en Python composé d'un serveur et d'un client communicant via socket TCP chiffrée et sécurisée.

**Date limite** : 31 décembre 2025 à 23h59
**Groupe** : 2 personnes uniquement

## Installation
```bash
# Cloner le repository
git clone [url-du-repo]
cd projet-rat

# Installation avec Poetry
poetry install

# Activation de l'environnement
poetry shell
```

## Utilisation
```bash
# Lancement du serveur
python serveur.py

# Lancement du client
python client.py
```

## Suivi des Fonctionnalités

### Fonctionnalités Client (10 points)

| Fonctionnalités | Avancement | Commentaire | Conclusion | Points | Attribution |
|----------------|------------|-------------|------------|------------|------------|
| help | 🔴 Non commencé | x | x | 0.5 pt | |
| download | 🔴 Non commencé | x | x | 1 pt | |
| upload | 🔴 Non commencé | x | x | 1 pt | |
| shell | 🔴 Non commencé | x | x | 0.5 pt | |
| ipconfig | 🔴 Non commencé | x | x | 0.5 pt | |
| screenshot | 🔴 Non commencé | x | x | 1 pt | |
| search | 🔴 Non commencé | x | x | 0.5 pt | |
| hashdump | 🔴 Non commencé | x | x | 1 pt | |
| keylogger | 🔴 Non commencé | x | x | 1 pt | |
| webcam_snapshot | 🔴 Non commencé | x | x | 1 pt | |
| webcam_stream | 🔴 Non commencé | x | x | 1 pt | |
| record_audio | 🔴 Non commencé | x | x | 1 pt | |

### Fonctionnalités Serveur (6 points)

| Fonctionnalités | Avancement | Commentaire | Conclusion | Points | Attribution |
|----------------|------------|-------------|------------|------------|------------|
| Interface interactive | 🔴 Non commencé | x | x | 1 pt | |
| Écoute TCP | 🔴 Non commencé | x | x | 1 pt | |
| Multi-agents | 🔴 Non commencé | x | x | 2 pts | |
| Gestion connexions | 🔴 Non commencé | x | x | 1 pt | |
| Gestion erreurs/help | 🔴 Non commencé | x | x | 1 pt | |

### Exigences Techniques

| Fonctionnalités | Avancement | Commentaire | Conclusion | Points | Attribution |
|----------------|------------|-------------|------------|------------|------------|
| Socket TCP chiffrée | 🔴 Non commencé | x | x | Obligatoire | |
| Compatibilité Windows/Linux | 🔴 Non commencé | x | x | Obligatoire | |
| Poetry | 🔴 Non commencé | x | x | -1 pt | |
| Pre-commit | 🔴 Non commencé | x | x | -1 pt | |
| Logger | 🔴 Non commencé | x | x | -1 pt | |
| Tests unitaires (pytest) | 🔴 Non commencé | x | x | -2 pts | |
| Git | 🔴 Non commencé | x | x | -1 pt | |
| Vidéo démo | 🔴 Non commencé | x | x | -2 pts | |

### Bonus Facultatifs

| Fonctionnalités | Avancement | Commentaire | Conclusion | Points | Attribution |
|----------------|------------|-------------|------------|------------|------------|
| Interface web | 🔴 Non commencé | x | x | +1 pt | |
| Interface graphique | 🔴 Non commencé | x | x | +1 pt | |
| Docker | 🔴 Non commencé | x | x | +1 pt | |
| Contournement antivirus | 🔴 Non commencé | x | x | +2 pts | |
| Fonctionnalités custom | 🔴 Non commencé | x | x | +1 pt | |

## Architecture Technique
- **Langage** : Python exclusivement
- **Communication** : Socket TCP avec chiffrement SSL/TLS
- **Gestion dépendances** : Poetry
- **Tests** : pytest
- **Formatage** : pre-commit hooks
- **Logging** : Module logging Python

## Points d'Attention
⚠️ **Malus à éviter** :
- Absence de chiffrement : -2 points
- Pas de vidéo : -2 points
- Pas de tests unitaires : -2 points
- Utilisation de print au lieu de logger : -1 point
