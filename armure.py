from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

SEUILS = [2, 4, 8, 12]  # semaines forgées pour passer Mk 2, 3, 4, 5


def semaine(jour):
    annee, numero, _ = jour.isocalendar()
    return (annee, numero)


def etat_armure(classeur):
    seances = classeur.worksheet("Séances").get_all_values()[1:]
    pieces = classeur.worksheet("Pièces").get_all_values()[1:]

    aujourd_hui = datetime.now(ZoneInfo("Asia/Bangkok")).date()
    cette_semaine = semaine(aujourd_hui)
    deux_dernieres = [semaine(aujourd_hui - timedelta(weeks=1)),
                      semaine(aujourd_hui - timedelta(weeks=2))]

    compte = {}
    premiere = None
    for ligne in seances:
        if len(ligne) < 3 or not ligne[0]:
            continue
        s = semaine(datetime.strptime(ligne[0], "%d/%m/%Y").date())
        compte[(ligne[2], s)] = compte.get((ligne[2], s), 0) + 1
        if premiere is None or s < premiere:
            premiere = s

    etat = []
    for p in pieces:
        nom, objectif = p[0], int(p[2])
        forgees = sum(1 for (piece, s), n in compte.items() if piece == nom and n >= objectif)
        mk = 1 + sum(1 for seuil in SEUILS if forgees >= seuil)
        rouille = premiere is not None and all(
            s >= premiere and compte.get((nom, s), 0) < objectif for s in deux_dernieres)
        etat.append({"piece": nom, "mk": mk, "objectif": objectif, "rouille": rouille,
                     "semaine": compte.get((nom, cette_semaine), 0)})
    return etat