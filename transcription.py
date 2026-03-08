import logging
import whisper

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Whisper model (large version)
model = whisper.load_model("base")

def transcribe_audio(audio_path):
    """
    Transcribe the full audio file using Whisper model.
    
    Args:
        audio_path (str): Path to the full audio file (.wav)
        
    Returns:
        str: Combined transcript from Whisper
    """
    try:
        logger.debug(f"Starting transcription for: {audio_path}")
        
        # Use Whisper to transcribe the audio
        result = model.transcribe(audio_path)
        
        # Extract the transcription text
        transcript = result['text']
        
        logger.debug(f"Transcription completed. Length: {len(transcript)} characters")
        return transcript.strip()

    except Exception as e:
        logger.error(f"Error in transcription: {e}")
        return f"Error transcribing audio: {str(e)}"
