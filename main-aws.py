from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import sys
from tempfile import gettempdir
import pyperclip
import time
import pygame
import psutil, os
import hashlib

def get_aws_mp3(text, filename, voice="Joanna"):
    try:
        # Request speech synthesis
        ssmlText = "<speak><prosody rate=\"125%\">" + text + "</prosody></speak>"
        response = polly.synthesize_speech(Text=ssmlText, OutputFormat="mp3",
                                            VoiceId=voice, TextType="ssml")
    except (BotoCoreError, ClientError) as error:
        # The service returned an error, exit gracefully
        print(error)
        sys.exit(-1)

    # Access the audio stream from the response
    if "AudioStream" in response:
        # Note: Closing the stream is important because the service throttles on the
        # number of parallel connections. Here we are using contextlib.closing to
        # ensure the close method of the stream object will be called automatically
        # at the end of the with statement's scope.
        with closing(response["AudioStream"]) as stream:
            output = filename

            try:
            # Open a file for writing the output as a binary stream
                with open(output, "wb") as file:
                    file.write(stream.read())
            except IOError as error:
                # Could not write to file, exit gracefully
                print(error)
                sys.exit(-1)

    else:
        # The response didn't contain audio data, exit gracefully
        print("Could not stream audio")
        sys.exit(-1)


def should_play_clip(clipText, speakerName):
    if "Save slot" in speakerName:
            return False
    if "Load slot" in speakerName:
            return False
    if not clipText.startswith("•"):
        if len(clipText) > 1:
            return True
    return False

def get_speaker_name(clipText):
    clipText = clipNow.split(":")
    if len(clipText) > 1:
        text = clipText[0]
    else:
        return "Misc"
    text = text.strip()
    numSpaces = len(text.split())-1
    if numSpaces > 2:
        return "Misc"
    if "?" in text:
        return "Unknown"
    return text

def try_makedir(name):
    try:
        os.mkdir(name)
    except:
        pass

def get_formatted_clip(clipText):
    clipText = clipNow.split(":")
    if len(clipText) > 1:
        text = clipText[1]
    else:
        text = clipNow
    numSpacesInSpeaker = len(clipText[0].split())-1
    if numSpacesInSpeaker > 2:
        text = clipNow
    text = text.replace("\"", "")
    text = text.replace(":", "")
    text = text.replace("''", "")
    text = text.replace("—", "")        
    text = text.replace("Snoopy", "you") # removing my char name
    text = text.replace("DerpTown", "your home town") # removing my hometown name
    text = text.strip()
    return text

def get_aws_voice_from_speaker(speakerName):
    voiceName = "Joanna"
    if speakerName == "Misc":
        voiceName = "Joanna"
    elif speakerName == "Snoopy":  # change to your char name if you want to change voices, etc
        voiceName = "Matthew"
    elif speakerName == "Frou-frou":
        voiceName = "Ivy"
    elif speakerName == "Gretchen":
        voiceName = "Ivy"
    return voiceName

session = Session(region_name="us-west-1") # setup AWS Polly using ENV vars or config file according to AWS docs
polly = session.client("polly")

p = psutil.Process(os.getpid())
p.nice(psutil.HIGH_PRIORITY_CLASS)
mixer = pygame.mixer
mixer.init()
pygame.init()

lastClip = "" 
index = 0
try_makedir("cache")

while True:
    time.sleep(0.1)
    clipNow = pyperclip.paste()
    if clipNow != lastClip:    
        index += 1
        lastClip = clipNow
        speakerName = get_speaker_name(clipNow)        
        formattedClip = get_formatted_clip(clipNow)
        if should_play_clip(formattedClip, speakerName):
            try:                
                result = hashlib.sha256(formattedClip.encode())
                try_makedir("cache\\" + speakerName)
                fileName = "cache\\" + speakerName + "\\" + result.hexdigest() + ".mp3"
                if not os.path.isfile(fileName):
                    voiceName = get_aws_voice_from_speaker(speakerName)
                    get_aws_mp3(formattedClip, fileName, voiceName)
                    print(speakerName + ": " + str(index) + ": " + formattedClip)
                else:
                    print(speakerName + ": " + str(index) + ": " + formattedClip + " (cached)")

                tada = mixer.Sound(fileName)
                channel = tada.play()
                while channel.get_busy():
                    clipNow = pyperclip.paste()
                    if clipNow != lastClip:
                        channel.stop()
                    else:
                        pygame.time.wait(50)
            except:
                print("Error playing clip")
