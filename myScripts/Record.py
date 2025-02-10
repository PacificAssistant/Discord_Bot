from discord.ext.voice_recv import AudioSink
from datetime import datetime
from config.config import RECORDINGS_DIR, RECOGNITION_DIR,BASE_DIR
import os
from pydub import AudioSegment
from database.database import SessionLocal
from database.models import User, Audio
import uuid
import re
import speech_recognition as sr


class MP3Recorder(AudioSink):
    """A class for recording, converting, and managing audio data from Discord voice channels.

    This class handles recording of PCM audio data, conversion to MP3/WAV formats, and
    integration with speech recognition services. It also manages database storage of
    recorded audio files.

    Attributes:
        files (dict): Storage for file handles.
        user_name (str): Name of the user being recorded.
        date (str): Current date in YYYY-MM-DD format.
        pcm_path (str): Path to the temporary PCM file.
        mp3_path (str): Path to the converted MP3 file.
        wav_path (str): Path to the WAV file used for speech recognition.
    """
    def __init__(self):
        self.files = {}
        self.user_name = None
        self.date = None
        self.pcm_path = None
        self.mp3_path = None
        self.wav_path = None

    def write(self, user_name, data):
        """Writes PCM audio data to a file for a specific user.

           Creates necessary file paths and writes incoming PCM audio data to a temporary file.

           Args:
               user_name (str): The name of the user being recorded.
               data: The PCM audio data from Discord.

           Returns:
               None
           """
        self.date = datetime.now().strftime("%Y-%m-%d")
        self.user_name = user_name
        self.pcm_path = os.path.join(
            RECORDINGS_DIR, f"user_{user_name}_{self.date}.pcm"
        )
        self.mp3_path = os.path.join(
            RECORDINGS_DIR, f"user_{user_name}_{self.date}.mp3"
        )
        self.wav_path = os.path.join(
            RECOGNITION_DIR, f"user_{user_name}_{self.date}.wav"
        )

        with open(self.pcm_path, "ab") as f:
            f.write(data.pcm)  # Важливо зберігати саме data.pcm!


    def cleanup(self):
        """Converts recorded PCM data to MP3 and WAV formats.

            Processes all PCM files in the recordings directory:
            1. Converts PCM to WAV format
            2. Converts WAV to MP3 format (192 kbps)
            3. Cleans up temporary PCM files
            4. Adds the MP3 file to the database

            Returns:
                None
            """
        for pcm_file in sorted(os.listdir(RECORDINGS_DIR)):
            if pcm_file.endswith(".pcm"):

                # PCM у WAV
                if os.path.exists(self.wav_path):
                    audio = AudioSegment.from_wav(self.wav_path)
                else:
                    audio = AudioSegment.silent(duration=0)

                audio += AudioSegment.from_raw(
                    self.pcm_path, sample_width=2, frame_rate=48000, channels=2
                )

                audio.export(self.wav_path, format="wav")

                # WAV у MP3 (192 kbps)
                audio = AudioSegment.from_wav(self.wav_path)
                audio.export(self.mp3_path, format="mp3", bitrate="192k")

                if os.path.exists(self.pcm_path):
                    os.remove(self.pcm_path)
                else:
                    pass
                self.add_mp3_to_db()

    def add_mp3_to_db(self):
        """Adds the converted MP3 file information to the database.

            Creates or updates an Audio record in the database with the file information
            and user association.

            Returns:
                None

            Raises:
                Exception: If database operations fail.
            """
        try:
            session = SessionLocal()
            username, date = self.extract_user_date(self.mp3_path)
            date_obj = datetime.strptime(date, "%Y-%m-%d").date()
            file_id = self.generate_file_id(username, date)
            audio_add = session.query(Audio).filter_by(file_id=file_id).first()
            user = session.query(User).filter_by(name=username).first()
            relative_file_path = os.path.relpath(self.mp3_path,BASE_DIR)
            if not audio_add:
                new_role = Audio(
                    file_id=file_id,
                    file_path=relative_file_path,
                    created_at=date_obj,
                    user_id=user.id,
                )
                session.add(new_role)
            session.commit()

        except Exception as e:
            print(f"Error ocurred : {e}")
        finally:
            session.close()

    def wants_opus(self):
        """Indicates whether the recorder wants Opus format audio.

           Returns:
               bool: Always returns False as this recorder works with PCM data.
           """
        return False

    @staticmethod
    def generate_file_id(username: str, created_at: str) -> str:
        """Generates a unique file ID using UUID5.

            Args:
                username (str): The username of the recorded user.
                created_at (str): The date of recording in YYYY-MM-DD format.

            Returns:
                str: A unique UUID5 string generated from username and date.
            """
        unique_id = uuid.uuid5(uuid.NAMESPACE_DNS, f"{username}_{created_at}")
        return str(unique_id)

    @staticmethod
    def extract_user_date(filename: str) -> tuple[str, str]:
        """Extracts username and date from a recording filename.

            Args:
                filename (str): The full path or filename of the recording.

            Returns:
                tuple[str, str]: A tuple containing (username, date).
                    Returns (None, None) if the filename doesn't match the expected pattern.
            """
        match = re.search(r"user_(.*?)_(\d{4}-\d{2}-\d{2})\.mp3", filename)
        if match:
            return match.group(1), match.group(2)  # user_id, date
        return None, None

    @staticmethod
    def recognize_speech_from_wav(wav_path):
        """Performs speech recognition on a WAV file using Google's speech recognition API.

            Args:
                wav_path (str): Path to the WAV file to be processed.

            Returns:
                str: The recognized text in Ukrainian, or an error message if recognition fails.

            Raises:
                sr.UnknownValueError: If speech cannot be recognized.
                sr.RequestError: If there's an error with the Google API request.
            """
        recognizer = sr.Recognizer()  # Ініціалізація розпізнавача

        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)  # Зчитування аудіо
            try:
                text = recognizer.recognize_google(
                    audio_data, language="uk-UA"
                )  # Розпізнавання української мови
                return text
            except sr.UnknownValueError:
                return "Не вдалося розпізнати мову"
            except sr.RequestError:
                return "Помилка запиту до Google API"
