from pathlib import Path
from termcolor import colored

from src.generate_ideas import generate_ideas
from src.topic2text import generate_script
from src.text2voice import generate_audio_for_clips
from src.voice2video import process_json_data, create_combined_video_from_clips


def topic2video(video_subject, num_clips, output_file_path):
    # Create or clear the temp folder
    temp_folder = Path("./temp")
    temp_folder.mkdir(exist_ok=True)
    for file in temp_folder.glob("*"):
        file.unlink()

    clips = generate_script(video_subject, num_clips)
    print(colored("[+] Generating script...", "yellow"))
    print(clips)

    updated_clips = generate_audio_for_clips(clips)
    print(colored("[+] Generating audio for clips...", "yellow"))
    print(updated_clips)

    updated_clips = process_json_data(updated_clips)
    print(colored("[+] Processing JSON data...", "yellow"))
    print(updated_clips)

    video_path = create_combined_video_from_clips(
        updated_clips, output_file_path)
    print(colored("[+] Creating combined video...", "yellow"))

    # Delete temporary files
    for file in temp_folder.glob("*"):
        file.unlink()

    return video_path, updated_clips


if __name__ == "__main__":
    # どのような動画を作成するか大まかに指定
    meta_topic = "科学に関する話題を具体的に。"
    # 何本の動画アイデアを生成するか指定
    num_ideas = 3
    ideas = generate_ideas(meta_topic, num_ideas)
    print(colored("[+] Generating ideas...", "yellow"))
    print(ideas)

    # アイデアの数だけ動画を生成、具体的なトピックはgpt APIで生成
    for idea in ideas["ideas"]:
        video_subject = idea
        # １動画あたりのクリップ数
        num_clips = 5
        output_file_path = f"./output/{video_subject}.mp4"
        video_path, updated_clips = topic2video(
            video_subject, num_clips, output_file_path)
