from flask import Flask, render_template, request
import numpy as np
import pandas as pd
import os
import random

app = Flask(__name__)

# Traits of Guna Combinations
guna_traits = {
    "SS": "High clarity and calm. Ideal for focus, meditation, and self-awareness.",
    "SR": "Peaceful and ambitious. You balance action with purpose.",
    "ST": "Spiritual and emotionally deep. Ideal for reflective creativity.",
    "RS": "Energetic with empathy. Strong for leadership with care.",
    "RR": "Driven but impatient. Needs channeling through mindful intensity.",
    "RT": "Restless and overwhelmed. Reflect, then act slowly.",
    "TS": "Slow-moving but aware. Needs uplifting and light.",
    "TR": "Emotionally reactive. Can shift through self-expression.",
    "TT": "Low energy and static. Needs emotional ignition."
}

# Guna Distance Ranking
guna_priority = {
    "S": ["S", "R", "T"],
    "R": ["R", "S", "T"],
    "T": ["T", "R", "S"]
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/result', methods=['POST'])
def result():
    try:
        # Guna calculation
        guna_responses = np.array([int(request.form[f'q{i}']) for i in range(1, 13)]).reshape(12, 1)

        guna_matrix = np.array([
            [1, 0, 0], [1, 0, 0], [0, 1, 0], [0, 1, 0],
            [0, 0, 1], [0, 0, 1], [1, 0, 0], [0, 1, 0],
            [0, 0, 1], [1, 0, 0], [0, 1, 0], [0, 0, 1],
        ])

        guna_scores = np.dot(guna_matrix.T, guna_responses).flatten()
        guna_labels = ['Sattva', 'Rajas', 'Tamas']
        guna_dict = dict(zip(guna_labels, guna_scores))

        # Music preference adjustment
        music_map = {
            "spiritual": 'Sattva',
            "high_energy": 'Rajas',
            "emotional": 'Tamas',
            "relaxing": 'Sattva',
            "rap": 'Rajas',
            "romantic": 'Tamas'
        }

        preference_scores = {}
        for idx, key in enumerate(music_map.keys(), start=13):
            rating = int(request.form.get(f'q{idx}', 3))
            guna_dict[music_map[key]] += (rating - 3) * 0.5
            preference_scores[key] = rating

        # Sort guna and preference
        sorted_gunas = sorted(guna_dict.items(), key=lambda x: x[1], reverse=True)
        top_2 = sorted_gunas[:2]
        guna_code = top_2[0][0][0] + top_2[1][0][0]

        # Best music preference selected
        best_preference = max(preference_scores, key=preference_scores.get)
        best_pref_label = music_map[best_preference]

        # Load songs
        base_dir = os.path.dirname(os.path.abspath(__file__))
        df = pd.read_csv(os.path.join(base_dir, "music.csv"), names=["Title", "Guna", "Type", "Link"])

        # Priority 1: Match both Guna & Preference
        matched = df[(df["Guna"] == guna_code) & (df["Type"].str.lower() == best_preference.replace("_", " "))]
        if matched.empty:
            # Priority 2: Match same preference, close Guna
            for alt_code in generate_alternative_gunas(guna_code):
                matched = df[(df["Guna"] == alt_code) & (df["Type"].str.lower() == best_preference.replace("_", " "))]
                if not matched.empty:
                    break

        if matched.empty:
            # Priority 3: Match Guna only
            matched = df[df["Guna"] == guna_code]

        if not matched.empty:
            selected = matched.sample(1).iloc[0]
            song = {"title": selected["Title"], "url": selected["Link"]}
        else:
            song = {
                "title": "Raabta (Kehte Hain Khuda) – Agent Vinod",
                "url": "https://www.youtube.com/watch?v=zlt38OOqwDc"
            }

        return render_template(
            'result.html',
            guna_code=guna_code,
            guna_scores=guna_dict,
            song=song,
            traits=guna_traits.get(guna_code, "Unique emotional state."),
            top_two=top_2
        )

    except Exception as e:
        return f"<h3>Something went wrong: {str(e)}</h3>"

def generate_alternative_gunas(code):
    # Generate similar guna codes in priority order
    a, b = code[0], code[1]
    alternates = []
    for x in guna_priority[a]:
        for y in guna_priority[b]:
            combo = x + y
            if combo != code:
                alternates.append(combo)
    return alternates

if __name__ == '__main__':
    app.run(debug=True)
