# Feather-Cast

Feather-Cast is a command-line tool for capturing RTSP streams, processing the audio with the Python `birdnetlib` library to detect bird species, and storing detections in an SQLite database. A Streamlit interface is included for visualizing recent bird detections.

## Features
- Captures RTSP streams for real-time audio analysis using `ffmpeg`.
- Processes audio with `birdnetlib` to detect bird species and filter detections by confidence.
- Stores detected bird species along with timestamps and audio clips in an SQLite database.
- Provides a Streamlit-based dashboard for viewing recent detections, including Wikipedia and Wikidata integration for species information.

## Installation

Clone the repository:
```bash
git clone https://github.com/yourusername/feather-cast.git
cd feather-cast
```

Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Capturing and Processing RTSP Stream
```bash
python run.py <RTSP_STREAM_URL> <SAMPLE_DURATION>
```
Replace `<RTSP_STREAM_URL>` with the RTSP URL of your audio stream and `<SAMPLE_DURATION>` with the desired length of each processed audio segment in seconds.

Optional parameters:
- `--latitude <LAT>`: Specify latitude for location-based analysis (default: 35.952735467340304)
- `--longitude <LON>`: Specify longitude for location-based analysis (default: -79.3092613045215)
- `--min_confidence <CONF>`: Set the minimum confidence threshold for detections (default: 0.25)
- `--clip_save_dir <DIR>`: Directory to store clipped bird audio segments (default: `bird_audio_clips`)

### Running the Streamlit Dashboard
```bash
streamlit run display_streamlit.py
```
This will start the Streamlit web interface for visualizing recent bird detections, enriched with Wikipedia and Wikidata data.

## Components

### `stream.py`
- Uses `ffmpeg` to extract audio from an RTSP stream.

### `processing.py`
- Runs BirdNET analysis on audio segments.
- Groups detections by species and merges overlapping detections.
- Saves processed detections and clipped audio segments.

### `database.py`
- Manages the SQLite database (`detections.db`).
- Provides functions to initialize the database, add detections, and fetch recent detections.

### `display_streamlit.py`
- Displays recent bird detections in a Streamlit dashboard.
- Fetches additional information from Wikipedia and Wikidata.

### `run.py`
- Main script to capture and process RTSP streams.
- Calls `stream.py` to extract audio and `processing.py` to analyze detections.
- Stores results in `detections.db`.

## Dependencies
- Python 3.x
- `birdnetlib`
- `opencv-python`
- `sqlite3`
- `streamlit`
- `ffmpeg`

## License
MIT License

## Contributing
Feel free to submit issues and pull requests to enhance Feather-Cast!

## Author
[Your Name]

