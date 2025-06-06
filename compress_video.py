import subprocess

def compress_video(input_file, output_file, bitrate='800k', resolution='1280x720'):
    """Compresses a video using FFmpeg.

    Args:
        input_file (str): Path to the input video file.
        output_file (str): Path to the output compressed video file.
        bitrate (str, optional): Video bitrate (e.g., '800k'). Defaults to '800k'.
        resolution (str, optional): Video resolution (e.g., '1280x720'). Defaults to '1280x720'.
    """

    command = [
        'ffmpeg',
        '-i', input_file,
        '-b:v', bitrate,
        '-vf', f'scale={resolution}',
        output_file
    ]

    try:
        subprocess.run(command, check=True)
        print(f"Video compressed and saved to {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error compressing video: {e}")

if __name__ == '__main__':
    input_video = 'input.mp4' # Replace with your input video file
    output_video = 'output.mp4' # Replace with your desired output video file
    compress_video(input_video, output_video)