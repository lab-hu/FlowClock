import pygame

def play_alarm():
    pygame.mixer.init()
    # Loading the aiff file you renamed/copied earlier
    pygame.mixer.music.load("alarm.aiff")
    # -1 means play on an infinite loop
    pygame.mixer.music.play(-1) 

def stop_alarm():
    pygame.mixer.music.stop()