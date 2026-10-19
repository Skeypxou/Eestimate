
import json
import os
import tempfile
import uuid
from datetime import date
from pathlib import Path


# Dossier de stockage du projet
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "storage"
CLIENTS_FILE = DATA_DIR / "clients.json"


def charger_clients():
    """Charge les clients depuis le fichier JSON."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not CLIENTS_FILE.exists():
        return []

    try:
        with CLIENTS_FILE.open("r", encoding="utf-8") as fichier:
            donnees = json.load(fichier)
    except json.JSONDecodeError as erreur:
        raise ValueError(
            "Le fichier clients.json est invalide. "
            "Vérifie ou restaure une sauvegarde avant de continuer."
        ) from erreur
    except OSError as erreur:
        raise RuntimeError(
            "Impossible de lire le fichier des clients."
        ) from erreur

    if not isinstance(donnees, list):
        raise ValueError(
            "Le fichier clients.json doit contenir une liste de clients."
        )

    return donnees


def sauvegarder_clients(clients):
    """Enregistre les clients en limitant le risque de fichier incomplet."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    fichier_temporaire = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=DATA_DIR,
            suffix=".tmp",
            delete=False
        ) as fichier:
            fichier_temporaire = fichier.name
            json.dump(
                clients,
                fichier,
                ensure_ascii=False,
                indent=2
            )
            fichier.flush()
            os.fsync(fichier.fileno())

        os.replace(fichier_temporaire, CLIENTS_FILE)

    except OSError as erreur:
        if fichier_temporaire and os.path.exists(fichier_temporaire):
            os.remove(fichier_temporaire)

        raise RuntimeError(
            "Impossible d'enregistrer les clients."
        ) from erreur


def ajouter_client(nom, telephone="", email="", adresse=""):
    """Crée un client et renvoie la fiche enregistrée."""
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
        "actif": True
    }

    clients.append(client)
    sauvegarder_clients(clients)

    return client


def modifier_client(
    client_id,
    nom,
    telephone="",
    email="",
    adresse=""
):
    """Modifie une fiche client existante."""
    nom = nom.strip()

    if not nom:
        raise ValueError("Le nom du client est obligatoire.")

    clients = charger_clients()

    for client in clients:
        if client.get("id") == client_id:
            client["nom"] = nom
            client["telephone"] = telephone.strip()
            client["email"] = email.strip()
            client["adresse"] = adresse.strip()

            sauvegarder_clients(clients)
            return client

    raise ValueError("Client introuvable.")


def rechercher_clients(texte=""):
    """Recherche par nom, téléphone ou adresse e-mail."""
    clients = charger_clients()
    texte = texte.strip().casefold()

    if not texte:
        return clients

    resultats = []

    for client in clients:
        champs = [
            client.get("nom", ""),
            client.get("telephone", ""),
            client.get("email", "")
        ]

        if any(texte in valeur.casefold() for valeur in champs):
            resultats.append(client)

    return resultats
