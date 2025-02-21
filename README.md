# Real-Time Speech Transcription with Summarization and Insights

## Overview
This project implements a real-time speech transcription system using Azure Cognitive Services and OpenAI's GPT-4 API. The application transcribes speech from multiple speakers, identifies key dates, extracts actionable items, and provides a summarized transcript.

![Screenshot 2025-02-21 213250](https://github.com/user-attachments/assets/7d172fe6-7e5a-4836-8121-79455bdd6bab)


## Features
- **Real-Time Transcription**: Captures speech input and transcribes it using Azure Speech SDK.
- **Speaker Identification**: Differentiates between speakers during transcription.
- **Date Detection**: Extracts date-related information from transcriptions.
- **Action Item Extraction**: Identifies actionable tasks or instructions.
- **Summarization**: Summarizes the entire transcription using OpenAI's GPT-4.
- **WebSocket API**: Enables real-time communication with a client for dynamic interactions.

## Prerequisites
1. **Azure Cognitive Services Speech API**:
   - Obtain an API key and region from Azure.
2. **OpenAI API**:
   - Obtain an API key from OpenAI.
3. **Python Libraries**:
   - Install the following libraries:
     ```bash
     pip install azure-cognitiveservices-speech openai python-dotenv fastapi uvicorn dateparser
     ```
4. **Environment Variables**:
   - Create a `.env` file with the following keys:
     ```env
     AZURE_SPEECH_API_KEY=<Your Azure Speech API Key>
     AZURE_SPEECH_REGION=<Your Azure Speech Region>
     AI_API_KEY=<Your OpenAI API Key>
     ```

## Project Structure
```
project/
├── main.py       # Main application file (provided above).
├── .env          # Environment variables file.
├── requirements.txt # List of required Python libraries.
└── README.md     # Project documentation.
```

## How It Works
1. **Setup Speech Config**:
   - Initializes Azure Speech SDK with the provided API key and region.
   - Sets the default language to English (US).

2. **Transcription**:
   - Captures audio input from the microphone.
   - Transcribes speech into text and identifies speakers.

3. **Data Analysis**:
   - **Date Detection**: Uses regex and `dateparser` to find date patterns in the text.
   - **Action Items**: Identifies actionable tasks using a regex pattern.

4. **Summarization**:
   - Combines transcripts with speaker identifiers.
   - Checks if the conversation is a monologue or a dialogue.
   - Calls OpenAI GPT-4 to generate a summary.

5. **WebSocket API**:
   - Establishes a WebSocket connection to send and receive real-time data.
   - Sends transcription, dates, actionable items, and summary upon request.

## API Endpoints
### WebSocket Endpoint
**URL**: `/ws`
- Establish a WebSocket connection.
- **Input**: Sends "STOP" to terminate transcription and process data.
- **Output**:
  ```json
  {
    "type": "summary",
    "transcript": "<Complete transcript>",
    "dates": ["<Detected dates>"],
    "action_items": ["<Actionable items>"],
    "summary": "<Conversation summary>"
  }
  ```

## Running the Application
1. **Start the Server**:
   ```bash
   uvicorn main:app --reload
   ```
2. **Connect to WebSocket**:
   - Use a WebSocket client (e.g., Postman, browser extension) to connect to `ws://<server_address>/ws`.
3. **Interact**:
   - Start speaking to capture audio input.
   - Send "STOP" to receive processed results.

## Example Outputs
### Transcript
```text
[2024-12-24 12:00:00] Speaker ID(1): Hello, how are you?
[2024-12-24 12:00:10] Speaker ID(2): I'm doing well, thank you!
```

### Dates Detected
```json
["2024-12-24"]
```

### Action Items
```json
["Please review the document.", "Ensure the deadlines are met."]
```

### Summary
```text
This is a conversation. Speaker 1 greeted Speaker 2 and inquired about their well-being. Speaker 2 responded positively.
```

## Customization
- **Default Language**: Change the default language in `setup_speech_config` by modifying `speech_config.speech_recognition_language`.
- **Regex Patterns**: Update `find_dates_in_text` and `find_action_items` functions to refine detection logic.

## Known Limitations
- Date and action item detection rely on regex patterns, which may not cover all edge cases.
- Requires a stable internet connection for Azure Speech SDK and OpenAI API.



