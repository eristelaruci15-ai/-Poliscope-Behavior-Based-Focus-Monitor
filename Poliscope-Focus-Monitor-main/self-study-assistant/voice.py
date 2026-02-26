import pygame
import os

class VoicePlayer:
    def __init__(self, audio_dir):
        pygame.mixer.init()
        self.sounds = {}

        for s in ["engaged", "distracted", "inactive"]:
            path = os.path.join(audio_dir, f"{s}.wav")
            self.sounds[s.upper()] = pygame.mixer.Sound(path)

    def play(self, state):
        pygame.mixer.stop()
        self.sounds[state].play()
