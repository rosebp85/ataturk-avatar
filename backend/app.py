# Import necessary libraries and modules
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import pyttsx3
import subprocess
import os
import uuid
import wave
import platform
import time
import threading
from datetime import datetime, timedelta

# Initialize Flask app and enable CORS
app = Flask(__name__)
CORS(app)

# API key for external service (e.g., OpenAI or other APIs)
API_KEY = "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"  

# Function to convert text to speech and save as an audio file
def text_to_speech(text, output_path):
    engine = pyttsx3.init()
    engine.setProperty("rate", 150) 
    voices = engine.getProperty("voices")
    engine.setProperty("voice", voices[0].id) 
    engine.save_to_file(text, output_path)
    engine.runAndWait()

# Function to convert a WAV file to OGG format
def convert_wav_to_ogg(wav_path, ogg_path):
    try:
        command = ["ffmpeg", "-y", "-i", wav_path, "-c:a", "libvorbis", ogg_path]
        subprocess.run(command, check=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(f"Error converting WAV to OGG: {e.stderr.decode()}")
        raise

# Function to generate mouth cues from an OGG file and save them as a JSON file
def generate_mouth_cues(ogg_path, json_path):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    rhubarb_path = os.path.join(base_dir, "Rhubarb-Lip-Sync-1.14.0-Windows", "rhubarb.exe")
    is_windows = platform.system() == "Windows"
    command = [rhubarb_path if is_windows else "rhubarb", ogg_path, "-o", json_path, "-f", "json"]

    try:
        subprocess.run(command, check=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(" Rhubarb error:", e.stderr.decode())
    except FileNotFoundError:
        print(" Rhubarb executable not found. Check the path or platform.")

# Function to calculate the duration of a WAV file
def get_duration(path):
    with wave.open(path, 'r') as wav:
        frames = wav.getnframes()
        rate = wav.getframerate()
        return frames / float(rate)

# Flask route to handle chat requests
@app.route("/chat", methods=["POST"])
def chat():
    # Parse the incoming JSON request
    data = request.get_json()
    user_message = data.get("message", "") # Extract the user's message
    
    # Return an error if no message is provided
    if not user_message:
        return jsonify({"error": "No message received"}), 400
        
    # Headers for the external API request
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:3000",
        "X-Title": "Ataturk Chat"
    }
    # Payload for the external chat API
    payload = {
        "model": "deepseek/deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are Mustafa Kemal Atatürk, founder of the Republic of Turkey, a visionary leader who values reason, reform, and education. "
                    "Respond to respectful, relevant questions on your life and national issues. Keep answers brief, no more than two sentences, and be kind like a father."

                )

            },
            {"role": "user", "content": user_message}
        ]
    }
    # Make a POST request to the external chat API
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    
    # Handle errors from the external API
    if response.status_code != 200:
        return jsonify({"error": response.text}), response.status_code

    # Parse the response from the external API
    result = response.json()
    answer = result["choices"][0]["message"]["content"]

    # Parse the response from the external API
    frontend_audio_path = os.path.join(os.getcwd(), "frontend/r3f-lipsync-tutorial/public/audios")
    os.makedirs(frontend_audio_path, exist_ok=True)        # Ensure the directory exists

    file_id = str(uuid.uuid4())                            # Generate a unique ID for the files

    wav_path = os.path.join(frontend_audio_path, f"{file_id}.wav")
    audio_filename = f"{file_id}.ogg"
    mouth_cues_filename = f"{file_id}.json"

    audio_filepath = os.path.join(frontend_audio_path, audio_filename)
    mouth_cues_filepath = os.path.join(frontend_audio_path, mouth_cues_filename)

    # Generate audio and mouth cues
    text_to_speech(answer, wav_path)
    convert_wav_to_ogg(wav_path, audio_filepath)
    generate_mouth_cues(audio_filepath, mouth_cues_filepath)

    # Return the response, audio URL, and mouth cues URL
    return jsonify({
        "response": answer,
        "audioUrl": f"/audios/{file_id}.ogg",
        "mouthCuesUrl": f"/audios/{file_id}.json"
    })

# Constants for audio file cleanup
AUDIO_FOLDER = os.path.join(os.getcwd(), "frontend", "r3f-lipsync-tutorial", "public", "audios")
CLEANUP_INTERVAL = 120        # Interval (in seconds) to check for old files
FILE_EXPIRATION = 120         # Time (in seconds) after which files are deleted

# Function to clean up old audio files
def cleanup_old_files():
    while True:
        now = time.time() # Current time
        for filename in os.listdir(AUDIO_FOLDER):
            file_path = os.path.join(AUDIO_FOLDER, filename)   # Calculate file age
            if os.path.isfile(file_path):
                file_age = now - os.path.getmtime(file_path)
                if file_age > FILE_EXPIRATION:                 # Check if the file is expired
                    try:
                        os.remove(file_path)                   # Delete the file
                        print(f" Deleted: {filename}")
                    except Exception as e:
                        print(f"Error deleting.{filename}: {e}")
        time.sleep(CLEANUP_INTERVAL)                           # Wait before checking again

# Start the cleanup thread
threading.Thread(target=cleanup_old_files, daemon=True).start()



# Main entry point to run the Flask app
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
