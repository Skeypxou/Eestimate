
import json
import os
import tempfile
import uuid
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "storage"
PRODUITS_FILE = DATA_DIR / "produits.json"


def charger_produits():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not PRODUITS_FILE.exists():
        return []

    try:
        with PRODUITS_FILE.open("r", encoding="utf-8") as fichier:
            produits = json.load(fichier)
    except (json.JSONDecodeError, OSError) as erreur:
        raise RuntimeError(
            "Impossible de lire storage/produits.json."
        ) from erreur

    if not isinstance(produits, list):
        raise ValueError("produits.json doit contenir une liste.")

    return produits


def sauvegarder_produits(produits):
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
            json.dump(produits, fichier, ensure_ascii=False, indent=2)
            fichier.flush()
            os.fsync(fichier.fileno())

        os.replace(temporaire, PRODUITS_FILE)

    except OSError as erreur:
        if temporaire and os.path.exists(temporaire):
            try:
                os.remove(temporaire)
            except OSError:
                pass

        raise RuntimeError(
            "Impossible d'enregistrer les produits."
        ) from erreur


def ajouter_produit(nom, categorie, reference, prix, stock=0):
    nom = nom.strip()
    categorie = categorie.strip()
    reference = reference.strip()

    if not nom:
        raise ValueError("Le nom du produit est obligatoire.")

    if not categorie:
        raise ValueError("La catégorie est obligatoire.")

    if prix < 0:
        raise ValueError("Le prix ne peut pas être négatif.")

    if stock < 0:
        raise ValueError("Le stock ne peut pas être négatif.")

    produits = charger_produits()

    if reference and any(
        p.get("reference", "").casefold() == reference.casefold()
        for p in produits
    ):
        raise ValueError("Cette référence existe déjà.")

    produit = {
        "id": str(uuid.uuid4()),
        "nom": nom,
        "categorie": categorie,
        "reference": reference,
        "prix": round(float(prix), 2),
        "stock": int(stock),
        "actif": True,
    }

    produits.append(produit)
    sauvegarder_produits(produits)

    return produit
