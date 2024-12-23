import os
import queue
import azure.cognitiveservices.speech as speechsdk
from datetime import datetime
import openai
from dotenv import load_dotenv
import warnings
import re
import dateparser
from fastapi import FastAPI, WebSocket

app = FastAPI()

warnings.filterwarnings("ignore")

# Load environment variables from .env file
load_dotenv()

# Global variables
audio_queue = queue.Queue()  # Queue to process audio chunks
transcripts = []  # List to keep track of transcripts
last_transcribed_text = ""  # Variable to track the last transcribed text

def setup_speech_config():
    """
    Initializes the Azure Speech SDK configuration.
    """
    languages = [
        "en-US", "fr-FR", "es-ES", "de-DE", "hi-IN",
        "zh-CN", "ja-JP", "ru-RU", "it-IT", "ar-EG"
    ]

    speech_key = os.getenv("AZURE_SPEECH_API_KEY")
    speech_region = os.getenv("AZURE_SPEECH_REGION")

    if not speech_key or not speech_region:
        print("Please set the environment variables AZURE_SPEECH_API_KEY and AZURE_SPEECH_REGION.")
        return None

    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
    speech_config.speech_recognition_language = languages[0]  # Default language: English (US)
    speech_config.set_property(property_id=speechsdk.PropertyId.SpeechServiceResponse_DiarizeIntermediateResults, value='true')
    return speech_config

# Callback functions for Azure Speech SDK events
def conversation_transcriber_transcribed_cb(evt: speechsdk.SpeechRecognitionEventArgs):
    global last_transcribed_text

    if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
        pc_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        transcripts.append((evt.result.text, pc_time, evt.result.speaker_id))

        if evt.result.text != last_transcribed_text:
            print(f'[{pc_time}] Speaker ID({evt.result.speaker_id}): {evt.result.text}')
            last_transcribed_text = evt.result.text

def find_dates_in_text(text):
    date_regex = r'\b(?:\d{1,2}(?:st|nd|rd|th)? [A-Za-z]+ \d{4}|\d{1,2} [A-Za-z]+ \d{4}|\b[A-Za-z]+ \d{1,2},? \d{4}|first? of [A-Za-z]+ in the year of \d{4})\b | \b\d{2}/\d{2}/\d{4}\b'
    matches = re.findall(date_regex, text)
    found_dates = []

    for match in matches:
        if isinstance(match, str):
            match = re.sub(r'(\d{1,2})(st|nd|rd|th)', r'\1', match)
            match = match.replace("in the year of", "").strip()
            parsed_date = dateparser.parse(match)
            if parsed_date:
                found_dates.append(parsed_date)

    return found_dates

def find_action_items(text):
    action_item_regex = r'\b(?:do|follow|submit|review|check|ensure|make sure to|you must|please)\b.*?[.!?]'
    matches = re.findall(action_item_regex, text, re.IGNORECASE)
    return matches



def summarize_transcriptions(transcripts):

    # Combine transcript with speaker identifiers
    combined_transcript = "\n".join(
        [f"Speaker {speaker_id}: {text}" for text, _, speaker_id in transcripts]
    )

    # Check for monologue or conversation
    if len(set([speaker_id for _, _, speaker_id in transcripts])) == 1:
        combined_transcript = (
            "This is a monologue. Here is the transcript:\n" + combined_transcript
        )
    else:
        combined_transcript = (
            "This is a conversation. Here is the transcript:\n" + combined_transcript
        )

    # Set OpenAI API key
    openai.api_key = os.getenv("AI_API_KEY")

    try:
    # Call the ChatCompletion API
        response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "user",
                "content": f"Please summarize the following conversation:\n\n{combined_transcript}",
            }
        ],
    )

    # Extract and return the response content
        summary = response['choices'][0]['message']['content']
        return summary

    except Exception as e:
        # Handle exceptions
        print(f"Error during summarization: {e}")
        return None


@app.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        speech_config = setup_speech_config()
        if not speech_config:
            await websocket.send_json({"type": "error", "message": "Speech configuration error."})
            return

        audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        conversation_transcriber = speechsdk.transcription.ConversationTranscriber(speech_config=speech_config, audio_config=audio_config)
        conversation_transcriber.transcribed.connect(conversation_transcriber_transcribed_cb)

        conversation_transcriber.start_transcribing_async()

        while True:
            data = await websocket.receive_text()
            l=[]
    
            if data == "STOP":
                conversation_transcriber.stop_transcribing_async().get()
                print(transcripts)

                for i in transcripts:
                    reversed_data = i[::-1]
                    l.append((" : ".join(reversed_data)))

                dates_found = find_dates_in_text(str(transcripts))
                action_items_found = find_action_items(str(transcripts))
                summary = summarize_transcriptions(transcripts)
                

                await websocket.send_json({
                    "type": "summary",
                    "transcript": "".join(l),
                    "dates": dates_found,
                    "action_items": action_items_found,
                    "summary": summary
                })
                break

    except Exception as e:
        await websocket.send_json({"type": "error", "message": str(e)})

    finally:
        await websocket.close()
