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
### =============
## Code de couleurs recommandé :

- bleu en cours (#004BC7) : En cours
- vert (#52E600) : Terminé
- rouge (#FA2500) : Bloqué/Problème

exemple :

```md
<span style="background-color:#couleur">Votre texte</span>
```

| Fonctionnalités | Avancement | Commentaire | Conclusion | Points | Attribution |
|----------------|------------|-------------|------------|------------|------------|
| help | <span style="background-color:#FA2500">🔴 Non commencé</span> | x | x | 0.5 pt | Nagib |

### =============

## Suivi des Fonctionnalités

### Fonctionnalités Client (10 points)

| Fonctionnalités | Avancement | Commentaire | Conclusion | Points | Attribution |
|----------------|------------|-------------|------------|------------|------------|
| help | <span style="background-color:#FA2500">🔴 Non commencé</span> | x | x | 0.5 pt | |
| download | <span style="background-color:#FA2500">🔴 Non commencé</span> | x | x | 1 pt | |
| upload | <span style="background-color:#FA2500">🔴 Non commencé</span> | x | x | 1 pt | |
| shell | <span style="background-color:#FA2500">🔴 Non commencé</span> | x | x | 0.5 pt | |
| ipconfig | <span style="background-color:#FA2500">🔴 Non commencé</span> | x | x | 0.5 pt | |
| screenshot | <span style="background-color:#FA2500">🔴 Non commencé</span> | x | x | 1 pt | |
| search | <span style="background-color:#FA2500">🔴 Non commencé</span> | x | x | 0.5 pt | |
| hashdump | <span style="background-color:#FA2500">🔴 Non commencé</span> | x | x | 1 pt | |
| keylogger | <span style="background-color:#FA2500">🔴 Non commencé</span> | x | x | 1 pt | |
| webcam_snapshot | <span style="background-color:#FA2500">🔴 Non commencé</span> | x | x | 1 pt | |
| webcam_stream | <span style="background-color:#FA2500">🔴 Non commencé</span> | x | x | 1 pt | |
| record_audio | <span style="background-color:#FA2500">🔴 Non commencé</span> | x | x | 1 pt | |

### Fonctionnalités Serveur (6 points)

| Fonctionnalités | Avancement | Commentaire | Conclusion | Points | Attribution |
|----------------|------------|-------------|------------|------------|------------|
| Interface interactive | <span style="background-color:#FA2500">🔴 Non commencé</span> | x | x | 1 pt | |
| Écoute TCP | <span style="background-color:#FA2500">🔴 Non commencé</span> | x | x | 1 pt | |
| Multi-agents | <span style="background-color:#FA2500">🔴 Non commencé</span> | x | x | 2 pts | |
| Gestion connexions | <span style="background-color:#FA2500">🔴 Non commencé</span> | x | x | 1 pt | |
| Gestion erreurs/help | <span style="background-color:#FA2500">🔴 Non commencé</span> | x | x | 1 pt | |

### Exigences Techniques

| Fonctionnalités | Avancement | Commentaire | Conclusion | Points | Attribution |
|----------------|------------|-------------|------------|------------|------------|
| Socket TCP chiffrée | <span style="background-color:#FA2500">🔴 Non commencé</span> | x | x | Obligatoire | |
| Compatibilité Windows/Linux | <span style="background-color:#FA2500">🔴 Non commencé</span> | x | x | Obligatoire | |
| Poetry | <span style="background-color:#FA2500">🔴 Non commencé</span> | x | x | -1 pt | |
| Pre-commit | <span style="background-color:#FA2500">🔴 Non commencé</span> | x | x | -1 pt | |
| Logger | <span style="background-color:#FA2500">🔴 Non commencé</span> | x | x | -1 pt | |
| Tests unitaires (pytest) | <span style="background-color:#FA2500">🔴 Non commencé</span> | x | x | -2 pts | |
| Git | <span style="background-color:#FA2500">🔴 Non commencé</span> | x | x | -1 pt | |
| Vidéo démo | <span style="background-color:#FA2500">🔴 Non commencé</span> | x | x | -2 pts | |

### Bonus Facultatifs

| Fonctionnalités | Avancement | Commentaire | Conclusion | Points | Attribution |
|----------------|------------|-------------|------------|------------|------------|
| Interface web | <span style="background-color:#FA2500">🔴 Non commencé</span> | x | x | +1 pt | |
| Interface graphique | <span style="background-color:#FA2500">🔴 Non commencé</span> | x | x | +1 pt | |
| Docker | <span style="background-color:#FA2500">🔴 Non commencé</span> | x | x | +1 pt | |
| Contournement antivirus | <span style="background-color:#FA2500">🔴 Non commencé</span> | x | x | +2 pts | |
| Fonctionnalités custom | <span style="background-color:#FA2500">🔴 Non commencé</span> | x | x | +1 pt | |

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
