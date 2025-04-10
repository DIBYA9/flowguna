import os
import re
import pandas as pd
import torch
import torchaudio
import subprocess
from yt_dlp import YoutubeDL

# Define music preference labels
music_prefs = [
    "Devotional / Bhajans",
    "High-energy / Dance",
    "Emotional / Romantic",
    "Lo-fi / Chill",
    "Instrumental / Nature",
    "Folk / Regional"
]

guna_labels = ["SS", "SR", "ST", "RS", "RR", "RT", "TS", "TR", "TT"]

# Placeholder AI model (just returns random values for now)
class SimpleAudioClassifier(torch.nn.Module):
    def forward(self, x):
        guna = torch.randint(0, 9, (1,))
        pref = torch.randint(0, 6, (1,))
        return guna.item(), pref.item()

model = SimpleAudioClassifier()

def download_audio_yt_dlp(url, output_folder="downloads"):
    os.makedirs(output_folder, exist_ok=True)
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]',
        'outtmpl': f'{output_folder}/%(title).70s.%(ext)s',
        'quiet': True,
        'noplaylist': True
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename, info['title']

def convert_to_wav(input_file):
    output_file = re.sub(r'\.\w+$', '.wav', input_file)
    subprocess.run(['ffmpeg', '-i', input_file, output_file, '-y'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_file

def extract_features(file_path):
    waveform, sample_rate = torchaudio.load(file_path)
    mel_spec = torchaudio.transforms.MelSpectrogram()(waveform)
    return mel_spec.mean(dim=-1)  # Reduce temporal dimension

def ask_user(prompt, options):
    print(prompt)
    for idx, option in enumerate(options):
        print(f"{idx + 1}. {option}")
    while True:
        try:
            choice = int(input("Your choice (number): "))
            if 1 <= choice <= len(options):
                return choice - 1
        except ValueError:
            pass
        print("❌ Invalid choice. Please enter a number.")

def save_to_csv(song_title, guna, music_pref, url, csv_file="music.csv"):
    row = {
        "Title": song_title,
        "Guna": guna,
        "Music_Preference": music_pref,
        "YouTube_URL": url
    }
    df = pd.DataFrame([row])
    if os.path.exists(csv_file):
        df.to_csv(csv_file, mode='a', index=False, header=False)
    else:
        df.to_csv(csv_file, index=False)

# === MAIN ===
def main():
    url = input("🔗 Enter YouTube link: ").strip()
    print(f"\n🎧 Downloading audio from: {url}")

    try:
        file_path, title = download_audio_yt_dlp(url)
        wav_file = convert_to_wav(file_path)

        print("✅ Audio converted to WAV.")

        features = extract_features(wav_file)
        predicted_guna_idx, predicted_pref_idx = model(features)

        # Show predictions
        predicted_guna = guna_labels[predicted_guna_idx]
        predicted_pref = music_prefs[predicted_pref_idx]

        print(f"\n🔍 Predicted Guna: {predicted_guna}")
        print(f"🎵 Predicted Music Preference: {predicted_pref}")

        # Ask user to confirm or correct
        correct_guna = ask_user("\nIs the predicted Guna correct?", guna_labels)
        correct_pref = ask_user("What is the correct Music Preference for this song?", music_prefs)

        save_to_csv(title, guna_labels[correct_guna], music_prefs[correct_pref], url)
        print("✅ Entry saved to music.csv")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()