
import json
import os
import tempfile
import uuid
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "storage"
DEVIS_FILE = DATA_DIR / "devis.json"


def charger_devis():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not DEVIS_FILE.exists():
        return []

    try:
        with DEVIS_FILE.open("r", encoding="utf-8") as fichier:
            devis = json.load(fichier)
    except (json.JSONDecodeError, OSError) as erreur:
        raise RuntimeError(
            "Impossible de lire storage/devis.json."
        ) from erreur

    if not isinstance(devis, list):
        raise ValueError("devis.json doit contenir une liste.")

    return devis


def sauvegarder_devis(devis):
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
            json.dump(devis, fichier, ensure_ascii=False, indent=2)
            fichier.flush()
            os.fsync(fichier.fileno())

        os.replace(temporaire, DEVIS_FILE)

    except OSError as erreur:
        if temporaire and os.path.exists(temporaire):
            try:
                os.remove(temporaire)
            except OSError:
                pass

        raise RuntimeError(
            "Impossible d'enregistrer les devis."
        ) from erreur


def creer_devis(client_id, lignes, notes=""):
    if not client_id:
        raise ValueError("Sélectionne un client.")

    if not lignes:
        raise ValueError("Ajoute au moins un article au devis.")

    total = 0.0

    for ligne in lignes:
        try:
            quantite = float(ligne["quantite"])
            prix = float(ligne["prix_unitaire"])
        except (KeyError, TypeError, ValueError) as erreur:
            raise ValueError(
                "Vérifie les quantités et les prix."
            ) from erreur

        if quantite <= 0 or prix < 0:
            raise ValueError(
                "La quantité doit être positive et le prix non négatif."
            )

        total += quantite * prix

    devis = charger_devis()

    nouveau_devis = {
        "id": str(uuid.uuid4()),
        "numero": f"DEV-{date.today():%Y%m%d}-{len(devis) + 1:04d}",
        "date": date.today().isoformat(),
        "client_id": str(client_id),
        "lignes": lignes,
        "notes": notes.strip(),
        "total": round(total, 2),
        "statut": "En attente",
    }

    devis.append(nouveau_devis)
    sauvegarder_devis(devis)

    return nouveau_devis
