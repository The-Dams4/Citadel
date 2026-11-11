import random

INTROS = [
    "Nouveau record, Monsieur.",
    "New personal best, Sir.",
    "Record battu. Marc Aurèle approuverait.",
    "La Citadel s'épaissit.",
    "Well done, Sir. The forge is pleased.",
]


def nombre(texte):
    try:
        return float(str(texte).replace(",", ".").replace("\u202f", "").strip())
    except ValueError:
        return 0.0


def meilleurs(lignes):
    best = {}
    for exercice, reps, charge in lignes:
        perf = (float(charge), int(reps))
        if perf > best.get(exercice, (-1.0, -1)):
            best[exercice] = perf
    return best


def records_actuels(classeur):
    seances = classeur.worksheet("Séances").get_all_values()[1:]
    lignes = [(l[1], nombre(l[4]), nombre(l[5])) for l in seances if len(l) >= 6 and l[1]]
    return meilleurs(lignes)


def texte_perf(charge, reps):
    if charge == 0:
        return f"poids du corps × {reps}"
    return f"{charge:g} kg × {reps}".replace(".", ",")


def nouveaux_records(anciens, seance):
    annonces = []
    for exercice, (charge, reps) in meilleurs(seance).items():
        ancien = anciens.get(exercice)
        if ancien is not None and (charge, reps) > ancien:
            annonces.append(f"{random.choice(INTROS)} **{exercice}** : {texte_perf(charge, reps)} "
                            f"(ancien : {texte_perf(*ancien)}).")
    return annonces