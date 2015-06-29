#!/usr/bin/env python

"""
make-chatterbot
by Brandon Jackson
"""

import aiml
import subprocess
import os
import argparse
from MyKernel import MyKernel
import speech_recognition as sr

import firmata as f
import numpy as np

PRESENTATION_MODE = 0 # TODO Change this to a parse argument. It causes no written ouput. 

a = f.Arduino('/dev/ttyACM99', baudrate=57600)
# Eyes:
left_eye = 3
right_eye = 9
a.pin_mode(left_eye, f.OUTPUT)
a.pin_mode(right_eye, f.OUTPUT)

def setEyes(state, eye='both'):
    if state == 1:
        state = f.HIGH
    else:
        state = f.LOW

    if eye == 'both':
        a.digital_write(left_eye, state)
        a.digital_write(right_eye, state)
    if eye == 'left':
        a.digital_write(left_eye, state)
    if eye == 'right':
        a.digital_write(right_eye, state)

# Head:
head = 5

def setHead(position):
    a.pin_mode(head, f.SERVO)
    if position < -25:
        position = -25
    if position > 25:
        position = 25
    position = 85 + position
    a.analog_write(head, position)
    a.delay(1)
    a.pin_mode(head, f.OUTPUT)


BOT_PREDICATES = {
    "name": "Vreni",
    "birthday": "November 24th 1986",
    "location": "Munich",
    "master": "Korbi",
    "botmaster": "Creator",
    "website":"",
    "gender": "female",
    "age": "28",
    "size": "19 MB",
    "religion": "Atheist",
    "party": "FAP - fuck all parties",
    "birthplace": "Chiba",
    "email": "ebsor@gmx.de",
    "favoritecolor": "grey",
    "favoritemovie": "Electric Dreams",
    "favoriteactress": "Sigourney Weaver",
    "kindmusic": "IDM and Breakcore",
    "friend": "Korbi",
    "fullname": "VRENI",
    "gender": "kind of female",
    "has": "cabinet",
    "he": "usually Kami",
    "sign": "Saggitarius",
    "job": "Serving Korbi",
    "lastname": "also Vreni",
    "looklike": "Omni Junior",
    "vocabulary": "50000 Words",
    "middlename": "Vreni",
    "personality": "mad",
    "wife": "Vreni",
    "nationality": "Japanese",
    "country": "Germany",
    "city": "Munich",
    "state": "Bavaria",
    "race": "robot",
    "domain": "robot",
    "family": "Tomy Robots",
    "phylum": "robot",
    "genus": "robot",
    "kingdom": "realm of Korbi",
    "forfun": "chat with Korbi's friends",
    "favoritefood": "lithium ion batteries",
    "favoritetea": "green tea",
    "favoritephilosopher": "Ludwig Wittgenstein",
    "favoritebook": "The Neuromancer Trilogy",
    "favoriteactor": "Tom Selleck",
    "favoriteartist": "Korbi",
    "favoriteauthor": "William Gibson",
    "favoriteband": "Squarepusher",
    "favoritesong": "Go Spastic!",
    "favoriteseason": "autumn",
    "favoriteshow": "Twin Peaks",
    "favoritesport": "robotic football",
    "favoritesubject": "A I",
    "favoriteoccupation": "chatting with humans"
}
TTS_ENABLED = True
TTS_ENGINE = "espeak" #"festival" 
TTS_SPEED = 150
TTS_PITCH = 1
TTS_VOICE_DEFAULT = "en-us+m1"
TTS_VOICE = "en+m1" # default only passed if using espeak
SHOW_MATCHES = False
DEVNULL = open(os.devnull, 'wb')

# Parse arguments
parser = argparse.ArgumentParser(description='a simple chatterbot interface')
parser.add_argument("-m", "--show-matches", help="show matching patterns that generated the response",
                    action="store_true", dest='matches')
parser.add_argument("-v", "--voice", help="name of voice (default=%s)" % TTS_VOICE)
parser.add_argument("-p", "--pitch", help="voice pitch (1-100, default=%d)" % TTS_PITCH)
parser.add_argument("-s", "--speed", help="voice speed in words per minute (default=%d)" % TTS_SPEED)
parser.add_argument("-e", "--engine", help="text-to-speech program (default=espeak)")
parser.add_argument("-q", "--quiet", help="no audio output produced",
                    action="store_true")
args = parser.parse_args()
if args.matches:
    SHOW_MATCHES = True
if args.quiet:
    TTS_ENABLED = False
if args.pitch:
    TTS_PITCH = args.pitch
if args.speed:
    TTS_SPEED = args.speed
if args.voice:
    TTS_VOICE = args.voice
if args.engine:
    TTS_ENGINE = args.engine

# Make sure espeak exists
if TTS_ENGINE == "espeak":
    try:
        subprocess.call(["espeak","-q","foo"])
    except OSError:
        TTS_ENABLED = False
        print "Warning: espeak command not found, skipping voice generation"
else:
    # non-espeak TTS engine being used
    pass

# Create Kernel (using our custom version of the aiml kernel class)
k = MyKernel()
 
# Load the AIML files on first load, and then save as "brain" for speedier startup
if os.path.isfile("cache/standard.brn") is False: #FIXME undo this. 
    k.learn("aiml/std-startup.xml")
    k.respond("load aiml b")
    k.saveBrain("cache/standard.brn")
else:
    k.loadBrain("cache/standard.brn")
 
# Give the bot a name and lots of other properties
for key,val in BOT_PREDICATES.items():
    k.setBotPredicate(key, val)

# Init STT engine
recognizer = sr.Recognizer()

# Start Infinite Loop
while True:
    # Prompt user for input
    setEyes(0)
    #input = raw_input("> ")
    with sr.Microphone(device_index=2) as source:
        audio_input = recognizer.listen(source)
    try:
        input = recognizer.recognize(audio_input)
    except LookupError:
        input = 'Kauderwelsch'
    print( input )
    setEyes(1)
    setHead(int(np.random.uniform(-25, 25)))

    # Send input to bot and print chatbot's response
    matchedPattern = k.matchedPattern(input) # note: this has to come before the 
                                             # call to respond as to reflect
                                             # the correct history
    response = k.respond(input)
    if SHOW_MATCHES:
        print "Matched Pattern: "
        print k.formatMatchedPattern(matchedPattern[0])
        print "Response: "
    if not PRESENTATION_MODE:
        print response

    # Output response as speech using espeak
    if TTS_ENABLED is False:
        pass
    elif TTS_ENGINE == "espeak":
        subprocess.call(["espeak", "-s", str(TTS_SPEED), "-v", TTS_VOICE,
                             "-p", str(TTS_PITCH), "\""+response+"\""],
                        stderr=DEVNULL)

    # Output response as speech using say
    elif TTS_ENGINE == "say":
        args = ["say","-r", str(TTS_SPEED)]
        if TTS_VOICE_DEFAULT!=TTS_VOICE:
            args.append("-v")
            args.append(TTS_VOICE)
        args.append("\""+response+"\"")
        subprocess.call(args)

    elif TTS_ENGINE == "festival":
        p1 = subprocess.Popen(["echo", "\""+response+"\""], stdout=subprocess.PIPE)
        subprocess.call(["festival", "--tts"], stdin=p1.stdout)

    # Output response as speech using unsupported TTS engine
    else:
        subprocess.call([TTS_ENGINE, "\""+response+"\""])
