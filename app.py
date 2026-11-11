import json
from datetime import datetime
from zoneinfo import ZoneInfo
import gspread
import pandas as pd
import streamlit as st
from pieces import EXERCICES
from structurer import structurer
from armure import etat_armure
from records import records_actuels, nouveaux_records

ID_CLASSEUR = "1hF78VjodLHoiKs9QDZ8tChI8WvOdRYluAyQeAtiw6jE"

st.set_page_config(page_title="Citadel", page_icon="🛡️")


def secret(nom):
    try:
        return st.secrets[nom]
    except Exception:
        return None


mot_de_passe = secret("APP_PASSWORD")
if mot_de_passe and st.text_input("Mot de passe", type="password") != mot_de_passe:
    st.stop()


@st.cache_resource
def ouvrir_classeur():
    cle = secret("GCP_JSON")
    if cle:
        client = gspread.service_account_from_dict(json.loads(cle))
    else:
        client = gspread.service_account(filename="cle_google.json")
    return client.open_by_key(ID_CLASSEUR)


classeur = ouvrir_classeur()

# --- L'armure ---
etat = etat_armure(classeur)
st.title(f"Citadel Mk {min(p['mk'] for p in etat)}")

if "message" in st.session_state:
    st.success(st.session_state.pop("message"))

if "records" in st.session_state:
    for annonce in st.session_state.pop("records"):
        st.info(annonce, icon="🏆")
    st.balloons()

for p in etat:
    gauche, droite = st.columns([1, 2])
    gauche.markdown(f"**{p['piece']}** · Mk {p['mk']}" + ("  \n🟠 rouille" if p["rouille"] else ""))
    droite.progress(min(p["semaine"] / p["objectif"], 1.0),
                    text=f"{p['semaine']} / {p['objectif']} séries cette semaine")

st.divider()

# --- La dictée ---
st.caption("Dictez votre séance. Marcus range, vous validez.")
dictee = st.text_area("Votre séance", height=150,
                      placeholder="Développé incliné 4 séries de 8 à 60 kilos, tractions 3x6...")

if st.button("Analyser"):
    if dictee.strip():
        with st.spinner("Marcus range votre séance..."):
            st.session_state["seance"] = pd.DataFrame(structurer(dictee))
    else:
        st.warning("Dictez d'abord quelque chose.")

if "seance" in st.session_state:
    st.subheader("Vérifiez avant d'enregistrer")
    tableau = st.data_editor(
        st.session_state["seance"],
        column_config={
            "exercice": st.column_config.SelectboxColumn("Exercice", options=list(EXERCICES.keys())),
            "serie": st.column_config.NumberColumn("Série", min_value=1, step=1),
            "repetitions": st.column_config.NumberColumn("Répétitions", min_value=0, step=1),
            "charge": st.column_config.NumberColumn("Charge (kg)", min_value=0.0, step=0.5),
        },
        num_rows="dynamic",
        hide_index=True,
    )
    tableau = tableau.dropna(subset=["exercice"]).fillna(0)

    inconnus = tableau[~tableau["exercice"].isin(EXERCICES.keys())]
    if not inconnus.empty:
        st.error("Exercice inconnu : " + ", ".join(inconnus["exercice"].unique())
                 + ". Choisissez le bon dans la liste.")

    if st.button("Valider la séance", type="primary", disabled=not inconnus.empty):
        date = datetime.now(ZoneInfo("Asia/Bangkok")).strftime("%d/%m/%Y")
        lignes = [[date, r["exercice"], EXERCICES[r["exercice"]],
                   int(r["serie"]), int(r["repetitions"]), float(r["charge"])]
                  for _, r in tableau.iterrows()]
        anciens = records_actuels(classeur)
        annonces = nouveaux_records(anciens, [(l[1], l[4], l[5]) for l in lignes])
        classeur.worksheet("Séances").append_rows(lignes, value_input_option="USER_ENTERED")
        if annonces:
            st.session_state["records"] = annonces
        del st.session_state["seance"]
        st.session_state["message"] = f"{len(lignes)} séries enregistrées. La Citadel se renforce."
        st.rerun()