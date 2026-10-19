
import streamlit as st
import pandas as pd

from services.client_service import (
    charger_clients,
    ajouter_client,
    modifier_client,
    rechercher_clients,
)
from services.devis_service import charger_devis, creer_devis
from services.produit_service import (
    charger_produits,
    ajouter_produit,
)
from services.fabrication_service import (
    charger_fabrications,
    creer_fabrication,
)

st.set_page_config(
    page_title="Atelier PVC Pro",
    page_icon="🏭",
    layout="wide",
)

st.title("🏭 Atelier PVC Pro")
st.caption("Gestion de votre atelier de menuiserie PVC")

PAGES = [
    "Tableau de bord",
    "Clients",
    "Devis",
    "Catalogue PVC",
    "Vitrages",
    "Accessoires",
    "Fabrication",
    "Paramètres",
]

if "page" not in st.session_state:
    st.session_state.page = "Tableau de bord"

with st.sidebar:
    st.title("🏭 Atelier PVC")
    st.divider()

    for nom_page in PAGES:
        if st.button(nom_page, use_container_width=True):
            st.session_state.page = nom_page

page = st.session_state.page


def afficher_tableau(donnees):
    if donnees:
        st.dataframe(
            pd.DataFrame(donnees),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Aucune donnée enregistrée.")


if page == "Tableau de bord":
    st.header("Tableau de bord")

    try:
        clients = charger_clients()
        devis = charger_devis()
        produits = charger_produits()
        fabrications = charger_fabrications()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Clients", len(clients))
        c2.metric("Devis", len(devis))
        c3.metric("Produits", len(produits))
        c4.metric("Fabrications", len(fabrications))

        st.subheader("Derniers devis")
        afficher_tableau([
            {
                "Numéro": d["numero"],
                "Date": d["date"],
                "Total": f"{d['total']:.2f}",
                "Statut": d["statut"],
            }
            for d in devis[-5:][::-1]
        ])

    except Exception as erreur:
        st.error(str(erreur))


elif page == "Clients":
    st.header("👥 Gestion des clients")
    tab1, tab2, tab3 = st.tabs(
        ["Ajouter", "Liste et recherche", "Modifier"]
    )

    with tab1:
        with st.form("ajouter_client", clear_on_submit=True):
            nom = st.text_input("Nom complet *")
            telephone = st.text_input("Téléphone")
            email = st.text_input("E-mail")
            adresse = st.text_area("Adresse")
            envoyer = st.form_submit_button("Enregistrer")

            if envoyer:
                try:
                    ajouter_client(nom, telephone, email, adresse)
                    st.success("Client enregistré.")
                    st.rerun()
                except Exception as erreur:
                    st.error(str(erreur))

    with tab2:
        recherche = st.text_input("Rechercher un client")
        try:
            clients = rechercher_clients(recherche)
            afficher_tableau([
                {
                    "Nom": c.get("nom", ""),
                    "Téléphone": c.get("telephone", ""),
                    "E-mail": c.get("email", ""),
                    "Adresse": c.get("adresse", ""),
                }
                for c in clients
            ])
        except Exception as erreur:
            st.error(str(erreur))

    with tab3:
        try:
            clients = charger_clients()
            if clients:
                choix = {
                    f"{c['nom']} — {c['id'][:8]}": c
                    for c in clients
                }
                selection = st.selectbox(
                    "Client à modifier", list(choix.keys())
                )
                client = choix[selection]

                with st.form("modifier_client"):
                    nom = st.text_input(
                        "Nom", value=client.get("nom", "")
                    )
                    telephone = st.text_input(
                        "Téléphone",
                        value=client.get("telephone", ""),
                    )
                    email = st.text_input(
                        "E-mail", value=client.get("email", "")
                    )
                    adresse = st.text_area(
                        "Adresse", value=client.get("adresse", "")
                    )
                    envoyer = st.form_submit_button("Enregistrer")

                    if envoyer:
                        try:
                            modifier_client(
                                client["id"], nom, telephone,
                                email, adresse
                            )
                            st.success("Client modifié.")
                            st.rerun()
                        except Exception as erreur:
                            st.error(str(erreur))
            else:
                st.info("Aucun client à modifier.")
        except Exception as erreur:
            st.error(str(erreur))


elif page == "Catalogue PVC":
    st.header("🪟 Catalogue des produits")
    st.caption("Profils PVC, vitrages et accessoires")

    with st.form("ajouter_produit", clear_on_submit=True):
        nom = st.text_input("Nom du produit *")
        categorie = st.selectbox(
            "Catégorie",
            ["Profil PVC", "Vitrage", "Accessoire"],
        )
        reference = st.text_input("Référence")
        prix = st.number_input("Prix unitaire", min_value=0.0, step=100.0)
        stock = st.number_input(
            "Stock disponible", min_value=0, step=1
        )
        envoyer = st.form_submit_button("Ajouter le produit")

        if envoyer:
            try:
                ajouter_produit(
                    nom, categorie, reference, prix, stock
                )
                st.success("Produit enregistré.")
                st.rerun()
            except Exception as erreur:
                st.error(str(erreur))

    try:
        produits = charger_produits()
        afficher_tableau([
            {
                "Nom": p["nom"],
                "Catégorie": p["categorie"],
                "Référence": p["reference"],
                "Prix": p["prix"],
                "Stock": p["stock"],
            }
            for p in produits
        ])
    except Exception as erreur:
        st.error(str(erreur))


elif page == "Vitrages":
    st.header("🔲 Vitrages")
    produits = charger_produits()
    vitrages = [
        p for p in produits
        if p.get("categorie") == "Vitrage"
    ]
    afficher_tableau(vitrages)
    st.info("Pour ajouter un vitrage, utilise le Catalogue PVC.")


elif page == "Accessoires":
    st.header("🔩 Accessoires")
    produits = charger_produits()
    accessoires = [
        p for p in produits
        if p.get("categorie") == "Accessoire"
    ]
    afficher_tableau(accessoires)
    st.info("Pour ajouter un accessoire, utilise le Catalogue PVC.")


elif page == "Devis":
    st.header("📄 Gestion des devis")

    try:
        clients = charger_clients()

        if not clients:
            st.warning("Ajoute d'abord un client.")
        else:
            choix = {
                f"{c['nom']} — {c['id'][:8]}": c
                for c in clients
            }

            with st.form("creer_devis"):
                client_label = st.selectbox(
                    "Client", list(choix.keys())
                )
                description = st.text_input("Description de l'article")
                quantite = st.number_input(
                    "Quantité", min_value=1, step=1
                )
                prix = st.number_input(
                    "Prix unitaire", min_value=0.0, step=100.0
                )
                notes = st.text_area("Notes")
                envoyer = st.form_submit_button("Créer le devis")

                if envoyer:
                    try:
                        devis = creer_devis(
                            choix[client_label]["id"],
                            [{
                                "description": description.strip(),
                                "quantite": int(quantite),
                                "prix_unitaire": float(prix),
                            }],
                            notes,
                        )
                        st.success(
                            f"Devis {devis['numero']} créé — "
                            f"{devis['total']:.2f}"
                        )
                        st.rerun()
                    except Exception as erreur:
                        st.error(str(erreur))

        st.subheader("Historique des devis")
        devis = charger_devis()
        afficher_tableau([
            {
                "Numéro": d["numero"],
                "Date": d["date"],
                "Client": next(
                    (
                        c["nom"] for c in clients
                        if c["id"] == d["client_id"]
                    ),
                    "Client inconnu",
                ),
                "Total": d["total"],
                "Statut": d["statut"],
            }
            for d in devis
        ])

    except Exception as erreur:
        st.error(str(erreur))


elif page == "Fabrication":
    st.header("⚙️ Gestion de la fabrication")

    try:
        clients = charger_clients()

        if not clients:
            st.warning("Ajoute d'abord un client.")
        else:
            choix = {
                f"{c['nom']} — {c['id'][:8]}": c
                for c in clients
            }

            with st.form("creer_fabrication"):
                client_label = st.selectbox(
                    "Client", list(choix.keys())
                )
                description = st.text_input(
                    "Description du travail"
                )
                largeur = st.number_input(
                    "Largeur (mm)", min_value=0, step=10
                )
                hauteur = st.number_input(
                    "Hauteur (mm)", min_value=0, step=10
                )
                quantite = st.number_input(
                    "Quantité", min_value=1, step=1
                )
                envoyer = st.form_submit_button(
                    "Enregistrer la fabrication"
                )

                if envoyer:
                    try:
                        if largeur <= 0 or hauteur <= 0:
                            st.error(
                                "La largeur et la hauteur doivent "
                                "être supérieures à zéro."
                            )
                        else:
                            fabrication = creer_fabrication(
                                choix[client_label]["id"],
                                description,
                                {
                                    "largeur_mm": largeur,
                                    "hauteur_mm": hauteur,
                                },
                                quantite,
                            )
                            st.success(
                                f"Fabrication {fabrication['numero']} "
                                "enregistrée."
                            )
                            st.rerun()
                    except Exception as erreur:
                        st.error(str(erreur))

        st.subheader("Historique des fabrications")
        afficher_tableau([
            {
                "Numéro": f["numero"],
                "Date": f["date"],
                "Description": f["description"],
                "Quantité": f["quantite"],
                "Statut": f["statut"],
            }
            for f in charger_fabrications()
        ])

    except Exception as erreur:
        st.error(str(erreur))


elif page == "Paramètres":
    st.header("⚙️ Paramètres")
    st.write("**Application :** Atelier PVC Pro")
    st.write("**Version :** 1.0")
    st.write("**Stockage configuré :** fichiers JSON")
    st.warning(
        "Sur Streamlit Cloud, les fichiers JSON locaux peuvent "
        "être perdus lors de certains redéploiements. Une base "
        "de données persistante sera nécessaire pour la production."
    )
