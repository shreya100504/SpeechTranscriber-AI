import os
import logging
import subprocess

# Configure logging
logger = logging.getLogger(__name__)

def extract_audio(video_path, audio_output_path):
    """
    Extract audio from a video file using ffmpeg directly
    
    Args:
        video_path (str): Path to the video file
        audio_output_path (str): Path where the extracted audio will be saved
        
    Returns:
        str: Path to the extracted audio file
    """
    try:
        logger.debug(f"Extracting audio from video: {video_path}")
        
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Use ffmpeg directly through subprocess to extract audio 
        # Extract mono (1 channel) audio at 16kHz sampling rate (good for speech recognition)
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-vn',                    # Disable video
            '-acodec', 'pcm_s16le',   # Output codec (PCM 16-bit)
            '-ar', '16000',           # Sample rate 16kHz (good for speech recognition)
            '-ac', '1',               # Mono channel
            '-y',                     # Overwrite output file if it exists
            audio_output_path
        ]
        
        logger.debug(f"Running ffmpeg command: {' '.join(cmd)}")
        
        # Run the ffmpeg command
        process = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Check if the command was successful
        if process.returncode != 0:
            logger.error(f"ffmpeg error: {process.stderr}")
            raise Exception(f"ffmpeg error: {process.stderr}")
        
        logger.debug(f"Audio extraction completed: {audio_output_path}")
        
        return audio_output_path
    
    except Exception as e:
        logger.error(f"Error extracting audio: {e}")
        raise Exception(f"Failed to extract audio: {str(e)}")
