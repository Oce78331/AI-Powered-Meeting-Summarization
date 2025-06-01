from flask import Flask, render_template, request, send_from_directory
import os
import whisper
from pydub import AudioSegment
from pydub.utils import mediainfo
import boto3
import json

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load Whisper model
print("Loading Whisper model...")
model = whisper.load_model("small")
print("Model loaded!")

REGION_NAME = os.getenv('REGION_NAME', 'us-east-1')  # default fallback

boto3.setup_default_session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=REGION_NAME
)

bedrock = boto3.client(
    service_name='bedrock-runtime',
    region_name=REGION_NAME  # <- ADD THIS LINE
)

def summarize_with_claude(transcript):
    full_prompt = f"""
Summarize this meeting transcript. Find the number of participants in the meeting. Provide meeting feedback and keyword highlight main.

Transcript:
{transcript}
"""

    body = json.dumps({
        "prompt": f"\n\nHuman:{full_prompt}\n\nAssistant:",
        "max_tokens_to_sample": 2000,
        "temperature": 0.5,
        "top_p": 0.9,
    })

    model_id = 'anthropic.claude-v2'
    accept = 'application/json'
    content_type = 'application/json'

    response_text = ""
    try:
        response = bedrock.invoke_model_with_response_stream(
            body=body,
            modelId=model_id,
            accept=accept,
            contentType=content_type
        )

        event_stream = response['body']
        for event in event_stream:
            chunk = event.get('chunk')
            if chunk:
                chunk_bytes = chunk.get('bytes')
                if chunk_bytes:
                    chunk_str = chunk_bytes.decode('utf-8')
                    chunk_json = json.loads(chunk_str)
                    completion = chunk_json.get('completion')
                    if completion:
                        response_text += completion
    except Exception as e:
        return f"Error during Bedrock stream processing: {e}"

    return response_text.strip()

def transcribe_with_whisper(path):
    try:
        result = model.transcribe(path)
        return result["text"]
    except Exception as e:
        return f"Transcription failed: {e}"

def save_transcript(transcript, filename):
    txt_filename = filename.rsplit('.', 1)[0] + '.txt'
    txt_filepath = os.path.join(app.config['UPLOAD_FOLDER'], txt_filename)
    with open(txt_filepath, 'w') as file:
        file.write(transcript)
    return txt_filename

def check_audio_validity(filepath):
    try:
        audio = AudioSegment.from_file(filepath)
        duration = len(audio) / 1000.0
        if duration < 1:
            return False, "Audio too short or silent."
        return True, None
    except Exception as e:
        return False, f"Error loading audio: {e}"

def convert_to_wav(filepath):
    audio = AudioSegment.from_file(filepath)
    audio = audio.set_frame_rate(16000).set_channels(1)
    wav_filepath = filepath.rsplit('.', 1)[0] + '.wav'
    audio.export(wav_filepath, format='wav')
    return wav_filepath

@app.route("/", methods=["GET", "POST"])
def index():
    transcript = ""
    txt_filename = ""
    summary = ""

    if request.method == "POST":
        if "audiofile" not in request.files:
            return "No file uploaded"

        file = request.files["audiofile"]
        if file.filename == "":
            return "No file selected"

        filename = file.filename
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        is_valid, error_message = check_audio_validity(filepath)
        if not is_valid:
            return error_message

        if filename.lower().endswith('.mp3'):
            filepath = convert_to_wav(filepath)

        transcript = transcribe_with_whisper(filepath)
        summary = summarize_with_claude(transcript)
        txt_filename = save_transcript(transcript, filename)

    return render_template("index.html", transcript=transcript, summary=summary, txt_filename=txt_filename)

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    app.run(debug=True)
