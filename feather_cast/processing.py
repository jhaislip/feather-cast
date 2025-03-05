from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
from datetime import datetime
import tempfile
import os
import wave
import logging

# Initialize BirdNET model
analyzer = Analyzer()

# Set up logging for debugging and monitoring
logging.basicConfig(level=logging.INFO)


def merge_audio_segments(original_audio_path, time_ranges, output_path):
    """Merges multiple audio segments into a single file."""
    with wave.open(original_audio_path, "rb") as wav_file:
        frame_rate = wav_file.getframerate()
        channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()

        with wave.open(output_path, "wb") as out_wav:
            out_wav.setnchannels(channels)
            out_wav.setsampwidth(sample_width)
            out_wav.setframerate(frame_rate)

            for start_time, end_time in time_ranges:
                start_frame = int(start_time * frame_rate)
                end_frame = int(end_time * frame_rate)
                wav_file.setpos(start_frame)
                frames = wav_file.readframes(end_frame - start_frame)
                out_wav.writeframes(frames)

    return output_path

def process_audio(audio_chunk, sample_duration, clip_save_dir=None, latitude=None, longitude=None, min_confidence=.25):
    """Process audio with BirdNET, group detections by species, and combine relevant segments."""

    
    # Ensure clip save directory exists
    if clip_save_dir is not None:
        os.makedirs(clip_save_dir, exist_ok=True)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_wav:
        temp_wav.write(audio_chunk)
        temp_wav_path = temp_wav.name

    recording = Recording(
        analyzer,
        temp_wav_path,
        lat=latitude,
        lon=longitude,
        date=datetime.now(),
        min_conf=min_confidence,
    )
    recording.analyze()

    # Group detections by common name
    grouped_detections = {}

    for detection in recording.detections:
        common_name = detection.get("common_name", "Unknown")
        start_time = detection.get("start_time", 0)
        end_time = detection.get("end_time", 0)

        if common_name not in grouped_detections:
            grouped_detections[common_name] = []
        grouped_detections[common_name].append((start_time, end_time))

    results = []

    for common_name, time_ranges in grouped_detections.items():
        # Merge overlapping or adjacent time ranges
        time_ranges.sort()
        merged_ranges = []
        for start, end in time_ranges:
            if merged_ranges and start <= merged_ranges[-1][1] + 1:  # Merge if overlapping or adjacent
                merged_ranges[-1] = (merged_ranges[-1][0], max(merged_ranges[-1][1], end))
            else:
                merged_ranges.append((start, end))

        # Generate a unique output filename
        if clip_save_dir is not None:
            clip_filename = f"{common_name.replace(' ', '_')}_{int(datetime.now().timestamp())}.wav"
            clip_path = os.path.join(clip_save_dir, clip_filename)

            # Merge audio segments and save
            merge_audio_segments(temp_wav_path, merged_ranges, clip_path)
        else:
            clip_path = None

        # Save detection info
        results.append({
            "common_name": common_name,
            "scientific_name": detection.get("scientific_name", ""),
            "confidence": detection.get("confidence", 0),
            "label": detection.get("label", ""),
            "file_path": clip_path,
            "start_time": merged_ranges[0][0],
            "end_time": merged_ranges[-1][1],
        })

    os.unlink(temp_wav_path)  # Remove temp file after processing

    return results
