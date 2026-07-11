# Retake
Project retake

# Signed Local Message Exchange (CLI)

Client/serveur TCP local qui échange des messages texte signés numériquement (RSA + SHA-256) et détecte toute altération après signature.

**Protocole custom : SFX** (`[HEADER][TYPE][LENGTH][PAYLOAD]`).

---

## 1. Prérequis et dépendances

- Python 3.10+
- Librairie [`cryptography`](https://cryptography.io/) (RSA, SHA-256, sérialisation PEM)

### Installation

```bash
pip install cryptography
```

Ou avec `uv` :

```bash
uv add cryptography
```

Aucune autre dépendance externe. Le projet n'utilise que la bibliothèque standard Python (`socket`, `struct`, `json`, `pathlib`, `datetime`) en plus de `cryptography`.

---

## 2. Structure du projet

```
signed_exchange_project/
├── server.py                    # serveur TCP (127.0.0.1:6000)
├── client.py                    # client CLI
├── constant.py                  # client CLI
│
├── protocol/                    # framing SFX bas niveau
│   ├── frame.py                 # construction/lecture des trames, recv_exact, MAX_PAYLOAD
│   ├── encoder.py               # construction des payloads JSON par commande,  helpers Base64 (to_b64 / from_b64)
│   └── decoder.py               # validation des payloads reçus (requêtes et réponses)
│
├── crypto/                      # cryptographie (RSA 2048 + SHA-256)
│   ├── rsa_keys.py              # génération / sérialisation / chargement des clés PEM
│   ├── signature.py             # sign_message() / verify_signature()
│   └── hashing.py               # SHA-256 autonome (affichage uniquement, pas la signature)
│ 
│
├── storage/                      # persistance disque
│   └── object_store.py           # store / list / get / tamper des signed objects
│
├── keys/                         # clés RSA générées par /generate_keys <username>
│   ├── <username>_private.pem    # ne quitte JAMAIS le client
│   └── <username>_public.pem
│
└── server_storage/               # objets signés stockés côté serveur
    └── object_N/
        ├── metadata.json         # object_id, object_name, sender, hash_algorithm, timestamp, tampered
        ├── content.bin            # corps du message (modifiable indépendamment)
        ├── signature.bin          # signature RSA brute
        └── public_key.pem         # clé publique de l'expéditeur
```

---

## 3. Démarrage

### Lancer le serveur

```bash
python server.py
```

Sortie attendue :

```
Server started on 127.0.0.1:6000
Waiting for clients...
```

### Lancer le client (dans un autre terminal)

```bash
python client.py
```

Sortie attendue :

```
Client started (not connected yet).
Type /help to see available commands, or /connect to connect to the server.
```

Le client ne se connecte pas automatiquement : il faut taper `/connect` explicitement.

---

## 4. Commandes CLI disponibles

| Commande | Portée | Description |
|---|---|---|
| `/help` | client | Affiche l'aide |
| `/connect` | réseau | Ouvre la connexion TCP vers le serveur |
| `/disconnect` | réseau | Ferme la connexion TCP |
| `/generate_keys <username>` | client | Génère une paire de clés RSA 2048 bits dans `keys/` |
| `/send_text <username> <object_name> <message>` | réseau | Signe le message avec la clé privée de `<username>` et l'envoie au serveur |
| `/list` | réseau | Liste tous les objets stockés côté serveur |
| `/get <object_id>` | réseau | Récupère un objet et affiche son contenu |
| `/verify <object_id>` | réseau | Récupère un objet **frais** depuis le serveur et vérifie sa signature côté client |
| `/verify_all` | réseau | Récupère la liste, puis chaque objet, et vérifie chacun individuellement |
| `/tamper <object_id>` | réseau | Demande au serveur d'altérer intentionnellement `content.bin` de cet objet |
| `/exit` | client | Ferme la connexion et quitte |
| `/clear` | client | Efface l'écran |

---

## 5. Workflow de signature (rappel des responsabilités)

**Signature — toujours côté client :**
1. Le corps du message est encodé en UTF-8 (`str.encode("utf-8")`).
2. Signature en **un seul appel** de la librairie : `private_key.sign(message_bytes, padding.PKCS1v15(), hashes.SHA256())`. La librairie calcule l'empreinte SHA-256 en interne — on ne hash jamais manuellement avant de signer (ça produirait un double hachage).
3. Les champs binaires (message, signature, clé publique PEM) sont encodés en Base64 pour pouvoir voyager dans le JSON du protocole SFX.

**Vérification — toujours côté client, jamais côté serveur :**
1. Le client va chercher l'objet **actuel** sur le serveur (`GET_OBJECT`), jamais une copie en cache.
2. Les champs sont décodés depuis Base64.
3. `public_key.verify(signature, message, padding.PKCS1v15(), hashes.SHA256())` — retourne `VALID` si la vérification réussit, `INVALID` si `InvalidSignature` est levée.

**Le serveur ne signe jamais, ne vérifie jamais, et ne voit jamais de clé privée** (section 3.1 du cahier des charges).

### Paramètres cryptographiques imposés

| Paramètre | Valeur |
|---|---|
| Algorithme | RSA |
| Taille de clé | 2048 bits |
| Padding | PKCS1 v1.5 |
| Hash | SHA-256 |

### Pourquoi `cryptography` plutôt qu'une implémentation manuelle

La bibliothèque `cryptography` (pyca) est utilisée pour toute la partie obligatoire du projet car :
- elle implémente RSA-PKCS1v1.5 de façon éprouvée et constante en temps (résistante aux attaques par canal auxiliaire);
- elle gère correctement la sérialisation PEM standard (`-----BEGIN PUBLIC KEY-----`), interopérable avec n'importe quel autre outil crypto ;
- le cahier des charges impose explicitement l'usage d'une "vraie" librairie cryptographique pour le chemin obligatoire (section 4.2).

---

## 6. Protocole SFX

```
[HEADER][TYPE][LENGTH][PAYLOAD]
   3B      1B     4B     N Bytes
```

- **HEADER** : toujours `b"SFX"`. Toute trame dont les 3 premiers octets diffèrent est rejetée.
- **TYPE** : 1 octet ASCII identifiant la commande.

  | TYPE | Commande |
  |---|---|
  | `S` | SEND_SIGNED_TEXT (soumission d'un objet signé) |
  | `L` | LIST_OBJECTS |
  | `G` | GET_OBJECT |
  | `T` | TAMPER_OBJECT |
  | `O` | réponse succès |
  | `E` | réponse erreur |

- **LENGTH** : taille du PAYLOAD, entier non signé 4 octets big-endian (`struct.pack(">I", n)` / `struct.unpack(">I", b)`).
- **PAYLOAD** : exactement `LENGTH` octets de texte UTF-8 contenant un objet JSON.

### Lecture fiable des trames

Un seul appel à `socket.recv()` peut renvoyer moins d'octets que demandé — c'est un comportement TCP normal, pas une erreur. `protocol/frame.py` boucle donc (`recv_exact`) jusqu'à avoir lu exactement les 8 octets fixes, puis exactement `LENGTH` octets de payload, quel que soit le découpage réseau.

### Protection contre les trames malformées

Avant de lire le payload, `LENGTH` est comparé à `MAX_PAYLOAD = 1_048_576` (1 MiB). Toute trame annonçant un payload plus grand est rejetée **avant** toute tentative de lecture, pour éviter qu'un `LENGTH` mensonger ne déclenche une allocation mémoire excessive.

---

## 7. Stockage persistant côté serveur

Chaque objet signé est stocké dans `server_storage/object_N/` avec 4 fichiers séparés :

- `metadata.json` — `object_id`, `object_name`, `sender`, `hash_algorithm`, `timestamp`, `tampered` (flag informatif uniquement, jamais utilisé pour la vérification cryptographique elle-même)
- `content.bin` — le corps du message, modifiable indépendamment
- `signature.bin` — la signature RSA brute, jamais modifiée après création
- `public_key.pem` — la clé publique de l'expéditeur, jamais modifiée après création

À chaque lecture (`/list`, `/get`, `/verify`), le contenu de `content.bin` est relu **directement depuis le disque** — jamais depuis une valeur mise en cache dans `metadata.json` — pour garantir que la vérification porte toujours sur l'état actuel des données.

---

## 8. Démonstration : envoi, vérification, altération

```
/connect
/generate_keys alice
/send_text alice note1 Hello server, this is a signed message
/list
/get 1
/verify 1
```
→ `/verify 1` doit afficher **VALID**.

```
/tamper 1
/get 1
/verify 1
```
→ `content.bin` a été modifié côté serveur (suffixe ajouté), mais `signature.bin` et `public_key.pem` restent inchangés. La signature ne correspond plus au contenu actuel → `/verify 1` doit afficher **INVALID**.

```
/verify_all
```
→ Récupère la liste complète, va chercher chaque objet, et affiche un résumé VALID/INVALID pour chacun.

---

```

→ Doit afficher **INVALID**, car `verify_signature()` recalcule la vérification sur les octets **actuels** de `content.bin`, jamais sur une copie en mémoire ou en cache.

---
