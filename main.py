from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import sqlite3

app = FastAPI()

# Database
conn = sqlite3.connect("homeoplay.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symptoms TEXT,
    remedy TEXT,
    time TEXT
)
""")
conn.commit()

class SymptomInput(BaseModel):
    symptoms: str

REMEDIES = {
    "Arsenicum Album": ["burning", "restless", "fear", "anxiety", "thirst"],
    "Pulsatilla": ["weeps", "mild", "consolation"],
    "Nux Vomica": ["irritable", "chilly", "constipation"],
    "Belladonna": ["sudden", "violent", "red face"],
    "Lachesis": ["jealous", "left sided"]
}

def repertorize(symptoms):
    symptoms = symptoms.lower()
    scores = {}

    for remedy, keys in REMEDIES.items():
        score = 0
        for k in keys:
            if k in symptoms:
                score += 1
        scores[remedy] = score

    best = max(scores, key=scores.get)
    return best

@app.post("/repertorize")
def analyze(data: SymptomInput):
    remedy = repertorize(data.symptoms)

    cur.execute(
        "INSERT INTO logs VALUES (NULL, ?, ?, ?)",
        (data.symptoms, remedy, str(datetime.now()))
    )
    conn.commit()

    return {
        "remedy": remedy,
        "note": "Educational purpose only"
    }

@app.get("/")
def root():
    return {"status": "HomeoPlay Backend Running"}
