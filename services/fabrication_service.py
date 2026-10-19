
import json
import os
import tempfile
import uuid
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "storage"
FABRICATION_FILE = DATA_DIR / "fabrications.json"


def charger_fabrications():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not FABRICATION_FILE.exists():
        return []

    try:
        with FABRICATION_FILE.open("r", encoding="utf-8") as fichier:
            fabrications = json.load(fichier)
    except (json.JSONDecodeError, OSError) as erreur:
        raise RuntimeError(
            "Impossible de lire storage/fabrications.json."
        ) from erreur

    if not isinstance(fabrications, list):
        raise ValueError("fabrications.json doit contenir une liste.")

    return fabrications


def sauvegarder_fabrications(fabrications):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    temporaire = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=DATA_DIR,
            suffix=".tmp",
            delete=False,
        ) as fichier:
            temporaire = fichier.name
            json.dump(
                fabrications,
                fichier,
                ensure_ascii=False,
                indent=2,
            )
            fichier.flush()
            os.fsync(fichier.fileno())

        os.replace(temporaire, FABRICATION_FILE)

    except OSError as erreur:
        if temporaire and os.path.exists(temporaire):
            try:
                os.remove(temporaire)
            except OSError:
                pass

        raise RuntimeError(
            "Impossible d'enregistrer les fabrications."
        ) from erreur


def creer_fabrication(client_id, description, dimensions, quantite=1):
    description = description.strip()

    if not client_id:
        raise ValueError("Sélectionne un client.")

    if not description:
        raise ValueError("La description est obligatoire.")

    if int(quantite) < 1:
        raise ValueError("La quantité doit être au moins égale à 1.")

    fabrication = {
        "id": str(uuid.uuid4()),
        "numero": f"FAB-{date.today():%Y%m%d}-{uuid.uuid4().hex[:6].upper()}",
        "date": date.today().isoformat(),
        "client_id": str(client_id),
        "description": description,
        "dimensions": dimensions,
        "quantite": int(quantite),
        "statut": "En attente",
    }

    fabrications = charger_fabrications()
    fabrications.append(fabrication)
    sauvegarder_fabrications(fabrications)

    return fabrication
