# BassieRacing - A topdown 2D two player racing game
# Made by Bastiaan van der Plaat (https://bastiaan.ml/)
# GitHub repo: https://github.com/bplaat/bassieracing
# Windows install all dependencies: pip install pygame
# Ubuntu install all dependencies: sudo apt install python3-pygame python3-tk
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
import signal
import urllib.request
from utils import *

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
        self.iconImage = pygame.image.load('assets/images/icon.png')
        pygame.display.set_icon(self.iconImage)

        self.width = Config.WIDTH
        self.height = Config.HEIGHT
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        self.screen = pygame.display.set_mode(( self.width, self.height ), pygame.DOUBLEBUF | pygame.RESIZABLE)
        del os.environ['SDL_VIDEO_CENTERED']

        # Load settings
        if os.path.isfile(os.path.expanduser('~/bassieracing-settings.json')):
            with open(os.path.expanduser('~/bassieracing-settings.json'), 'r') as file:
                self.settings = json.load(file)

                if self.settings['type'] != 'BassieRacing Settings':
                    self.use_default_settings()

                self.settings['version'] = Config.VERSION

                # Restore corrupt settings fields
                if 'account' not in self.settings:
                    self.settings['account'] = {}
                if 'username' not in self.settings['account']:
                    self.settings['account']['username'] = 'Anonymous'

                if 'intro' not in self.settings:
                    self.settings['intro'] = {}
                if 'enabled' not in self.settings['intro']:
                    self.settings['intro']['enabled'] = True

                if 'music' not in self.settings:
                    self.settings['music'] = {}
                if 'enabled' not in self.settings['music']:
                    self.settings['music']['enabled'] = True
                if 'position' not in self.settings['music']:
                    self.settings['music']['position'] = 0

                if 'sound-effects' not in self.settings:
                    self.settings['sound-effects'] = {}
                if 'enabled' not in self.settings['sound-effects']:
                    self.settings['sound-effects']['enabled'] = True

                if 'selected' not in self.settings:
                    self.settings['selected'] = {}
                if 'map-id' not in self.settings['selected']:
                    self.settings['selected']['map-id'] = None

                if 'left' not in self.settings['selected']:
                    self.settings['selected']['left'] = {}
                if 'vehicle-id' not in self.settings['selected']['left']:
                    self.settings['selected']['left']['vehicle-id'] = 0
                if 'vehicle-color' not in self.settings['selected']['left']:
                    self.settings['selected']['left']['vehicle-color'] = VehicleColor.BLUE

                if 'right' not in self.settings['selected']:
                    self.settings['selected']['right'] = {}
                if 'vehicle-id' not in self.settings['selected']['right']:
                    self.settings['selected']['right']['vehicle-id'] = 0
                if 'vehicle-color' not in self.settings['selected']['right']:
                    self.settings['selected']['right']['vehicle-color'] = VehicleColor.RED

                if 'multiplayer' not in self.settings:
                    self.settings['multiplayer'] = {}
                if 'last-address' not in self.settings['multiplayer']:
                    self.settings['multiplayer']['last-address'] = ''

                if 'map-editor' not in self.settings:
                    self.settings['map-editor'] = {}
                if 'last-path' not in self.settings['map-editor']:
                    self.settings['map-editor']['last-path'] = None
                if 'grid' not in self.settings['map-editor']:
                    self.settings['map-editor']['grid'] = False
                if 'brush' not in self.settings['map-editor']:
                    self.settings['map-editor']['brush'] = 3

                if 'map-options' not in self.settings:
                    self.settings['map-options'] = {}
                if 'name' not in self.settings['map-options']:
                    self.settings['map-options']['name'] = 'Custom Map'
                if 'size' not in self.settings['map-options']:
                    self.settings['map-options']['size'] = Config.MAP_DEFAULT_SIZES_INDEX
                if 'laps' not in self.settings['map-options']:
                    self.settings['map-options']['laps'] = Config.MAP_DEFAULT_LAPS_INDEX

                if 'crashes' not in self.settings['map-options']:
                    self.settings['map-options']['crashes'] = {}
                if 'enabled' not in self.settings['map-options']['crashes']:
                    self.settings['map-options']['crashes']['enabled'] = True
                if 'timeout' not in self.settings['map-options']['crashes']:
                    self.settings['map-options']['crashes']['timeout'] = Config.MAP_DEFAULT_CRASH_TIMEOUT_INDEX

                if 'high-scores' not in self.settings:
                    self.settings['high-scores'] = []

                if 'custom-maps' not in self.settings:
                    self.settings['custom-maps'] = []

        else:
            self.use_default_settings()

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
        self.musicStart = self.settings['music']['position']
        pygame.mixer.music.load('assets/music/deadmau5 - Infra Turbo Pigcart Racer.mp3')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)

        # Load sounds
        self.checkpointSound = pygame.mixer.Sound('assets/sounds/checkpoint.wav')
        self.clickSound = pygame.mixer.Sound('assets/sounds/click.wav')
        self.crashSound = pygame.mixer.Sound('assets/sounds/crash.wav')
        self.introSound = pygame.mixer.Sound('assets/sounds/intro.wav')
        self.finishSound = pygame.mixer.Sound('assets/sounds/finish.wav')
        self.lapSound = pygame.mixer.Sound('assets/sounds/lap.wav')
        self.tickSound = pygame.mixer.Sound('assets/sounds/tick.wav')
        self.tockSound = pygame.mixer.Sound('assets/sounds/tock.wav')

        # Create hidden Tkinter window for file dialogs and error messages
        self.tkinter_window = tkinter.Tk()
        self.tkinter_window.withdraw()

        # Detect new version
        self.detect_new_version()

        # Create intro or menu page
        if self.settings['intro']['enabled']:
            self.page = IntroPage(self)
        else:
            self.page = MenuPage(self)

        # Init signal handlers
        signal.signal(signal.SIGINT, self.handle_signals)
        signal.signal(signal.SIGTERM, self.handle_signals)

    # Use default settings
    def use_default_settings(self):
        self.settings = {
            'type': 'BassieRacing Settings',
            'version': Config.VERSION,
            'account': {
                'username': 'Anonymous'
            },
            'intro': {
                'enabled': True
            },
            'music': {
                'enabled': True,
                'position': 0
            },
            'sound-effects': {
                'enabled': True
            },
            'selected': {
                'map-id': None,
                'left': {
                    'vehicle-id': 0,
                    'vehicle-color': VehicleColor.BLUE
                },
                'right': {
                    'vehicle-id': 0,
                    'vehicle-color': VehicleColor.RED
                }
            },
            'multiplayer': {
                'last-address': ''
            },
            'map-editor': {
                'last-path': None,
                'grid': False,
                'brush': Config.EDITOR_DEFAULT_BRUSH_INDEX,
            },
            'map-options': {
                'name': 'Custom Map',
                'size': Config.MAP_DEFAULT_SIZES_INDEX,
                'laps': Config.MAP_DEFAULT_LAPS_INDEX,
                'crashes': {
                    'enabled': True,
                    'timeout': Config.MAP_DEFAULT_CRASH_TIMEOUT_INDEX
                }
            },
            'high-scores': [],
            'custom-maps': []
        }

    # Save settings to file
    def save_settings(self):
        self.settings['music']['position'] = round(self.musicStart + pygame.mixer.music.get_pos() / 1000, 3)
        with open(os.path.expanduser('~/bassieracing-settings.json'), 'w') as file:
            file.write(json.dumps(self.settings, separators=(',', ':')) + '\n')

    # Handle signals
    def handle_signals(self, sig, frame):
        self.save_settings()
        self.running = False

    # Detect new version
    def detect_new_version(self):
        try:
            # Do HTTP request to online constants.py file to check version label
            response = urllib.request.urlopen(Config.GIT_REPO_URL + '/blob/master/src/constants.py?raw=true')
            data = response.read().decode('utf8')

            # Parse version label
            start = 'VERSION = \''
            version = data[data.find(start) + len(start):]
            version = version[:version.find('\'')]

            # Do final version logic
            if checkVersion(version):
                self.newVersionAvailable = version
            else:
                self.newVersionAvailable = None

        # When it fails because of no internet it isn't so bad
        except:
            self.newVersionAvailable = None

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

    # Focus the game window
    def focus(self):
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF| pygame.RESIZABLE)

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
