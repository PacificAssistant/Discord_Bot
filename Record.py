from discord.ext.voice_recv import AudioSink
from datetime import datetime
from config import RECORDINGS_DIR,RECOGNITION_DIR
import os
from pydub import AudioSegment

class MP3Recorder(AudioSink):
    """ Клас для запису аудіо та збереження у MP3 """

    def __init__(self):
        self.files = {}

    def write(self, user_id, data):
        """ Запис PCM-даних у файл """
        date = datetime.now().strftime("%Y-%m-%d")
        pcm_path = f"{RECORDINGS_DIR}/user_{user_id}_{date}.pcm"

        with open(pcm_path, "ab") as f:
            f.write(data.pcm)  # Важливо зберігати саме data.pcm!


    def cleanup(self):
        """ Конвертація PCM у MP3 """
        for pcm_file in sorted(os.listdir(RECORDINGS_DIR)):
            if pcm_file.endswith(".pcm"):
                file_name = '.'.join(pcm_file.split('.')[:-1])
                pcm_path = os.path.join(RECORDINGS_DIR, pcm_file)
                mp3_path = os.path.join(RECORDINGS_DIR, f"{file_name }.mp3")

                # Конвертація PCM -> WAV -> MP3 (щоб уникнути помилок)
                wav_path = os.path.join(RECOGNITION_DIR, pcm_file).replace(".pcm", ".wav")

                # PCM у WAV
                if os.path.exists(wav_path) :
                    audio = AudioSegment.from_wav(wav_path)
                else:
                    audio = AudioSegment.silent(duration=0)

                audio += AudioSegment.from_raw(
                    pcm_path, sample_width=2, frame_rate=48000, channels=2
                )

                audio.export(wav_path, format="wav")

                # WAV у MP3 (192 kbps)
                audio = AudioSegment.from_wav(wav_path)
                audio.export(mp3_path, format="mp3", bitrate="192k")

                if os.path.exists(pcm_path):
                    os.remove(pcm_path)
                else:
                    pass


    def wants_opus(self):
        """ Запитуємо PCM замість Opus """
        return False

