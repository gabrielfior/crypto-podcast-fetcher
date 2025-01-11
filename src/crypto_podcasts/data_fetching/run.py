import uuid
from pathlib import Path

from crypto_podcasts.config import DBConfig
from crypto_podcasts.data_fetching.cosmos_handler import CosmosClient
from crypto_podcasts.data_fetching.download_audio import download_url_to_file
from dotenv import load_dotenv
from joblib import Parallel, delayed
from loguru import logger
from loky import get_reusable_executor
from openai import AzureOpenAI
from openai.types.audio import Transcription
from pydub import AudioSegment, utils

from src.crypto_podcasts.config import WhisperConfig
from src.crypto_podcasts.data_fetching.models import PodcastEpisode

load_dotenv()

# ToDo
# 1. Derive uuid from URL (e.g. hash)
# 2. Make this script runnable atomically (check if URL available in Cosmos, else stop, check if transcript file for URL exists (change name of stored transcript file) - add another step with the full transcript before uploading to Azure)
# 3. Download transcript, chunk, embed into vector storage (in the cloud)
# 4. Create agent for QA
# 5. Make agent run daily, send a daily report of what happened.

###########
DOWNLOAD_AUDIO = False
CHUNK_AUDIOS = False
TRANSCRIBE = False
UPLOAD=True
##########


def export_song_chunk(idx, song_chunk):
    filename = data_folder / f"file-{idx}.mp3"
    song_chunk.export(filename, format="mp3")
    print(f"generated file {filename}")


# audio_url = "https://chrt.fm/track/713ACD/traffic.megaphone.fm/BWG3931113912.mp3?updated=1726549986" #1h19, kasey
audio_url = "https://chtbl.com/track/D3D2E/cdn.simplecast.com/audio/ff28301d-1e3d-4020-b63f-70f47c6c9d63/episodes/36282215-6c80-458e-9055-0b0769a7a280/audio/bcd3594f-93af-4c56-82d1-b94d0c8b6f0e/default_tc.mp3?aid=embed"  # epicenter, redstone
deployment_id = "whisper"  # This will correspond to the custom name you chose for your deployment when you deployed a model."

filepath = Path(__file__).parent / "my_audio.mp3"
if DOWNLOAD_AUDIO:
    download_url_to_file(filepath=filepath, url=audio_url)

if CHUNK_AUDIOS:
    song = AudioSegment.from_mp3(filepath)
    one_minute = 1 * 1000 * 60  # 1s * 1000 ms * 60
    # song_segment_length = 10 * 60 * 1000  # 10 min
    song_segment_length = 10 * 60 * 500  # 5 min
    data_folder = Path(__file__).parent / "data"
    data_folder.mkdir(exist_ok=True)

    executor = get_reusable_executor(max_workers=4)
    chunks = list(enumerate(utils.make_chunks(song, song_segment_length)))
    executor.map(lambda args: export_song_chunk(*args), chunks)


def build_transcript(mp3_file: str) -> Transcription | None:
    mp3_filepath = Path(mp3_file)
    txt_filename = data_folder / f"{mp3_filepath.name}_transcription.txt"
    if txt_filename.exists():
        logger.info(f"file {txt_filename} already exists. Skipping.")
        return
    logger.debug(f'transcribing {mp3_file}')
    result = client.audio.transcriptions.create(
        file=open(mp3_filepath, "rb"), model=deployment_id
    )
    logger.info(f"Transcription for {mp3_filepath.name} generated")
    return result

def dummy(mp3_file: str):
    print(mp3_file)
    return mp3_file



if TRANSCRIBE:
    whisper_config = WhisperConfig()
    client = AzureOpenAI(
        api_key=whisper_config.WHISPER_AZURE_API_KEY,
        api_version=whisper_config.WHISPER_API_VERSION,
        azure_endpoint=whisper_config.WHISPER_API_ENDPOINT,
    )
    # read all docs from data folder

    data_folder = Path(__file__).parent / "data"
    data_folder.mkdir(exist_ok=True)
    mp3_files = sorted(data_folder.glob("*.mp3"))
    print(len(mp3_files))
    parallel = Parallel(n_jobs=5, prefer="threads") # prefer="threads", "loky"
    #output_generator = parallel(delayed(build_transcript)(i) for i in mp3_files)
    print(f'{mp3_files=}')
    all_transcripts = parallel(delayed(dummy)(i) for i in mp3_files)
    
if UPLOAD:
    data_folder = Path(__file__).parent / "data"
    all_transcripts = sorted(data_folder.glob("*_transcription.txt"))
    transcripts_list = []
    for t in all_transcripts:
        with open(t, 'r') as file:
            transcript_content = file.read()
            transcripts_list.append(transcript_content)
    # ToDo - Get text
    full_transcript = '\n'.join(transcripts_list)
    db_config = DBConfig()
    c = CosmosClient(db_config)
    episode = PodcastEpisode(uuid=str(uuid.uuid4()), transcript=full_transcript)
    c.store_episode_if_not_exists(episode)

    print('done')

