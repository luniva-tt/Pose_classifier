import cv2
import numpy as np
import mediapipe as mp
import os
import pandas as pd
import shutil
import json
import json
import os
import time
import random

from moviepy.video.io.VideoFileClip import VideoFileClip

youtube_downloader = "yt-dlp"

def download_yt_videos(indexfile, saveto='raw_videos', n_videos = 5526):
    content = json.load(open(indexfile))

    if not os.path.exists(saveto):
        os.mkdir(saveto)

    #total_videos = n_videos
    downloaded_videos = 0

    for entry in content:
        pose = entry['pose']
        instances = entry['instances']

        for inst in instances:
            video_url = inst['url']
            video_id = inst['sequence_id']

            if 'youtube' not in video_url and 'youtu.be' not in video_url:
                continue

            if os.path.exists(os.path.join(saveto, video_url[-11:] + '.mp4')) or os.path.exists(os.path.join(saveto, video_url[-11:] + '.mkv')):
                print('YouTube videos {} already exists.'.format(video_url))
                continue
            else:
                cmd = f"{youtube_downloader} \"{{}}\" -o \"{{}}%(id)s.%(ext)s\""
                cmd = cmd.format(video_url, saveto + os.path.sep)

                rv = os.system(cmd)

                if not rv:
                    print(f'Finish downloading youtube video url {video_url}')
                else:
                    print(f'Unsuccessful downloading - youtube video url {video_url}')

                downloaded_videos += 1
                progress = (downloaded_videos / n_videos) * 100
                print(f'Video {video_id} downloaded successfully! Progress: {progress:.2f}%')
                # please be nice to the host - take pauses and avoid spamming
                time.sleep(random.uniform(1.0, 1.5))


def convert_everything_to_mp4(src_path = 'raw_videos', overwrite=False):
    # Set the destination path
    dst_path = os.path.join(os.path.dirname(src_path), 'raw_videos_mp4')

    # Create the destination folder if it doesn't exist
    if not os.path.exists(dst_path):
        os.makedirs(dst_path)

    for root, _, files in os.walk(src_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            file_basename, extension = os.path.splitext(filename)

            if extension.lower() == '.mp4':
                # For .mp4 files, simply copy to the destination folder
                new_file_path = os.path.join(dst_path, filename)
                if overwrite or not os.path.exists(new_file_path):
                    print(f"Coping {filename} to {dst_path}")
                    shutil.copy(file_path, new_file_path)
                    print(f"Copied {filename} to {dst_path}")
                else:
                    print(f"File {filename} already exists in {dst_path}. Skipping.")
            else:
                try:
                    # For non-.mp4 files, rename the extension to .mp4
                    new_filename = file_basename + ".mp4"
                    new_file_path = os.path.join(dst_path, new_filename)
                    if overwrite or not os.path.exists(new_file_path):
                        print(f"Converting {filename} to {new_filename}")
                        shutil.copy(file_path, new_file_path)
                        print(f"Converted {filename} to {new_filename}")
                    else:
                        print(f"File {new_filename} already exists in {dst_path}. Skipping.")
                except Exception as e:
                    print(f"Failed to convert {filename}: {str(e)}")



def process_videos(json_file, raw_folder='raw_videos_mp4', trimmed_folder='trimmed_mp4'):
    # Load the JSON file
    with open(json_file, 'r') as file:
        data = json.load(file)

    # Create trimmed folder if it doesn't exist
    os.makedirs(trimmed_folder, exist_ok=True)

    # Process each video
    for item in data:
        pose = item['pose']
        for instance in item['instances']:
            sequence_id = instance['sequence_id']
            url = instance['url']
            frame_start = instance['frame_start']-1
            frame_end = instance['frame_end']+1

            # Construct filenames
            # video_file = os.path.join(raw_folder, f'{url_id}.mp4')
            # output_file = os.path.join(trimmed_folder, f'{pose}_{sequence_id}.mp4')
            
            yt_identifier = url[-11:]
            video_file = os.path.join(raw_folder, yt_identifier + '.mp4')
            video_id = str(instance['sequence_id'])  # Convert video_id to string
            output_file = os.path.join(trimmed_folder, video_id + '.mp4')

            # Check if video exists
            if os.path.exists(video_file):
                print("file exists")
                # Open video
                cap = cv2.VideoCapture(video_file)
                fps = int(cap.get(cv2.CAP_PROP_FPS))
                start_frame = int(frame_start * fps)
                end_frame = int(frame_end * fps)

                # Set up video writer
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

                # Trim the video
                cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
                frame_number = start_frame
                while frame_number <= end_frame:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    out.write(frame)
                    frame_number += 1

                # Release resources
                cap.release()
                out.release()

                # Remove the original file
                # os.remove(video_file)
            else:
                print("file doesnt exist")
                print(video_file)

def main():
    # 1. Convert .swf, .mkv file to mp4.
    # download_yt_videos('mountain.json')

    # convert_everything_to_mp4()

    # 2. Cut the videos and create sequences.
    process_videos('mountain.json')

if __name__ == "__main__":
    main()