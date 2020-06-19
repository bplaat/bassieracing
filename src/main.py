# BassieRacing - A topdown 2D two player racing game
# Made by Bastiaan van der Plaat (https://bastiaan.ml/)
# GitHub repo: https://github.com/bplaat/bassieracing
# Made with PyGame (but only used to plot images and text to the screen and to handle the window events)
# It also uses tkinter for the file open and save dialogs and error messages
# And a noise library for random terrain generation

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
        pygame.init()

        # Create the window
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        self.screen = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))
        pygame.display.set_caption('BassieRacing')

        # Set running
        self.running = True

        # Load fonts
        font_path = 'assets/fonts/PressStart2P-Regular.ttf'
        self.titleFont = pygame.font.Font(font_path, 48)
        self.textFont = pygame.font.Font(font_path, 24)
        self.smallFont = pygame.font.Font(font_path, 16)

        # Load textures
        self.tilesImage = pygame.image.load('assets/images/tiles.png').convert_alpha()
        self.vehiclesImage = pygame.image.load('assets/images/vehicles.png').convert_alpha()

        # Hidden Tkinter window for file dialogs and error messages
        self.tkinter_window = tkinter.Tk()
        self.tkinter_window.withdraw()

        # Create menu page
        self.page = MenuPage(self)

    # Handle user events
    def handle_event(self, event):
        # Send event to current page
        self.page.handle_event(event)

        # Handle window close events
        if event.type == pygame.QUIT:
            self.running = False

    # The game loop
    def start(self):
        lastTime = time.time()
        while self.running:
            # Calculate delta time
            currentTime = time.time()
            delta = currentTime - lastTime
            lastTime = currentTime

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
