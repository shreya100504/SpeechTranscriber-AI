document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const videoFileInput = document.getElementById('videoFile');
    const uploadBtn = document.getElementById('uploadBtn');
    const progressContainer = document.getElementById('progressContainer');
    const progressBar = document.getElementById('progressBar');
    const progressStatus = document.getElementById('progressStatus');
    const errorAlert = document.getElementById('errorAlert');
    const errorMessage = document.getElementById('errorMessage');
    const resultsContainer = document.getElementById('resultsContainer');
    const transcriptText = document.getElementById('transcriptText');
    const downloadBtn = document.getElementById('downloadBtn');

    function showError(message) {
        errorMessage.textContent = message;
        errorAlert.classList.remove('d-none');
        progressContainer.classList.add('d-none');
        uploadBtn.disabled = false;
    }

    function resetUI() {
        errorAlert.classList.add('d-none');
        progressContainer.classList.add('d-none');
        resultsContainer.classList.add('d-none');
        progressBar.style.width = '0%';
        progressBar.textContent = '0%';
        progressStatus.textContent = 'Uploading video...';
        transcriptText.value = '';
    }

    function updateProgress(percent, statusText) {
        progressBar.style.width = `${percent}%`;
        progressBar.textContent = `${percent}%`;
        progressStatus.textContent = statusText;
    }

    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();

        const videoFile = videoFileInput.files[0];
        if (!videoFile) {
            showError('Please select a video file');
            return;
        }

        const maxSize = 100 * 1024 * 1024;
        if (videoFile.size > maxSize) {
            showError('File size exceeds limit (100MB). Please choose a smaller file.');
            return;
        }

        resetUI();
        progressContainer.classList.remove('d-none');
        uploadBtn.disabled = true;

        const formData = new FormData();
        formData.append('video', videoFile);

        let progressInterval;
        const simulateProgress = () => {
            let progress = 0;
            progressInterval = setInterval(() => {
                if (progress < 95) {
                    progress += Math.random() * 4;
                    updateProgress(Math.round(progress),
                        progress < 30 ? 'Uploading video...' :
                        progress < 60 ? 'Extracting audio...' :
                        progress < 90 ? 'Transcribing using Whisper...' :
                        'Finalizing...'
                    );
                }
            }, 600);
        };
        simulateProgress();

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            clearInterval(progressInterval);
            if (!response.ok) {
                return response.text().then(text => {
                    try {
                        const data = JSON.parse(text);
                        throw new Error(data.error || 'Error processing video');
                    } catch {
                        throw new Error(text || 'Error processing video');
                    }
                });
            }
            return response.json();
        })
        .then(data => {
            updateProgress(100, 'Transcription complete!');

            setTimeout(() => {
                progressContainer.classList.add('d-none');
                resultsContainer.classList.remove('d-none');
                transcriptText.value = data.transcript || '';
                uploadBtn.disabled = false;
            }, 800);
        })
        .catch(error => {
            clearInterval(progressInterval);
            showError(error.message || 'Error processing video');
        });
    });

    downloadBtn.addEventListener('click', function() {
        if (!transcriptText.value.trim()) {
            showError('No transcript to download');
            return;
        }

        const blob = new Blob([transcriptText.value], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = 'transcript.txt';

        document.body.appendChild(a);
        a.click();

        setTimeout(() => {
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        }, 100);
    });

    videoFileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            const fileName = this.files[0].name;
            this.nextElementSibling.textContent = `Selected: ${fileName}`;
        } else {
            this.nextElementSibling.textContent = 'Choose file';
        }
    });
});
