# BassieRacing - A topdown 2D two player racing game
# Made by Bastiaan van der Plaat (https://bastiaan.ml/)
# GitHub repo: https://github.com/bplaat/bassieracing
# Install all dependencies: pip install pygame
# Made with pygame (but only used to plot images and text to the screen and to handle the window events)
# It also uses tkinter for the file open and save dialogs and error messages

# Hide pygame support message
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'

# Import modules
from pages import *
import pygame
import time
import tkinter

# The game class
class Game:
    def __init__(self):
        # Init pygame
        pygame.mixer.pre_init(44100, 16, 1, 512)
        pygame.init()

        # Set running
        self.running = True

        # Init the window
        pygame.display.set_caption('BassieRacing')
        self.width = Config.WIDTH
        self.height = Config.HEIGHT
        self.fullscreen = False
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        self.screen = pygame.display.set_mode(( self.width, self.height ), pygame.DOUBLEBUF | pygame.RESIZABLE)
        del os.environ['SDL_VIDEO_CENTERED']

        # Load fonts
        font_path = 'assets/fonts/PressStart2P-Regular.ttf'
        self.titleFont = pygame.font.Font(font_path, 48)
        self.textFont = pygame.font.Font(font_path, 24)
        self.smallFont = pygame.font.Font(font_path, 16)

        # Load images
        self.tilesImage = pygame.image.load('assets/images/tiles.png').convert_alpha()
        self.vehiclesImage = pygame.image.load('assets/images/vehicles.png').convert_alpha()
        self.explosionImage = pygame.image.load('assets/images/explosion.png').convert_alpha()

        # Load music
        pygame.mixer.music.load('assets/music/deadmau5 - Infra Turbo Pigcart Racer.ogg')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)

        # Load sounds
        self.checkpointSound = pygame.mixer.Sound('assets/sounds/checkpoint.wav')
        self.clickSound = pygame.mixer.Sound('assets/sounds/click.wav')
        self.crashSound = pygame.mixer.Sound('assets/sounds/crash.wav')
        self.introSound = pygame.mixer.Sound('assets/sounds/intro.wav')
        self.lapSound = pygame.mixer.Sound('assets/sounds/lap.wav')

        # Load settings
        if os.path.isfile('settings.json'):
            with open('settings.json', 'r') as file:
                self.settings = json.load(file)
        else:
            self.settings = {
                'type': 'BassieRacing Settings',
                'music': {
                    'enabled': True,
                    'position': 0
                },
                'sound-effects': {
                    'enabled': True
                }
            }
        self.musicStart = self.settings['music']['position']

        # Create hidden Tkinter window for file dialogs and error messages
        self.tkinter_window = tkinter.Tk()
        self.tkinter_window.withdraw()

        # Create intro page
        self.page = IntroPage(self)

    # Save settings to file
    def save_settings(self):
        self.settings['music']['position'] = round(self.musicStart + pygame.mixer.music.get_pos() / 1000, 3)
        with open('settings.json', 'w') as file:
            file.write(json.dumps(self.settings, separators=(',', ':')) + '\n')

    # Handle user events
    def handle_event(self, event):
        # When music is finished reset and repeat
        if event.type == pygame.USEREVENT + 1:
            self.musicStart = 0
            pygame.mixer.music.rewind()
            pygame.mixer.music.play()

        # Handle window resize events
        if event.type == pygame.VIDEORESIZE:
            self.width = event.w
            self.height = event.h
            self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF| pygame.RESIZABLE)

        # Send event to current page
        self.page.handle_event(event)

        # Handle window close events
        if event.type == pygame.QUIT:
            self.save_settings()
            self.running = False

    # The game loop
    def start(self):
        lastTime = time.time()
        while self.running:
            # Calculate delta time
            self.time = time.time()
            delta = self.time - lastTime
            lastTime = self.time

            # Handle window events
            for event in pygame.event.get():
                self.handle_event(event)

            # Update the current page
            self.page.update(delta)

            # Draw the current page and flip pygame back buffer
            self.page.draw(self.screen)
            pygame.display.flip()

            # Sleep for a short while
            time.sleep(1 / Config.FPS)

# Create a game instance and start the game
game = Game()
game.start()
