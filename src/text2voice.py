import requests
from pydub import AudioSegment
import io
import uuid
from pathlib import Path
from termcolor import colored

# tempフォルダのパスを定義（存在しない場合は作成）
temp_folder = Path("./temp")
temp_folder.mkdir(exist_ok=True)


def generate_audio_for_clips(clips):
    """
    Generate audio files for each clip in the given list.

    Args:
        clips (list): A list of clips, where each clip is a dictionary containing the "text" key.

    Returns:
        None
    """
    for clip in clips["clips"]:
        filename = f"{str(uuid.uuid4())}.mp3"
        filepath = temp_folder / filename  # 保存するファイルパス
        text = clip["text"]  # 音声に変換するテキスト

        combined_audio = process_and_combine_audio(text)
        if combined_audio:
            combined_audio.export(filepath, format="mp3")
            clip["audio_path"] = str(filepath)  # 生成した音声ファイルのパスをJSONに追加
        else:
            clip["audio_path"] = None  # 音声生成に失敗した場合
    return clips


def process_and_combine_audio(text: str) -> AudioSegment:
    """
    Process and combine audio segments for each paragraph in the given text.

    Args:
        text (str): The input text.

    Returns:
        AudioSegment: The combined audio segment.

    """
    text_no_newlines = text.replace("\n\n", "")
    paragraphs = [f"{p}。" for p in text_no_newlines.split("。") if p]

    combined_audio = None
    for i, paragraph in enumerate(paragraphs):
        print(
            colored(f"[+] Processing paragraph {i+1}/{len(paragraphs)}...", "yellow"))
        audio_content = get_tts_audio(paragraph)
        if audio_content:
            current_audio = AudioSegment.from_file(
                io.BytesIO(audio_content), format="wav")
            silence = AudioSegment.silent(duration=1000)  # 1秒の無音を追加
            combined_audio = combined_audio + silence + \
                current_audio if combined_audio else current_audio
    return combined_audio


def get_tts_audio(text: str) -> bytes:
    """
    Get text-to-speech audio for the given text.

    Args:
        text (str): The text to convert to audio.

    Returns:
        bytes: The audio content in bytes if successful, None otherwise.
    """
    url = "https://igeb37tgif2guh-5000.proxy.runpod.net/voice"
    params = {
        "text": text,
        "encoding": "utf-8",
        "model_id": 4,
        "speaker_id": 0,
        "sdp_ratio": 0.6,
        "noise": 0.7,
        "noisew": 1.1,
        "length": 0.75,
        "language": "JP",
        "auto_split": True,
        "split_interval": 0.5,
        "assist_text_weight": 1,
        "style": "Neutral",
        "style_weight": 5,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200 and "audio/wav" in response.headers.get("Content-Type"):
        return response.content
    return None


if __name__ == "__main__":
    # JSONデータを処理するための例
    clips = {
        "clips": [
            {
                "num": 0,
                "title": "サンプルタイトル",
                "text": "これはサンプルのテキストです。宇宙人はいます。会ったことがあります！",
                "video_prompt": "静かな森の風景を描写する文章。",
            },
            # 他のクリップ...
        ]
    }

    updated_clips = generate_audio_for_clips(clips)

    # 結果を確認
    print(updated_clips)
