from flask import Flask, render_template, request
import numpy as np

app = Flask(__name__)

# Guna recommendation mapped to 9 combinations
recommendations = {
    "SS": {"title": "Kun Faya Kun – Pure Peace", "url": "https://www.youtube.com/embed/T94PHkuydcw"},
    "SR": {"title": "Ilahi – Calm Yet Driven", "url": "https://www.youtube.com/embed/2akgW4duhNw"},
    "ST": {"title": "Tera Yaar Hoon Main – Serenity with Depth", "url": "https://www.youtube.com/embed/MFZ94Agvp_4"},
    "RS": {"title": "Zinda – Focused Action with Compassion", "url": "https://www.youtube.com/embed/hOW2KPLMvOQ"},
    "RR": {"title": "Apna Time Aayega – Raw Energy", "url": "https://www.youtube.com/embed/xO7AfJbZQXM"},
    "RT": {"title": "Kabira – Restless Mind, Seeking Depth", "url": "https://www.youtube.com/embed/pLUJdMCTw-w"},
    "TS": {"title": "Tera Naam – Heavy But Hopeful", "url": "https://www.youtube.com/embed/_ylKbs48KW0"},
    "TR": {"title": "Agar Tum Saath Ho – Melancholic Momentum", "url": "https://www.youtube.com/embed/oD2-49dEaD4"},
    "TT": {"title": "Channa Mereya – Deep Stillness", "url": "https://www.youtube.com/embed/gvyUuxdRdR4"}
}

# Meaningful description for each guna combination
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
        # Get first 12 psychological responses
        guna_responses = np.array([int(request.form[f'q{i}']) for i in range(1, 13)]).reshape(12, 1)

        # Guna matrix (S, R, T)
        guna_matrix = np.array([
            [1, 0, 0],  # Q1 - S
            [1, 0, 0],  # Q2 - S
            [0, 1, 0],  # Q3 - R
            [0, 1, 0],  # Q4 - R
            [0, 0, 1],  # Q5 - T
            [0, 0, 1],  # Q6 - T
            [1, 0, 0],  # Q7 - S
            [0, 1, 0],  # Q8 - R
            [0, 0, 1],  # Q9 - T
            [1, 0, 0],  # Q10 - S
            [0, 1, 0],  # Q11 - R
            [0, 0, 1],  # Q12 - T
        ])

        guna_scores = np.dot(guna_matrix.T, guna_responses).flatten()
        guna_labels = ['Sattva', 'Rajas', 'Tamas']
        guna_dict = dict(zip(guna_labels, guna_scores))

        # Step 2: Music Preferences (boost relevant guna)
        music_map = {
            "spiritual": 'Sattva',
            "high_energy": 'Rajas',
            "emotional": 'Tamas',
            "relaxing": 'Sattva',
            "rap": 'Rajas',
            "romantic": 'Tamas'
        }

        for idx, key in enumerate(music_map.keys(), start=13):
            rating = int(request.form.get(f'q{idx}', 3))  # default neutral if missing
            guna_dict[music_map[key]] += (rating - 3) * 0.5  # slight boost/reduce

        # Step 3: Find top 2 gunas
        sorted_gunas = sorted(guna_dict.items(), key=lambda x: x[1], reverse=True)
        top_2 = sorted_gunas[:2]
        guna_code = top_2[0][0][0] + top_2[1][0][0]  # e.g., SR

        song = recommendations.get(guna_code.upper(), recommendations['SS'])
        traits = guna_traits.get(guna_code.upper(), "Unique state. Explore deeper.")

        return render_template(
            'result.html',
            guna_code=guna_code.upper(),
            guna_scores=guna_dict,
            song=song,
            traits=traits,
            top_two=top_2
        )

    except Exception as e:
        return f"<h3>Something went wrong: {str(e)}</h3>"

if __name__ == '__main__':
    app.run(debug=True)
