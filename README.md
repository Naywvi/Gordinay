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

| Fonctionnalités | Avancement | Commentaire | Conclusion |
|----------------|------------|-------------|------------|
| help | 🔴 Non commencé | Afficher la liste des commandes (0.5 pt) | À implémenter en premier |
| download | 🔴 Non commencé | Récupération fichiers victime → serveur (1 pt) | Priorité élevée |
| upload | 🔴 Non commencé | Envoi fichiers serveur → victime (1 pt) | Priorité élevée |
| shell | 🔴 Non commencé | Shell interactif bash/cmd (0.5 pt) | Fonctionnalité de base |
| ipconfig | 🔴 Non commencé | Configuration réseau victime (0.5 pt) | Simple à implémenter |
| screenshot | 🔴 Non commencé | Capture d'écran victime (1 pt) | Nécessite bibliothèque image |
| search | 🔴 Non commencé | Recherche fichier sur victime (0.5 pt) | Utiliser os.walk |
| hashdump | 🔴 Non commencé | Base SAM/shadow selon OS (1 pt) | Fonctionnalité avancée |
| keylogger | 🔴 Non commencé | Enregistrement frappes clavier (1 pt) | Complexité élevée |
| webcam_snapshot | 🔴 Non commencé | Photo via webcam (1 pt) | Nécessite OpenCV |
| webcam_stream | 🔴 Non commencé | Flux vidéo webcam en direct (1 pt) | Très complexe |
| record_audio | 🔴 Non commencé | Enregistrement audio micro (1 pt) | Gestion des codecs |

### Fonctionnalités Serveur (6 points)

| Fonctionnalités | Avancement | Commentaire | Conclusion |
|----------------|------------|-------------|------------|
| Interface interactive | 🔴 Non commencé | Interface CLI avec prompt (1 pt) | Base du projet |
| Écoute TCP | 🔴 Non commencé | Socket serveur sur port TCP (1 pt) | Prérequis fondamental |
| Multi-agents | 🔴 Non commencé | Gestion plusieurs clients (2 pts) | Threading nécessaire |
| Gestion connexions | 🔴 Non commencé | Connect/disconnect agents (1 pt) | Gestion des sessions |
| Gestion erreurs/help | 🔴 Non commencé | Erreurs + help serveur (1 pt) | UX important |

### Exigences Techniques

| Fonctionnalités | Avancement | Commentaire | Conclusion |
|----------------|------------|-------------|------------|
| Socket TCP chiffrée | 🔴 Non commencé | SSL/TLS obligatoire | Sécurité critique |
| Compatibilité Windows/Linux | 🔴 Non commencé | Code multi-plateforme | Tests sur 2 OS |
| Poetry | 🔴 Non commencé | Gestion dépendances | -1 pt si absent |
| Pre-commit | 🔴 Non commencé | Formatage code | -1 pt si absent |
| Logger | 🔴 Non commencé | Pas de print() | -1 pt si print utilisé |
| Tests unitaires (pytest) | 🔴 Non commencé | Couverture de code | -2 pts si absent |
| Git | 🔴 Non commencé | Versioning | -1 pt si absent |
| Vidéo démo | 🔴 Non commencé | Preuve fonctionnement | -2 pts si absente |

### Bonus Facultatifs (+1 point chacun)

| Fonctionnalités | Avancement | Commentaire | Conclusion |
|----------------|------------|-------------|------------|
| Interface web | 🔴 Non commencé | Alternative au CLI | Bonus intéressant |
| Interface graphique | 🔴 Non commencé | GUI desktop | Exclusif avec web |
| Docker | 🔴 Non commencé | Containerisation | Facilite déploiement |
| Contournement antivirus | 🔴 Non commencé | Techniques d'évasion (+2 pts) | Très avancé |
| Fonctionnalités custom | 🔴 Non commencé | Créativité | À définir |

## Légende des Avancements
- ✅ **Terminé** : Fonctionnalité complète et testée
- 🟡 **En cours** : Développement en cours
- 🔴 **Non commencé** : Pas encore démarré

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

<!-- ## Structure Projet Recommandée
```
projet-rat/
├── src/
│   ├── serveur/
│   ├── client/
│   └── common/
├── tests/
├── docs/
├── pyproject.toml
├── README.md
└── .pre-commit-config.yaml
``` -->