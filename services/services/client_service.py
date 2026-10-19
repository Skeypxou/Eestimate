
import json
import os
import tempfile
import uuid
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "storage"
CLIENTS_FILE = DATA_DIR / "clients.json"


def charger_clients():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not CLIENTS_FILE.exists():
        return []

    try:
        with CLIENTS_FILE.open("r", encoding="utf-8") as f:
            clients = json.load(f)
    except (json.JSONDecodeError, OSError) as erreur:
        raise RuntimeError(
            "Lecture impossible de clients.json. Vérifie le fichier."
        ) from erreur

    if not isinstance(clients, list):
        raise ValueError("clients.json doit contenir une liste.")

    return clients


def sauvegarder_clients(clients):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    temporaire = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=DATA_DIR,
            suffix=".tmp",
            delete=False,
        ) as f:
            temporaire = f.name
            json.dump(clients, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())

        os.replace(temporaire, CLIENTS_FILE)

    except OSError as erreur:
        if temporaire and os.path.exists(temporaire):
            try:
                os.remove(temporaire)
            except OSError:
                pass
        raise RuntimeError("Enregistrement des clients impossible.") from erreur


def ajouter_client(nom, telephone="", email="", adresse=""):
    nom = nom.strip()
    if not nom:
        raise ValueError("Le nom du client est obligatoire.")

    clients = charger_clients()

    client = {
        "id": str(uuid.uuid4()),
        "nom": nom,
        "telephone": telephone.strip(),
        "email": email.strip(),
        "adresse": adresse.strip(),
        "date_creation": date.today().isoformat(),
        "actif": True,
    }

    clients.append(client)
    sauvegarder_clients(clients)
    return client


def modifier_client(
    client_id, nom, telephone="", email="", adresse=""
):
    nom = nom.strip()
    if not nom:
        raise ValueError("Le nom du client est obligatoire.")

    clients = charger_clients()

    for client in clients:
        if client.get("id") == client_id:
            client.update({
                "nom": nom,
                "telephone": telephone.strip(),
                "email": email.strip(),
                "adresse": adresse.strip(),
            })
            sauvegarder_clients(clients)
            return client

    raise ValueError("Client introuvable.")


def rechercher_clients(texte=""):
    clients = charger_clients()
    texte = texte.strip().casefold()

    if not texte:
        return clients

    return [
        client for client in clients
        if any(
            texte in str(client.get(champ, "")).casefold()
            for champ in ("nom", "telephone", "email")
        )
    ]
