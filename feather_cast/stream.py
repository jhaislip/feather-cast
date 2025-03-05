import subprocess

def start_ffmpeg(rtsp_url):
    """Start FFmpeg process to extract audio from the RTSP stream."""
    return subprocess.Popen(
        ["ffmpeg", "-i", rtsp_url, "-f", "wav", "-ac", "1", "-ar", "16000", "-"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        bufsize=10**8
    )
