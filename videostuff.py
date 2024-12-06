import os
import csv
import ffmpeg

#mostly from chatgpt
video_directory = "Z:\\"
output_csv = "video_metadata.csv"
errorFile = open('error_file_list.txt', 'w')

def get_video_metadata(file_path):
    try:
        probe = ffmpeg.probe(file_path)
        format_info = probe.get("format", {})
        streams = probe.get("streams", [])
        
        # Get the first video stream
        video_stream = next((stream for stream in streams if stream["codec_type"] == "video"), {})
        audio_stream = next((stream for stream in streams if stream["codec_type"] == "audio"), {})
        
        # Extract relevant information
        container = format_info.get("format_name", "Unknown")
        resolution = f'{video_stream.get("width", 0)}x{video_stream.get("height", 0)}'
        codec = video_stream.get("codec_name", "Unknown")
        framerate = eval(video_stream.get("avg_frame_rate", "0"))  # Converts "30/1" to 30
        bit_depth = video_stream.get("bits_per_raw_sample", "Unknown")
        audio_codec = audio_stream.get("codec_name", "Unknown")
        audio_channels = audio_stream.get("channels", "Unknown")
        bitrate = int(format_info.get("bit_rate", 0)) / 1_000_000  # Convert to Mbps
        
        return {
            "Path": file_path,
            "Name": os.path.basename(file_path),
            "Container": container,
            "Resolution": resolution,
            "Video Codec": f"{codec} (level {video_stream.get('profile', 'Unknown')})",
            "Framerate": f"{framerate} fps (bit depth: {bit_depth})",
            "Audio Codec": f"{audio_codec} ({audio_channels} channels)",
            "Bitrate": f"{bitrate:.2f} Mbps"
        }
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        errorFile.write(f'{file_path} failed due to {e}\n')
        return None

def main():
    # List to store metadata
    metadata_list = []
    count = 0
    # Walk through the directory and process video files
    for root, _, files in os.walk(video_directory):
        for file in files:
            file_path = os.path.join(root, file)
            if file.lower().endswith((".mp4", ".mkv", ".avi", ".mov", ".dv")):  # Add other extensions as needed
                metadata = get_video_metadata(file_path)
                if metadata:
                    metadata_list.append(metadata)
                    count += 1
            if (count%1000 == 0):
                print(f'{count} files counted.')
    
    # Write to a CSV file
    with open(output_csv, mode="w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["Path", "Name", "Container", "Resolution", "Video Codec", "Framerate", "Audio Codec", "Bitrate"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(metadata_list)
    
    print(f"Metadata saved to {output_csv}")

main()