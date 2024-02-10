# Youtube-short creater with BERT-VITS2 & DALLE-3 & ChatGPT 🚀

Automate the creation of YouTube Shorts locally, simply by providing a video topic to talk about.

[![ビデオの例](docs/thumbnail.png)](https://www.youtube.com/shorts/Eah3Pb9s2Kk "例を見る")


## Installation 📥

`YoutubeShortCreator` requires Python 3.11 to run effectively. If you don't have Python installed, you can download it from [here](https://www.python.org/downloads/).

After you finished installing Python, you can install `YoutubeShortCreator` by following the steps below:

```bash
git clone https://github.com/avonx/youtube_short.git
cd YoutubeShortCreator

# Install requirements
pip install -r requirements.txt

# Copy .env.example and fill out values
cp .env.example .env

# Run the python program
python generate_video.py

# Alternatively, run this to upload videos to youtube automatically.
python upload_video.py
```

See [`.env.example`](.env.example) for the required environment variables.

## Usage 🛠️

1. Copy the `.env.example` file to `.env` and fill in the required values
2. Run this command `python generate_video.py`
3. Enter a topic to talk about
4. Wait for the video to be generated
5. The video's location is `output/<タイトルは自動的に生成されます>.mp4`


## Automatic YouTube Uploading 🎥

To use this feature, you need to:

1. Create a project inside your Google Cloud Platform -> [GCP](https://console.cloud.google.com/).
2. Obtain `client_secret.json` from the project and add it to the Backend/ directory.
3. Enable the YouTube v3 API in your project -> [GCP-API-Library](https://console.cloud.google.com/apis/library/youtube.googleapis.com)
4. Create an `OAuth consent screen` and add yourself (the account of your YouTube channel) to the testers.
5. Enable the following scopes in the `OAuth consent screen` for your project:

```
'https://www.googleapis.com/auth/youtube.upload'
```

## License 📝

See [`LICENSE`](LICENSE) file for more information.
