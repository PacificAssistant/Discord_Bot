from discord.ext.voice_recv import AudioSink
from datetime import datetime
from config.config import RECORDINGS_DIR, RECOGNITION_DIR
import os
from pydub import AudioSegment
from database.database import SessionLocal
from database.models import User, Audio
import uuid
import re
import speech_recognition as sr


class MP3Recorder(AudioSink):
    """class for record and save audio file"""

    def __init__(self):
        self.files = {}
        self.user_name = None
        self.date = None
        self.pcm_path = None
        self.mp3_path = None
        self.wav_path = None

    def write(self, user_name, data):
        """Запис PCM-даних у файл"""
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
        """Конвертація PCM у MP3"""
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
        try:
            session = SessionLocal()
            username, date = self.extract_user_date(self.mp3_path)
            date_obj = datetime.strptime(date, "%Y-%m-%d").date()
            file_id = self.generate_file_id(username, date)
            audio_add = session.query(Audio).filter_by(file_id=file_id).first()
            user = session.query(User).filter_by(name=username).first()
            if not audio_add:
                new_role = Audio(
                    file_id=file_id,
                    file_path=self.mp3_path,
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
        """Запитуємо PCM замість Opus"""
        return False

    @staticmethod
    def generate_file_id(username: str, created_at: str) -> str:
        unique_id = uuid.uuid5(uuid.NAMESPACE_DNS, f"{username}_{created_at}")
        return str(unique_id)

    @staticmethod
    def extract_user_date(filename: str) -> tuple[str, str]:
        match = re.search(r"user_(.*?)_(\d{4}-\d{2}-\d{2})\.mp3", filename)
        if match:
            return match.group(1), match.group(2)  # user_id, date
        return None, None

    @staticmethod
    def recognize_speech_from_wav(wav_path):
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
