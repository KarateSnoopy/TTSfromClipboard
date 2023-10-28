import pyperclip
import time
import pygame
import psutil, os
import pyttsx3

def should_play_clip(clipText):
    if not clipText.startswith("•"):
        if len(clipText) > 1:
            return True
    return False

def get_formatted_clip(clipText):
    clipText = clipNow.split(":")
    if len(clipText) > 1:
        text = clipText[1]
    else:
        text = clipNow
    text = text.replace("\"", "")
    text = text.replace(":", "")
    text = text.replace("''", "")
    text = text.replace("—", "")        
    text = text.strip()
    return text

p = psutil.Process(os.getpid())
p.nice(psutil.HIGH_PRIORITY_CLASS)
mixer = pygame.mixer
mixer.init()
pygame.init()

engine = pyttsx3.init()
voices = engine.getProperty('voices')
for voice in voices:
    if "David" in voice.name:
        engine.setProperty('voice', voice.id)
        print("Using voice: " + voice.name)
engine.setProperty('rate', 225) 

lastClip = "" 
index = 0

while True:
    time.sleep(0.1)
    clipNow = pyperclip.paste()
    if clipNow != lastClip:    
        index += 1
        lastClip = clipNow
        formattedClip = get_formatted_clip(clipNow)
        if should_play_clip(formattedClip):
            try:                
                print(str(index) + ": " + formattedClip)

                # use pyttsx3 TTS
                engine.save_to_file(formattedClip, 'audio.mp3')
                engine.runAndWait()

                # play speed up audio
                tada = mixer.Sound('audio.mp3')
                channel = tada.play()
                while channel.get_busy():
                    clipNow = pyperclip.paste()
                    if clipNow != lastClip:
                        channel.stop()
                    else:
                        pygame.time.wait(50)
                try:                
                    os.remove("audio.mp3")
                except:
                    pass
            except:
                print("Error playing clip")
