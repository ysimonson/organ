import random
import socket
import pygame
import time
import sys
import os

try:
    import Adafruit_MPR121.MPR121 as MPR121
except:
    sys.stderr.write("WARNING: Could not import MPR121\n")

NOTES = ["c", "d", "e", "g", "a"]
PITCHES = list(range(5))

class TouchInput:
    def __init__(self):
        self.cap = MPR121.MPR121()

        if not self.cap.begin():
            raise Exception("Could not initialize capacitive touch interface")

    def __call__(self):
        notes = []
        pitches = []
        touched = self.cap.touched()

        for i in xrange(5):
            pin_bit = 1 << i

            if touched & pin_bit:
                notes.append(NOTES[i])

        for i in xrange(5, 10):
            pin_bit = 1 << i

            if touched & pin_bit:
                pitches.append(i - 5)

        return (notes, pitches)

class CommandLineInput:
    def __call__(self):
        line = sys.stdin.readline()
        notes = []
        pitches = []

        for c in line:
            if c in NOTES:
                notes.append(c)
            elif c in [str(pitch) for pitch in PITCHES]:
                pitches.append(int(c))

        return (notes, pitches)

class RandomInput:
    def __call__(self):
        num_notes = random.randint(0, len(NOTES))
        num_pitches = random.randint(0, len(PITCHES))
        return (random.sample(NOTES, num_notes), random.sample(PITCHES, num_pitches))

class AudioOutput:
    def __init__(self, sample_dir):
        pygame.mixer.init()
        pygame.init()
        pygame.mixer.set_num_channels(25)
        self.sounds = {}
        self.channels = {}

        for note in NOTES:
            for pitch in PITCHES:
                sound_path = os.path.join(sample_dir, "%s%s.wav" % (note, pitch))
                sound = pygame.mixer.Sound(sound_path)
                self.sounds[(note, pitch)] = sound

    def __call__(self, keys):
        # Kill any sounds no longer playing
        for key, channel in list(self.channels.items()):
            if not channel or not channel.get_busy():
                # GC any old sounds
                del self.channels[key]
            elif not key in keys:
                # If the key was released, and the sound is still playing,
                # stop it
                self.channels[key].fadeout(500)
                del self.channels[key]

        # Now update the playing keys
        for key in keys:
            if not key in self.channels:
                # If the key was pressed, and the sound is not playing yet,
                # play it
                channel = self.sounds[key].play(loops=-1)
                self.channels[key] = channel

class FireOutput:
    def __init__(self, host):
        self.host = host
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.last_output = time.time()

    def __call__(self, keys):
        if self.last_output is not None and time.time() - self.last_output < 0.1:
            return

        message_buffer = ["0", "5", "5"]

        for note in NOTES:
            message_buffer.append("".join("1" if (note, pitch) in keys else "0" for pitch in PITCHES))

        message = "\n".join(message_buffer)
        self.socket.sendto(message, (self.host, 1075))
        self.last_output = time.time()

def get_input_engine():
    configured_input = os.environ.get("INPUT", "cli")

    if configured_input == "cli":
        return CommandLineInput()
    elif configured_input == "touch":
        return TouchInput()
    elif configured_input == "random":
        return RandomInput()
    else:
        raise Exception("Unknown input engine `%s`" % configured_input)

def get_output_engines():
    configured_outputs = os.environ.get("OUTPUTS", "audio").split(",")
    outputs = []

    for configured_output in configured_outputs:
        if configured_output == "audio":
            sample_dir = os.environ.get("SAMPLE_DIR", "./audio")
            outputs.append(AudioOutput(sample_dir))
        elif configured_output == "fire":
            host = os.environ.get("FIRE_HOST", "192.168.42.1")
            outputs.append(FireOutput(host))
        else:
            raise Exception("Unknown output engine `%s`" % configured_output)

    return outputs

def main():
    input_engine = get_input_engine()
    output_engines = get_output_engines()
    notes = None
    pitches = None
    keys = None

    while True:
        notes, pitches = input_engine()
        keys = [(note, pitch) for note in notes for pitch in pitches]

        for output_engine in output_engines:
            output_engine(keys)

if __name__ == "__main__":
    main()
