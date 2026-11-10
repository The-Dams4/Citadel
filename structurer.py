import json
import os
from dotenv import load_dotenv
import anthropic
from pieces import EXERCICES

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def structurer(texte):
    liste = "\n".join(EXERCICES.keys())
    consigne = f"""Tu ranges une séance de musculation dictée.
La dictée vient d'une reconnaissance vocale : corrige les fautes de transcription évidentes (exemple : « développez coucher » = « développé couché »).   
Exercices connus (utilise exactement ces noms) :
{liste}
Si un exercice ne correspond à aucun nom de la liste, garde le nom dicté.
Une entrée par série : "3 séries de 10 à 50 kg" donne trois entrées.
Charge en kilos, 0 si poids du corps.
Réponds uniquement avec une liste JSON, sans texte autour, au format :
[{{"exercice": "...", "serie": 1, "repetitions": 10, "charge": 50}}]"""

    reponse = client.messages.create(
        model="claude-haiku-5-5",
        max_tokens=2000,
        system=consigne,
        messages=[{"role": "user", "content": texte}],
    )
    brut = "".join(bloc.text for bloc in reponse.content if bloc.type == "text")
    debut = brut.find("[")
    fin = brut.rfind("]") + 1
    return json.loads(brut[debut:fin])

if __name__ == "__main__":
    dictee = "DC incliné 4 séries de 8 à 60 kilos, puis tractions 3x6 au poids du corps, et curl marteau 3 séries de 12 avec des 14"
    for s in structurer(dictee):
        piece = EXERCICES.get(s["exercice"], "Inconnue")
        print(s["exercice"], "|", piece, "| série", s["serie"], "|", s["repetitions"], "reps |", s["charge"], "kg")