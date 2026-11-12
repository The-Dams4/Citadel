import pandas as pd
import streamlit as st
from records import nombre


def afficher_progression(classeur):
    lignes = classeur.worksheet("Séances").get_all_values()[1:]
    donnees = [
        {"Date": l[0], "Exercice": l[1], "Repetitions": nombre(l[4]), "Charge": nombre(l[5])}
        for l in lignes if len(l) >= 6 and l[0] and l[1]
    ]
    st.subheader("Progression")
    if not donnees:
        st.caption("Aucune séance enregistrée pour l'instant.")
        return
    df = pd.DataFrame(donnees)
    df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y", errors="coerce")
    df = df.dropna(subset=["Date"])
    exercice = st.selectbox("Exercice", sorted(df["Exercice"].unique()))
    choix = df[df["Exercice"] == exercice]
    par_jour = choix.groupby("Date").agg(Charge=("Charge", "max"), Repetitions=("Repetitions", "max"))
    if (par_jour["Charge"] > 0).any():
        st.line_chart(par_jour["Charge"], y_label="Charge max (kg)")
    else:
        st.line_chart(par_jour["Repetitions"], y_label="Répétitions max")
    st.caption(f"{len(choix)} séries enregistrées depuis le {par_jour.index.min():%d/%m/%Y}.")
