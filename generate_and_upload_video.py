import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from termcolor import colored
from dotenv import load_dotenv
from src.generate_video import topic2video
from src.generate_ideas import generate_ideas

# Load environment variables from .env file
load_dotenv()

# 認証情報の設定
CLIENT_SECRETS_FILE = os.getenv("CLIENT_SECRETS_FILE")
SCOPES = [os.getenv("SCOPES")]
API_SERVICE_NAME = os.getenv("API_SERVICE_NAME")
API_VERSION = os.getenv("API_VERSION")


def get_authenticated_service():
    credentials = None
    # Check if user's access token and refresh token are saved in token.pickle file
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            credentials = pickle.load(token)
    # If there are no valid credentials, prompt the user to login
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES
            )
            credentials = flow.run_local_server(port=0)
        # Save the credentials for next time
        with open("token.pickle", "wb") as token:
            pickle.dump(credentials, token)

    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)


def upload_video(youtube, file, title, description, category, keywords, privacyStatus):
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": keywords.split(","),
            "categoryId": category,
        },
        "status": {"privacyStatus": privacyStatus},
    }

    # Upload the video file
    media = MediaFileUpload(file, chunksize=-1, resumable=True)
    request = youtube.videos().insert(
        part=",".join(body.keys()), body=body, media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print("Uploaded %d%%." % int(status.progress() * 100))
    print("Upload Complete.")


if __name__ == "__main__":
    meta_topic = "1000年後の世界について"
    num_ideas = 5

    youtube = get_authenticated_service()
    category = os.getenv("CATEGORY")
    privacyStatus = os.getenv("PRIVACY_STATUS")

    ideas = generate_ideas(meta_topic, num_ideas)
    print(colored("[+] Generating ideas...", "yellow"))  # Progress message
    print(ideas)

    num_clips = 5
    for idea in ideas["ideas"]:
        video_subject = idea
        output_file_path = f"./output/{video_subject}.mp4"
        video_path, updated_clips = topic2video(video_subject, num_clips, output_file_path)

        description = updated_clips["description"]
        keywords = updated_clips["topic"]
        category = updated_clips["category"]

        title = updated_clips["title"]
        upload_video(youtube, video_path, title, description, category, keywords, privacyStatus)
