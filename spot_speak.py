import speech_recognition as sr

def listen():
    # Initialize recognizer
    r = sr.Recognizer()

    # Open the microphone and start recording
    with sr.Microphone() as source:
        print("Say something!")
        audio = r.listen(source)

    # Using Google's speech recognition to recognize Lithuanian
    try:
        text = r.recognize_google(audio, language='lt-LT')
        print("You said: " + text)
        return text
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
        return None
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return None
    

from groq import Groq
import os

os.environ["GROQ_API_KEY"] = "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"


def respond(text):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"),)
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "you are a helpful assistant called Spot; you only speak in lithuanian; tell funny jokes"
            },
            {
                "role": "user",
                "content": text,
            }
        ],
        model="llama3-70b-8192",
        temperature=0.1,
        max_tokens=1024,
        top_p=1,
        stop=None,
        stream=False,
    )

    return chat_completion.choices[0].message.content



from TTS.api import TTS
import simpleaudio as sa
import numpy as np
import threading
import queue
import time

tts = TTS(model_name='tts_models/lt/cv/vits')

# Create a queue to hold text entries
text_queue = queue.Queue()
audio_queue = queue.Queue()

def tts_worker():

    while True:
        # Wait for text to be available in the queue
        text = text_queue.get()
        sound = tts.tts(text=text)
        sound = np.array(sound)
        sound = sound * (2**15 - 1) / np.max(np.abs(sound))
        sound = sound.astype(np.int16)
        audio_queue.put(sound)
        
def audio_player():
    while True:
        sound = audio_queue.get()
        play_obj = sa.play_buffer(sound, 1, 2, 22050)
        play_obj.wait_done()

def enqueue_text(text):
    text_queue.put(text)



sit_acrivation_list = ['sėsk', 'atsisėsk', 'sedėt', 'sit', 'gult', 'atsigulk', 'sėdėt', 'gulėt', 'gulet', 'sedėti', 'gulėti']
walk_forward_activation_list = ['pirmyn', 'į priekį', 'forwards', 'go']
walk_backwards_activation_list = ['atgal', 'atbulom', 'backwards']
stand_activation_list = ['atsistok', 'stovėk', 'stand', 'stovėti', 'stot', 'stovėti']

def voice_control(command):
    cmd = None
    for sit_cmd in sit_acrivation_list:
        for find_cmd in command.split(' '):
            if find_cmd == sit_cmd:
                    # Sit command
                    cmd = 'v'
    for forward_cmd in walk_forward_activation_list:
        for find_cmd in command.split(' '):
            if find_cmd == forward_cmd:
                # Forward command
                cmd = 'w'
    for backward_cmd in walk_backwards_activation_list:
        for find_cmd in command.split(' '):
            if find_cmd == backward_cmd:
                # Backward command
                cmd = 's'
    for stand_cmd in stand_activation_list:
        for find_cmd in command.split(' '):
            if find_cmd == stand_cmd:
                # Backward command
                cmd = 'f'
    for find_cmd in command.split(' '):
        if find_cmd == 'stop':
            # stop
            cmd = ' '
    for find_cmd in command.split(' '):
        if find_cmd == 'apsisuk':
            cmd = 'q'
    for find_cmd in command.split(' '):
        if find_cmd == 'įsijunk':
            cmd = 'p'

    return cmd


# Start the TTS worker in a separate thread
threading.Thread(target=tts_worker, daemon=True).start()
threading.Thread(target=audio_player, daemon=True).start()


def main():
    while True:
        text = listen()  # Listen for speech
        #text = input()
        if text:
            response = respond(text)  # Generate a response
            print(response)
            for sentance in response.split('.'):
                # Example of enqueuing text
                if sentance != '':
                    enqueue_text(sentance) # Speak out the response
                    time.sleep(0.1)  

        # command = input("Continue? (yes/no): ")
        # if command.lower() != "yes":
        #     break


# if __name__ == "__main__":
#      main()
