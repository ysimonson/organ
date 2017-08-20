import pygame
import time

pygame.mixer.init()
pygame.init()
pygame.mixer.set_num_channels(25)

for note in ['a', 'c', 'd', 'e', 'g']:
    for scale in range(5):
        sound = pygame.mixer.Sound("audio/%s%s.wav" % (note, scale))
        channel = sound.play()
        time.sleep(1.0)
        channel.fadeout(500)
