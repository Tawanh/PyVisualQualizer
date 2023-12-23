#Pygame for visualization
import pygame

#Librosa to get data of the audio
from librosa import load, core

import numpy as np
from math import sin, cos, pi

###########################
### AUDIO DATA FONCTION ###
###########################

#Load the audio with librosa and return the spectorgram, time_ratio and frequencies_ratio of it
def load_audio(audio_path):
    #get the sampling rate and the audio time series (np.ndarray)  of the audio 
    audio_time_series, sampling_rate = load(audio_path)

    #lenght of the windowed signal
    n_fft = 2048
    #number of audio samples between adjacent STFT columns
    hop_lenght = 512

    #stft = Short-time Fourier transform
    #to get spectogram of the audio
    audio_stft = core.stft(audio_time_series)

    spectrogram = np.abs(audio_stft)

    frequencies = core.fft_frequencies(n_fft = n_fft)
    times = core.frames_to_time(
        np.arange(spectrogram.shape[1]),
        sr = sampling_rate,
        hop_length = hop_lenght
    )

    #spectogram columns = time_ratio * any time
    time_ratio = len(times) / times[len(times) - 1] 
    #spectrogram row = frequencies_ratio * any frequenciey
    frequencies_ratio = len(frequencies) / frequencies[len(frequencies) - 1]

    return spectrogram, time_ratio, frequencies_ratio

#get decibel of a given time and frequency
def get_decibel(time, frequency, spectrogram, time_ratio, frequecies_ratio):
    return spectrogram[int(frequency * frequecies_ratio)][int(time * time_ratio)]

################
### VARIABLE ###
################

AUDIO_PATH = "audio.mp4"
SPECTROGRAM, TIME_RATIO, FREQUENCIES_RATIO = load_audio(AUDIO_PATH)
HZ = np.arange(0,8000,100)


SCREEEN_SIZE = [1000, 500]
FPS = 60

equalizer_type = 1

#############################
### PYGAME INITIALISATION ###
#############################

#Initialisation
pygame.init()
pygame.mixer.init()
pygame.mixer.music.load(AUDIO_PATH)

#Variable
screen = pygame.display.set_mode(SCREEEN_SIZE)
clock = pygame.time.Clock()
AUDIO_LENGTH = pygame.mixer.Sound(AUDIO_PATH).get_length()

##################
### EQUALIZERS ###
##################

#Draw a vizual equalizer in circle on the surface
def equ_circle(surface):
    nb_point = len(HZ)
    for i in range(nb_point):

        size = 75

        angle1 = pi / nb_point * 2 * i
        angle2 = pi / nb_point * 2 * (i + 1)

        position_x = SCREEEN_SIZE[0] / 2
        position_y = SCREEEN_SIZE[1] / 2

        distance_point1 = size + get_decibel(pygame.mixer.music.get_pos() / 1000, HZ[i], SPECTROGRAM, TIME_RATIO, FREQUENCIES_RATIO)
        if i < nb_point - 1:
            distance_point2 = size + get_decibel(pygame.mixer.music.get_pos() / 1000, HZ[i + 1], SPECTROGRAM, TIME_RATIO, FREQUENCIES_RATIO)
        else :
            distance_point2 = size + get_decibel(pygame.mixer.music.get_pos() / 1000, HZ[0], SPECTROGRAM, TIME_RATIO, FREQUENCIES_RATIO)

        if distance_point1 > size * 2:
            distance_point1 = size * 2
        if distance_point2 > size * 2:
            distance_point2 = size * 2

        point1 = (
            sin(angle1) * distance_point1 + position_x,
            cos(angle1) * distance_point1 + position_y
        )

        point2 = (
            sin(angle2) * distance_point2 + position_x,
            cos(angle2) * distance_point2 + position_y
        )

        color = 255 - (distance_point1 + distance_point2 - size * 2) / (size * 2) * 255

        pygame.draw.line(surface, (255 - color, color, 0), point1, point2)

#Draw a vizual equalizer in line on the surface
def equ_line(surface):
    nb_point = len(HZ)
    max_length = 50
    screen_ratio_x = SCREEEN_SIZE[0] / nb_point
    screen_ratio_y = (SCREEEN_SIZE[1] / 2 - 20) / max_length
    for x in range(nb_point):
        length = get_decibel(pygame.mixer.music.get_pos() / 1000, HZ[x], SPECTROGRAM, TIME_RATIO, FREQUENCIES_RATIO)
        if length > max_length:
            length = max_length
        for y in range(int(length)):
            color = y / max_length * 255
            pygame.draw.rect(surface, (color, 255 - color, 0), (x * screen_ratio_x, y * -1 * screen_ratio_y + SCREEEN_SIZE[1] // 2 - screen_ratio_y + 1, screen_ratio_x, screen_ratio_y - 1))
        for y in range(int(length)):
            color = y / max_length * 255
            pygame.draw.rect(surface, (color, 255 - color, 0), (x * screen_ratio_x, y * screen_ratio_y + SCREEEN_SIZE[1] // 2 + screen_ratio_y + 1, screen_ratio_x, screen_ratio_y - 1))
    pygame.draw.rect(surface, (0, 255, 0), (0, SCREEEN_SIZE[1] // 2, SCREEEN_SIZE[0], screen_ratio_y))


###################
### PYGAME CORE ###
###################

def render(surface):
    surface.fill((0, 0, 0))

    if equalizer_type == 2:
        equ_line(surface)
    if equalizer_type == 1:
        equ_circle(surface)

    pygame.display.update()

def input():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        
        #if 1 or 2 is pressed, change the vizual equalizer
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                return 1
            if event.key == pygame.K_2:
                return 2
    return None


pygame.mixer.music.play(0)

while True:
    render(screen)

    input_out = input()
    if input_out != None:
        equalizer_type = input_out

    clock.tick(FPS)

    pygame.display.set_caption("PyVisualQualizer 0.1")

