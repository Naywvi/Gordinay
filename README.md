# Projet Final - RAT (Remote Administration Tool)

## Description

Système de RAT (Remote Administration Tool) développé en Python composé d'un serveur et d'un client communicant via socket TCP chiffrée et sécurisée.

**Date limite** : 31 décembre 2025 à 23h59
**Groupe** : 2 personnes uniquement

## Installation

```bash
# Cloner le repository
git clone https://github.com/Naywvi/Gordinay.git
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

| Fonctionnalités | Avancement | Commentaire                                                                                                                                                                                                                            | Conclusion  | Points | Attribution |
| --------------- | ---------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- | ------ | ----------- |
| help            | 🟢 Terminé | Système d'aide complet avec catégories (Client Management, Configuration, Capture, Stream, Audio, System, File Management, Advanced). Help général + help détaillé par commande. Affichage des profils de configuration disponibles    | Fonctionnel | 0.5 pt |             |
| download        | 🟢 Terminé | Téléchargement de fichiers du client vers le serveur avec chunking (64KB), barre de progression, vérification de taille, sauvegarde automatique dans data/clients/{id}/downloads/. Support de tous types de fichiers                   | Fonctionnel | 1 pt   |             |
| upload          | 🟢 Terminé | Upload de fichiers du serveur vers le client avec chunking, vérification d'existence, création de répertoires automatique, support chemins absolus et relatifs                                                                         | Fonctionnel | 1 pt   |             |
| shell           | 🟢 Terminé | Exécution de commandes shell uniques avec timeout, capture stdout/stderr, encodage correct (cp850 Windows), gestion des erreurs, affichage formaté des résultats                                                                       | Fonctionnel | 0.5 pt |             |
| ipconfig        | 🟢 Terminé | Classe NetworkInfo complète avec monitoring continu, détection des changements, collecte IP locale/publique/MAC/DNS/gateway, sauvegarde JSON, tracking des modifications réseau                                                        | Fonctionnel | 0.5 pt |             |
| screenshot      | 🟢 Terminé | Classe Screenshot avec capture périodique, détection de changements optionnelle (hash-based), compression JPEG configurable (85%), métadonnées avec fenêtre active, résolution, timestamp, contrôle start/stop à distance              | Fonctionnel | 1 pt   |             |
| search          | 🟢 Terminé | Recherche de fichiers récursive avec patterns (wildcards \*), filtrage par extensions multiples, limite de résultats configurable (100 par défaut), affichage formaté avec taille et chemin complet                                    | Fonctionnel | 0.5 pt |             |
| hashdump        | 🟢 Terminé | Extraction hashes Windows via 2 méthodes : SAM (registry) et LSASS (mimikatz-style). Parsing format SAM, extraction LM/NTLM hashes, sauvegarde hashcat-compatible, gestion privilèges admin, support Windows uniquement                | Fonctionnel | 1 pt   |             |
| keylogger       | 🟢 Terminé | Classe KeyLogger avec enregistrement par phrases, capture fenêtre active via ctypes, timer d'inactivité (5s), détection touches spéciales, sauvegarde JSON structurée, contrôle start/stop à distance, timestamps précis               | Fonctionnel | 1 pt   |             |
| webcam_snapshot | 🟢 Terminé | Classe Webcam avec capture périodique (30s), détection de mouvement optionnelle (OpenCV), métadonnées JSON complètes, contexte fenêtre active, index caméra configurable, contrôle start/stop, gestion multi-caméras                   | Fonctionnel | 1 pt   |             |
| webcam_stream   | 🟢 Terminé | Streaming vidéo temps réel avec affichage OpenCV côté serveur, FPS configurable (5-30), résolution ajustable (640x480 à 1920x1080), qualité JPEG paramétrable, détection mouvement optionnelle, overlay infos (client, FPS, timestamp) | Fonctionnel | 1 pt   |             |
| record_audio    | 🟢 Terminé | Enregistrement audio avec sounddevice, format WAV 44.1kHz, durée configurable (10s), mode continu avec intervalles (60s), détection de devices, métadonnées JSON, Voice Activity Detection (VAD) avancée, contrôle à distance          | Fonctionnel | 1 pt   |             |

### Fonctionnalités Serveur (6 points)

| Fonctionnalités       | Avancement | Commentaire                                                                                                                                                                                                                                     | Conclusion  | Points | Attribution |
| --------------------- | ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- | ------ | ----------- |
| Interface interactive | 🟢 Terminé | CLI complet avec cmd module Python, prompt personnalisé (RAT-Server (client_id)), auto-complétion, historique commandes, 40+ commandes disponibles, help contextuel, affichage formaté avec couleurs et tableaux, gestion erreurs user-friendly | Fonctionnel | 1 pt   |             |
| Écoute TCP            | 🟢 Terminé | Serveur socket TCP multi-threadé sur 0.0.0.0:4444, SSL/TLS avec certificats auto-signés, handshake client avec identification (hostname, OS, features), heartbeat ping/pong (30s), gestion propre des déconnexions, logging complet             | Fonctionnel | 1 pt   |             |
| Multi-agents          | 🟢 Terminé | Support clients illimités simultanés, thread dédié par client, stockage dict {client_id: ClientHandler}, commandes list/select/deselect/info, broadcast à tous les clients, isolation complète des données par client, stats temps réel         | Fonctionnel | 2 pts  |             |
| Gestion connexions    | 🟢 Terminé | Auto-reconnexion client (délai 5s), détection timeout, cleanup automatique des threads, fermeture gracieuse avec **stop**, gestion états (connected/disconnected), remove client on disconnect, thread-safe operations                          | Fonctionnel | 1 pt   |             |
| Gestion erreurs/help  | 🟢 Terminé | Try-except sur toutes opérations critiques, messages d'erreur explicites, validation paramètres commandes, help général + détaillé par commande, suggestions en cas de commande inconnue, gestion erreurs réseau, logging exceptions complètes  | Fonctionnel | 1 pt   |             |

### Exigences Techniques

| Fonctionnalités             | Avancement | Commentaire                                                                                                                                                                                                          | Conclusion       | Points      | Attribution |
| --------------------------- | ---------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- | ----------- | ----------- |
| Socket TCP chiffrée         | 🟢 Terminé | SSL/TLS avec ssl.wrap_socket(), certificats server.crt/server.key, chiffrement AES-256, vérification optionnelle certificats, communication JSON sur socket chiffrée, gestion erreurs SSL                            | Fonctionnel (OK) | Obligatoire |             |
| Compatibilité Windows/Linux | 🟢 Terminé | Détection OS avec sys.platform, chemins Path() cross-platform, encodage cp850 (Windows) / utf-8 (Linux), commandes shell adaptatives (cmd.exe vs bash), ctypes pour features Windows spécifiques, tests sur les 2 OS | Fonctionnel (OK) | Obligatoire |             |
| Poetry                      | 🟢 Terminé | Fonctionnel (OK) configurés                                                                                                                                                                                          | Fonctionnel (OK) | -1 pt       |             |
| Pre-commit                  | 🟢 Terminé | Fonctionnel (OK) configurés                                                                                                                                                                                          | Fonctionnel (OK) | -1 pt       |             |
| Logger                      | 🟢 Terminé | Fonctionnel (OK) configurés utilisation de logger                                                                                                                                                                    | Fonctionnel (OK) | -0.5 pt     |             |
| Tests unitaires (pytest)    | 🔴 Absent  | Pas de tests unitaires pytest implémentés                                                                                                                                                                            | Non fait         | -2 pts      |             |
| Git                         | 🟢 Terminé | Repository Git avec commits réguliers, branches, .gitignore configuré, versioning du code                                                                                                                            | Fonctionnel (OK) | -0 pt       |             |
| Vidéo démo                  | 🔴 Absent  | Vidéo de démonstration non fournie                                                                                                                                                                                   | À faire          | -2 pts      |             |

### Bonus Facultatifs

| Fonctionnalités         | Avancement | Commentaire                                                                                                                                                                                                                                       | Conclusion  | Points | Attribution |
| ----------------------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- | ------ | ----------- |
| Interface web           | 🔴 Absent  | Non implémenté                                                                                                                                                                                                                                    | Non fait    | 0 pt   |             |
| Interface graphique     | 🔴 Absent  | Non implémenté                                                                                                                                                                                                                                    | Non fait    | 0 pt   |             |
| Docker                  | 🔴 Absent  | Non implémenté                                                                                                                                                                                                                                    | Non fait    | 0 pt   |             |
| Contournement antivirus | 🔴 Absent  | Non implémenté                                                                                                                                                                                                                                    | Non fait    | 0 pt   |             |
| Fonctionnalités custom  | 🟢 Terminé | **Configuration à distance** : système complet de gestion config avec profiles (stealth, performance, balanced, minimal), modification paramètres en temps réel, affichage config, 10+ paramètres configurables (FPS, qualité, intervalles, etc.) | Fonctionnel | +1 pt  |             |
|                         | 🟢 Terminé | **Reverse Shell interactif** : shell persistant avec mode interactif, support cmd.exe et bash, threads lecture stdout/stderr séparés, encodage adaptatif, sortie temps réel, commandes exit/quit pour sortir                                      | Fonctionnel | +1 pt  |             |
|                         | 🟢 Terminé | **Stream webcam temps réel** : streaming vidéo avec fenêtre OpenCV, contrôle FPS/qualité/résolution en direct, overlay informations, détection mouvement, sauvegarde frames optionnelle, stats streaming                                          | Fonctionnel | +1 pt  |             |

## Architecture Technique

```
.env
src/
├── assets
│   └── gordinay.txt
├── main.py
├── __app__
│   ├── client_app
│   │   ├── features
│   │   │   ├── audioRecorder
│   │   │   │   └── main.py
│   │   │   ├── commandHandler
│   │   │   │   └── main.py
│   │   │   ├── fileManager
│   │   │   │   └── main.py
│   │   │   ├── hashDump
│   │   │   │   └── main.py
│   │   │   ├── keyLogger
│   │   │   │   └── main.py
│   │   │   ├── networkInfo
│   │   │   │   └── main.py
│   │   │   ├── record
│   │   │   │   └── main.py
│   │   │   ├── reverseShell
│   │   │   │   └── main.py
│   │   │   ├── screenshot
│   │   │   │   └── main.py
│   │   │   ├── shell
│   │   │   │   └── main.py
│   │   │   ├── socketClient
│   │   │   │   └── main.py
│   │   │   ├── webcam_snapshot
│   │   │   │   └── main.py
│   │   │   └── webcam_stream
│   │   │       └── main.py
│   │   ├── main.py
│   │   ├── utils
│   │   │   └── clientError
│   │   │       └── main.py
│   │   └── __conf__
│   │       └── main.py
│   └── server_app
│       ├── server.py
│       ├── server_app.py
│       ├── server_cert.pem
│       ├── server_cli.py
│       ├── server_key.pem
│       ├── server_socket.py
│       └── tools
│           └── stream_viewer.py
├── __conf__
│   └── main.py
└── __utils__
    ├── asciiArt.py
    ├── clientError.py
    ├── coloredFormatter.py
    ├── log.py
    └── terminal.py
```

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
