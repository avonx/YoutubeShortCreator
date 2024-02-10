from openai import OpenAI
import json
from termcolor import colored

client = OpenAI()


def generate_ideas(meta_topic: str, num_ideas: int) -> dict:
    """
    メタトピックについて、アイデアを生成する。
    """
    # プロンプトの構築
    prompt_valuables = f"""
    下記のメタトピックに応じて、youtubeのショート動画のアイデアを考えてください。

    主題: {meta_topic}
    出力するアイデアの個数: {num_ideas}
    """

    prompt_format = """
    次の形式のjsonで出力するようにしてください。
    "ideas": [
        "アイデア1", "アイデア2", ...
    ]

    例）
    "ideas": [
        "実は宇宙人はすでに紛れ込んでいる", "ドラえもんが怒った時に何が起こるか", ...
    ]
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
    meta_topic = "SFチックな、ちょっとオカルトな話を具体的に。"
    num_ideas = 2
    ideas = generate_ideas(meta_topic, num_ideas)
    print(ideas)
