import json
from termcolor import colored
from openai import OpenAI

client = OpenAI()


def generate_script(video_subject: str, num_clips: int) -> dict:
    """
    ビデオの主題に応じたスクリプトを生成する。

    Args:
        video_subject (str): ビデオの主題
        num_clips (int): クリップ数

    Returns:
        dict: 生成されたスクリプト

    Raises:
        json.JSONDecodeError: スクリプトの生成に失敗した場合に発生する例外
    """
    # プロンプトの構築
    prompt_valuables = f"""
    ビデオの主題に応じたスクリプトを生成してください。
    主題: {video_subject}
    クリップ数: {num_clips}
    """

    prompt_format = """
    次の形式のjsonで出力するようにしてください。
    {
    "title": str（ビデオのタイトル）,
    "description": str（ビデオの説明）,
    "topic": str（ビデオのトピック）,
    "category" = str（YouTubeのカテゴリID）,
    "clips": [
    {
        "num": int（そのクリップの番号、0から始まる）,
        "title": str（そのクリップのタイトル）,
        "text": str（そのクリップで読み上げる文章、1文だけ。）,
        "video_prompt": str（画像生成のための描写用の文章）,
        "subtitles": "str（そのクリップの字幕）
    },..]
    }

    1クリップは、常に１文で簡潔に記述してください。
    youtubeのショートです。
    具体的に、短い文章でニュース風に書いてください。
    オチをしっかりつけるように。
    センセーショナルにした方が面白いです。
    具体的な情報提供をするような内容にしてください。
    youtubeのショートです。

    例）
    {
    "title": "宇宙の謎",
    "description": "宇宙の謎に迫るビデオです。",
    "topic": "宇宙、SF、科学",
    "category" = "22"  # YouTubeのカテゴリID（例: "22"はPeople & Blogsカテゴリを示す）
    "clips": [
    {
        "num": 0,
        "title": "導入:広大な宇宙",
        "text": "宇宙は広大で、私たちの理解を超えています。",
        "video_prompt": "巨大な銀河が渦巻く様子を描写してください。",
        "subtitles": "宇宙は広大で、私たちの理解を超えています。"
    },
    {
        "num": 1,
        "title": "この宇宙の謎",
        "text": "そのため、まだわからないことも数多くあります。",
        "video_prompt": "巨大な？マークが画面中央にあるショットを撮影してください。",
    }
    ...
    ]
    }
    """
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        # model="gpt-3.5-turbo-1106",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": f"次の文章からJSONを生成してください。\n{prompt_valuables}{prompt_format}",
            },
        ],
        response_format={"type": "json_object"},
    )

    script = response.choices[0].message.content.strip()
    # scriptをjsonに変換
    try:
        script = json.loads(script)
        return script
    except json.JSONDecodeError as e:
        print(colored("スクリプトの生成に失敗しました。", "red"))
        print(colored("エラー内容: ", "red"), e)
        return None


if __name__ == "__main__":
    video_subject = "宇宙の謎"
    num_clips = 2
    script = generate_script(video_subject, num_clips)
    print(script)
    print("\n")

    video_subject = "自然の美"
    num_clips = 3
    script = generate_script(video_subject, num_clips)
    print(script)
    print("\n")
