import os

from flask import Flask, request, jsonify
import requests
from py_eureka_client import eureka_client
from supabase import create_client, Client
import uuid

app = Flask(__name__)

# Supabase setup
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# Eureka server URL
eureka_server = "http://localhost:8761/eureka/"

# The name of your application as registered in Eureka
app_name = "tts-service"

# The port at which your Flask application will be accessible
port = int(os.getenv("PORT", 5000))

eureka_client.init(eureka_server=eureka_server,
                   app_name=app_name,
                   instance_port=port)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/generate-speech', methods=['POST'])
def generate_speech():
    """Generates speech from text and uploads the audio to Supabase storage."""
    text = request.form.get('text')
    if not text:
        return jsonify({'error': 'No text provided'}), 400

    # Your Text-to-Speech API URL and headers
    url = "https://text-to-speech-realistic-ai-voices.p.rapidapi.com/text-to-speech/EXAVITQu4vr4xnSDxMaL/"

    payload = f"text={text}"
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "X-RapidAPI-Key": os.getenv("RAPIDAPI_KEY"),
        "X-RapidAPI-Host": "text-to-speech-realistic-ai-voices.p.rapidapi.com"
    }

    # Making a request to the Text-to-Speech API
    response = requests.post(url, data=payload, headers=headers)
    if response.status_code == 200:
        audio_content = response.content
        file_name = str(uuid.uuid4()) + ".mp3"  # Consider generating unique names for each file

        # Upload the audio content to Supabase storage
        result = supabase.storage.from_("audio").upload(file_name, audio_content,
                                                        {"content-type": "audio/mpeg"})

        # Check if upload was successful
        if result.status_code == 200:
            # Assuming public access, generate the URL
            # For private files, you'd generate a signed URL instead
            file_url = f"{supabase_url}/storage/v1/object/public/audio/{file_name}"
            return jsonify({'file_name': file_name, 'file_url': file_url}), 200
        else:
            return jsonify({'error': 'Failed to upload audio to storage'}), 500
    else:
        return jsonify({'error': 'Failed to generate audio from text'}), response.status_code


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
