import os
import requests
import uuid
from pathlib import Path
from openai import OpenAI
from termcolor import colored
from typing import List
import subprocess

client = OpenAI()  # 環境変数からAPIキーを取得


def download_image(prompt="a white siamese cat") -> str:
    """
    OpenAI APIを使用して画像を生成し、その画像のURLを取得します。

    Args:
        prompt (str): 生成する画像のプロンプト。

    Returns:
        str: 生成された画像のURL。
    """
    print(colored("[+] Downloading image...", "yellow"))

    response = client.images.generate(
        model="dall-e-3",
        prompt=f"{prompt} - できる限りリアルな画像を生成してください。めちゃくちゃ極端な表現描写をしてください",
        size="1024x1024",
        quality="standard",
        n=1,
    )

    image_url = response.data[0].url
    print(colored("[+] Image downloaded successfully!", "green"))
    return image_url


def download_and_save_image(prompt="a white siamese cat") -> str:
    """
    画像をダウンロードして、指定されたパスに保存します。

    Args:
        prompt (str): 生成する画像のプロンプト。

    Returns:
        str: 保存された画像ファイルのパス。
    """
    # 画像URLを取得
    image_url = download_image(prompt)

    # 画像データをダウンロード
    response = requests.get(image_url)
    response.raise_for_status()

    # 保存先のディレクトリを指定
    save_dir = Path("./temp/")
    save_dir.mkdir(parents=True, exist_ok=True)

    # 保存する画像ファイルのパスを生成
    image_file_path = save_dir / f"{uuid.uuid4()}.jpg"

    # 画像データをファイルに書き込む
    with open(image_file_path, "wb") as file:
        file.write(response.content)
    print(colored(f"[+] Image saved successfully: {image_file_path}", "green"))
    return str(image_file_path)


def create_silence_audio(duration: int, silence_path: str):
    """
    指定された秒数の無音オーディオファイルを生成します。

    Args:
        duration (int): 無音の長さ（秒）。
        silence_path (str): 無音オーディオファイルの保存パス。
    """
    cmd = [
        "ffmpeg",
        "-f",
        "lavfi",
        "-i",
        "anullsrc=r=44100:cl=stereo",
        "-t",
        str(duration),
        silence_path,
    ]
    subprocess.run(cmd, check=True)


def create_video_with_audio(
    image_path: str, audio_path: str, silence_duration: int, video_duration: int
) -> str:
    """
    画像と音声を組み合わせて動画を生成します。音声の前後に無音の期間を追加します。

    Args:
        image_path (str): 画像ファイルのパス。
        audio_path (str): 音声ファイルのパス。
        silence_duration (int): 音声の前後に追加する無音の期間（秒）。
        video_duration (int): 動画の長さ（秒）。

    Returns:
        str: 生成された動画のパス。
    """
    # 無音オーディオファイルのパス
    silence_path_before = f"temp/silence_before_{uuid.uuid4()}.mp3"
    silence_path_after = f"temp/silence_after_{uuid.uuid4()}.mp3"

    # 無音オーディオの生成
    create_silence_audio(silence_duration, silence_path_before)
    create_silence_audio(silence_duration, silence_path_after)

    # 無音オーディオを音声ファイルの前後に結合
    combined_audio_path = f"temp/combined_audio_{uuid.uuid4()}.mp3"
    cmd_combine = [
        "ffmpeg",
        "-i",
        silence_path_before,
        "-i",
        audio_path,
        "-i",
        silence_path_after,
        "-filter_complex",
        "[0:a][1:a][2:a]concat=n=3:v=0:a=1",
        combined_audio_path,
    ]
    subprocess.run(cmd_combine, check=True)

    # 生成された動画のパス
    video_id = uuid.uuid4()
    video_path = f"temp/{video_id}.mp4"

    # 画像と結合したオーディオを使用して動画を生成
    cmd_video = [
        "ffmpeg",
        "-loop",
        "1",
        "-i",
        image_path,
        "-i",
        combined_audio_path,
        "-c:v",
        "libx264",
        "-t",
        str(video_duration),
        "-pix_fmt",
        "yuv420p",
        "-vf",
        "fps=24",
        "-c:a",
        "aac",
        "-shortest",
        video_path,
    ]
    subprocess.run(cmd_video, check=True)

    # 生成された動画のパスを返す
    return video_path


def process_json_data(clips: dict) -> dict:
    """
    JSONデータに基づき、画像生成と動画生成を行い、結果をJSONに追加します。

    Args:
        json_data (List[Dict]): 入力JSONデータ。
    """
    for clip in clips["clips"]:
        video_prompt = clip["video_prompt"]
        audio_path = clip["audio_path"]

        # 画像生成
        image_path = download_and_save_image(video_prompt)

        # 動画生成
        video_path = create_video_with_audio(
            image_path, audio_path, silence_duration=0.5, video_duration=10
        )  # 仮の動画の長さを10秒とする

        # 動画パスをJSONに追加
        clip["video_path"] = video_path

    # 結果を表示または保存
    return clips


def concatenate_videos(
    video_paths: List[str], output_path: str = "temp/final_video.mp4"
) -> str:
    """
    複数の動画ファイルを一つの動画に結合します。

    Args:
        video_paths (List[str]): 結合する動画ファイルのパスのリスト。
        output_path (str): 結合された動画を保存するパス。

    Returns:
        str: 結合された動画のパス。
    """
    # 一時的なファイルリストのパス
    filelist_path = "temp/filelist.txt"

    # 一時的なファイルリストを作成
    with open(filelist_path, "w") as filelist:
        for path in video_paths:
            # temp/filelist.txtに対する相対パスを計算
            relative_path = os.path.relpath(path, start=os.path.dirname(filelist_path))
            filelist.write(f"file '{relative_path}'\n")

    # ffmpegを使用して動画を結合
    cmd = [
        "ffmpeg",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        "temp/filelist.txt",
        "-c",
        "copy",
        output_path,
    ]
    subprocess.run(cmd, check=True)

    # 一時的なファイルリストを削除
    os.remove(filelist_path)

    return output_path


def create_combined_video_from_clips(
    json_data: dict, output_path: str = "temp/combined_video.mp4"
) -> str:
    """
    json_dataから全てのクリップの動画パスを読み取り、それらを一つの動画に結合します。

    Args:
        json_data (dict): クリップ情報が含まれた辞書。
        output_path (str): 結合された動画を保存するパス。

    Returns:
        str: 結合された動画のパス。
    """
    # 結合する動画ファイルのパスのリストを取得
    video_paths = [clip["video_path"] for clip in json_data["clips"]]

    return concatenate_videos(video_paths, output_path)


if __name__ == "__main__":
    clips = {
        "clips": [
            {
                "num": 0,
                "title": "自然の美の魅力",
                "text": "自然の美は私たちの心を癒やし、感動させます。",
                "video_prompt": "自然の美しい風景が映るシーンを撮影してください。",
                "theme": "自然の美",
                "audio_path": "tests/test_data/4dbcd83a-b3d5-4d0a-aaf1-a5a8ca61c117.mp3",
                "video_path": "tests/test_data/4097fa1c-deff-4486-af8a-db74b5cf0413.mp4",
            },
            {
                "num": 1,
                "title": "命の息吹",
                "text": "自然は命を宿し、息づいている。",
                "video_prompt": "自然の息吹を感じさせるショットを撮影してください。",
                "theme": "自然の美",
                "audio_path": "tests/test_data/3748d4e4-1283-4ac3-85e5-7f989855e125.mp3",
                "video_path": "tests/test_data/53a2bd86-5968-4d8e-9e59-abf2ba0c59c3.mp4",
            },
        ]
    }

    # 画像生成から各クリップの動画生成までの処理をテスト
    updated_clips = process_json_data(clips)
    print("画像と動画が生成されました。")

    # 動画の結合処理をテスト
    create_combined_video_from_clips(clips)
    print("結合後の動画が生成されました。")
