import argparse
import time
from feather_cast.stream import start_ffmpeg
from feather_cast.processing import process_audio
from feather_cast.database import add_detection, init_db, get_recent_detections

def parse_arguments():
    """Parses command-line arguments for the RTSP stream and optional parameters."""
    parser = argparse.ArgumentParser(description="Bird Sound Detection from RTSP Stream")

    # Required positional arguments
    parser.add_argument("rtsp_url", help="RTSP stream URL")
    parser.add_argument("sample_duration", type=int, help="Duration of each sample in seconds")

    # Optional arguments
    parser.add_argument("--latitude", type=float, default=35.952735467340304, help="Latitude for location metadata")
    parser.add_argument("--longitude", type=float, default=-79.3092613045215, help="Longitude for location metadata")
    parser.add_argument("--min_confidence", type=float, default=0.25, help="Minimum confidence for detections")
    parser.add_argument("--clip_save_dir", type=str, default="bird_audio_clips", help="Directory to save clipped audio")

    return parser.parse_args()

def main():
    args = parse_arguments()

    init_db()

    while True:
        ffmpeg_process = start_ffmpeg(args.rtsp_url)
        audio_data = ffmpeg_process.stdout.read(16000 * 2 * args.sample_duration)
        ffmpeg_process.terminate()

        if audio_data:
            birds = process_audio(audio_data, args.sample_duration, args.clip_save_dir, args.latitude, args.longitude, args.min_confidence)
            for bird in birds:
                add_detection(bird)

        detections = get_recent_detections(5)
        for i, (common_name, scientific_name, confidence, label, file_path, start_time, end_time, timestamp) in enumerate(detections):
            print(f"{i}: {common_name} ({scientific_name}) - Confidence: {confidence:.2f} | File: {file_path} | Time: {start_time}-{end_time} ({timestamp})")

        print("----")
        time.sleep(1)  # Prevent excessive CPU usage

if __name__ == "__main__":
    main()
