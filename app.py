import os
import logging
import tempfile
import uuid
from flask import Flask, render_template, request, jsonify, send_file, session
from werkzeug.utils import secure_filename
from utils.video_processor import extract_audio
from utils.transcription import transcribe_audio

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Configure upload settings
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv'}
TEMP_DIR = tempfile.gettempdir()

def allowed_file(filename):
    """Check if the file is allowed for upload based on its extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Render the index page"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle video upload, extract audio, and perform transcription"""
    if 'video' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        # Generate a unique ID for this session
        process_id = str(uuid.uuid4())
        session['process_id'] = process_id
        
        # Create paths for processing
        video_path = os.path.join(TEMP_DIR, f"{process_id}_video_{secure_filename(file.filename)}")
        audio_path = os.path.join(TEMP_DIR, f"{process_id}_audio.wav")
        transcript = "An error occurred during processing."
        
        try:
            # Save the uploaded file
            file.save(video_path)
            logger.debug(f"Saved video to: {video_path}")
            
            # Extract audio from video
            extract_audio(video_path, audio_path)
            logger.debug(f"Extracted audio to: {audio_path}")
            
            # Transcribe the audio using Whisper
            transcript = transcribe_audio(audio_path)
            
            # Return the result (even if it's an error message)
            return jsonify({
                'success': True,
                'transcript': transcript
            })
            
        except Exception as e:
            logger.error(f"Critical error processing video: {e}")
            return jsonify({'error': str(e)}), 500
        finally:
            # Clean up temporary files
            try:
                if os.path.exists(video_path):
                    os.remove(video_path)
                if os.path.exists(audio_path):
                    os.remove(audio_path)
            except Exception as cleanup_error:
                logger.warning(f"Error cleaning up temporary files: {cleanup_error}")
    
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/download', methods=['POST'])
def download_transcript():
    """Allow the user to download the transcript as a text file"""
    try:
        transcript = request.json.get('transcript', '')
        if not transcript:
            return jsonify({'error': 'No transcript data provided'}), 400
        
        # Create a temporary file with the transcript
        process_id = session.get('process_id', str(uuid.uuid4()))
        temp_file_path = os.path.join(TEMP_DIR, f"{process_id}_transcript.txt")
        
        with open(temp_file_path, 'w') as f:
            f.write(transcript)
        
        return send_file(
            temp_file_path,
            as_attachment=True,
            download_name="transcript.txt",
            mimetype="text/plain"
        )
    
    except Exception as e:
        logger.error(f"Error downloading transcript: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
