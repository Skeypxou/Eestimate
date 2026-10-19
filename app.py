
import streamlit as st
import pandas as pd

from services.client_service import (
    charger_clients,
    ajouter_client,
    modifier_client,
    rechercher_clients,
)

st.set_page_config(
    page_title="Atelier PVC Pro",
    page_icon="🏭",
    layout="wide",
)

st.title("🏭 Atelier PVC Pro")
st.caption("Gestion professionnelle de votre atelier de menuiserie PVC")

if "page" not in st.session_state:
    st.session_state.page = "Tableau de bord"

with st.sidebar:
    st.title("🏭 Atelier PVC")
    st.divider()

    pages = [
        "Tableau de bord",
        "Clients",
        "Devis",
        "Catalogue PVC",
        "Vitrages",
        "Accessoires",
        "Fabrication",
        "Paramètres",
    ]

    for page in pages:
        if st.button(page, use_container_width=True):
            st.session_state.page = page

page = st.session_state.page

if page == "Tableau de bord":
    st.header("Tableau de bord")

    try:
        clients = charger_clients()
        total_clients = len(clients)
    except Exception as erreur:
        st.error(str(erreur))
        total_clients = 0

    col1, col2, col3 = st.columns(3)

    col1.metric("Clients enregistrés", total_clients)
    col2.metric("Devis", 0)
    col3.metric("Commandes en cours", 0)

    st.divider()
    st.info("Bienvenue dans votre espace de gestion Atelier PVC Pro.")

elif page == "Clients":
    st.header("👥 Gestion des clients")

    onglet_ajout, onglet_liste, onglet_modification = st.tabs(
        ["Ajouter un client", "Liste des clients", "Modifier un client"]
    )

    with onglet_ajout:
        with st.form("form_ajout_client", clear_on_submit=True):
            nom = st.text_input("Nom complet *")
            telephone = st.text_input("Téléphone")
            email = st.text_input("Adresse e-mail")
            adresse = st.text_area("Adresse")

            envoyer = st.form_submit_button(
                "Enregistrer le client",
                use_container_width=True,
            )

            if envoyer:
                try:
                    client = ajouter_client(
                        nom, telephone, email, adresse
                    )
                    st.success(f"Client « {client['nom']} » enregistré.")
                    st.rerun()
                except Exception as erreur:
                    st.error(str(erreur))

    with onglet_liste:
        recherche = st.text_input(
            "Rechercher par nom, téléphone ou e-mail"
        )

        try:
            clients = rechercher_clients(recherche)

            if clients:
                tableau = [
                    {
                        "Nom": c.get("nom", ""),
                        "Téléphone": c.get("telephone", ""),
                        "E-mail": c.get("email", ""),
                        "Adresse": c.get("adresse", ""),
                        "Créé le": c.get("date_creation", ""),
                    }
                    for c in clients
                ]

                st.dataframe(
                    pd.DataFrame(tableau),
                    use_container_width=True,
                    hide_index=True,
                )

                st.download_button(
                    "📥 Exporter les clients en CSV",
                    data=pd.DataFrame(tableau).to_csv(
                        index=False
                    ).encode("utf-8-sig"),
                    file_name="clients.csv",
                    mime="text/csv",
                )
            else:
                st.info("Aucun client trouvé.")

        except Exception as erreur:
            st.error(str(erreur))

    with onglet_modification:
        try:
            clients = charger_clients()

            if not clients:
                st.info("Ajoutez d'abord un client.")
            else:
                choix = {
                    f"{c['nom']} — {c.get('telephone', '')}": c
                    for c in clients
                }

                selection = st.selectbox(
                    "Choisir un client",
                    list(choix.keys()),
                )
                client = choix[selection]

                with st.form("form_modifier_client"):
                    nouveau_nom = st.text_input(
                        "Nom complet *", value=client.get("nom", "")
                    )
                    nouveau_telephone = st.text_input(
                        "Téléphone",
                        value=client.get("telephone", ""),
                    )
                    nouvel_email = st.text_input(
                        "E-mail", value=client.get("email", "")
                    )
                    nouvelle_adresse = st.text_area(
                        "Adresse", value=client.get("adresse", "")
                    )

                    modifier = st.form_submit_button(
                        "Enregistrer les modifications",
                        use_container_width=True,
                    )

                    if modifier:
                        try:
                            modifier_client(
                                client["id"],
                                nouveau_nom,
                                nouveau_telephone,
                                nouvel_email,
                                nouvelle_adresse,
                            )
                            st.success("Client modifié avec succès.")
                            st.rerun()
                        except Exception as erreur:
                            st.error(str(erreur))

        except Exception as erreur:
            st.error(str(erreur))

elif page == "Devis":
    st.header("📄 Devis")
    st.info("Le module de création et de gestion des devis sera développé ensuite.")

elif page == "Catalogue PVC":
    st.header("🪟 Catalogue des profils PVC")
    st.info("Le catalogue des profils et leurs prix sera développé ensuite.")

elif page == "Vitrages":
    st.header("🔲 Gestion des vitrages")
    st.info("Le catalogue des vitrages sera développé ensuite.")

elif page == "Accessoires":
    st.header("🔩 Accessoires")
    st.info("Les poignées, paumelles, serrures et autres accessoires seront ajoutés ensuite.")

elif page == "Fabrication":
    st.header("⚙️ Fabrication")
    st.info("Les dimensions, calculs et listes de découpe seront développés ensuite.")

elif page == "Paramètres":
    st.header("⚙️ Paramètres")
    st.write("**Application :** Atelier PVC Pro")
    st.write("**Version :** 1.0")
    st.write("**Stockage :** fichiers JSON")
