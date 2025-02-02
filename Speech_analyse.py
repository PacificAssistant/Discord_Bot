import speech_recognition as sr

def recognize_speech_from_wav(wav_path):
    recognizer = sr.Recognizer()  # Ініціалізація розпізнавача

    with sr.AudioFile(wav_path) as source:
        audio_data = recognizer.record(source)  # Зчитування аудіо
        try:
            text = recognizer.recognize_google(audio_data, language="uk-UA")  # Розпізнавання української мови
            return text
        except sr.UnknownValueError:
            return "Не вдалося розпізнати мову"
        except sr.RequestError:
            return "Помилка запиту до Google API"

