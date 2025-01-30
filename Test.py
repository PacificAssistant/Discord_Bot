# from pydub import AudioSegment
# import os
#
# # Налаштування параметрів PCM (змініть під ваш файл)
# sample_rate = 48000 # Частота дискретизації
# channels = 2  # Кількість каналів (1 - моно, 2 - стерео)
# sample_width = 2  # Розрядність семпла (2 байти = 16 біт)
#
# # Відкриття PCM-файлу
# pcm_path = "recordings/user_kvant_sveta.pcm"
# mp3_path = "recordings/user_kvant_sveta.mp3"
#
# # Завантаження PCM у формат raw
# audio = AudioSegment.from_raw(
#     pcm_path,
#     format="raw",
#     frame_rate=sample_rate,
#     channels=channels,
#     sample_width=sample_width
# )
#
# # Експорт у MP3
# audio.export(mp3_path, format="mp3", bitrate="192k")
# print("Конвертація завершена: output.mp3")

# from datetime import datetime,timedelta
#
# now = datetime.now().strftime("%Y-%m-%d_%H-%M")
# print(now)
import os

RECORDINGS_DIR = "recordings"

for pcm_file in os.listdir(RECORDINGS_DIR):
    if pcm_file.endswith(".pcm"):
        user_id = pcm_file.split("_")[1].split(".")[0]
        datetime = pcm_file.split("_")[2].split(".")[0]
        print(user_id, datetime)





