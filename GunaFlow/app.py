from flask import Flask, render_template, request
import numpy as np
import pandas as pd
import random
import os

app = Flask(__name__)

# 🧠 Traits for each guna combination
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

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/result', methods=['POST'])
def result():
    try:
        # ✅ Extract responses for guna calculation (Q1–Q12)
        guna_responses = np.array([
            int(request.form[f'q{i}']) for i in range(1, 13)
        ]).reshape(12, 1)

        # 🔢 Matrix to calculate Sattva, Rajas, Tamas scores
        guna_matrix = np.array([
            [1, 0, 0], [1, 0, 0],  # Q1–Q2: Sattva
            [0, 1, 0], [0, 1, 0],  # Q3–Q4: Rajas
            [0, 0, 1], [0, 0, 1],  # Q5–Q6: Tamas
            [1, 0, 0],             # Q7: Sattva
            [0, 1, 0],             # Q8: Rajas
            [0, 0, 1],             # Q9: Tamas
            [1, 0, 0],             # Q10: Sattva
            [0, 1, 0],             # Q11: Rajas
            [0, 0, 1],             # Q12: Tamas
        ])

        guna_scores = np.dot(guna_matrix.T, guna_responses).flatten()
        guna_labels = ['Sattva', 'Rajas', 'Tamas']
        guna_dict = dict(zip(guna_labels, guna_scores))

        # 🎧 Music preference ratings (Q13–Q18)
        music_map = {
            "spiritual": 'Sattva',
            "high_energy": 'Rajas',
            "emotional": 'Tamas',
            "relaxing": 'Sattva',
            "rap": 'Rajas',
            "romantic": 'Tamas'
        }

        for idx, key in enumerate(music_map.keys(), start=13):
            rating = int(request.form.get(f'q{idx}', 3))  # Default = 3 (neutral)
            guna_dict[music_map[key]] += (rating - 3) * 0.5

        # 🔍 Get top 2 dominant gunas
        sorted_gunas = sorted(guna_dict.items(), key=lambda x: x[1], reverse=True)
        top_2 = sorted_gunas[:2]
        guna_code = top_2[0][0][0] + top_2[1][0][0]  # E.g., SR, ST, TR

        # 📁 Locate and load CSV from current file directory
        base_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(base_dir, 'music.csv')
        df = pd.read_csv(csv_path, names=["Title", "Guna", "Type", "Link"])

        # 🎯 Filter matching songs based on guna code and music type
        matching_songs = df[(df["Guna"] == guna_code) & (df["Type"] != '')]

        if not matching_songs.empty:
            selected = matching_songs.sample(1).iloc[0]
            song = {"title": selected["Title"], "url": selected["Link"]}
        else:
            song = {
                "title": "Fallback Song – Default",
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
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

if __name__ == '__main__':
    app.run(debug=True)
