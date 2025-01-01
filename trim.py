import os
import json
import cv2

def process_videos(json_file, raw_folder='mountain', trimmed_folder='trimmed_mp4'):
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

# Example usage
process_videos('mountain.json')
