# BassieRacing - Pages

# Import modules
from constants import *
import math
from objects import *
import random
import tkinter.filedialog
from utils import *
import webbrowser
from widgets import *

# The page class
class Page:
    # Create empty page
    def __init__(self, game, backgroundColor = None):
        self.game = game

        # Pick random background color when background color null
        if backgroundColor != None:
            self.backgroundColor = backgroundColor
        else:
            self.backgroundColor = (random.randint(50, 150), random.randint(50, 150), random.randint(50, 150))

        # Create widgets
        self.widgets = []
        self.create_widgets()

    # Handle page events
    def handle_event(self, event):
        # Send all events to the widgets
        for widget in reversed(self.widgets):
            if widget.handle_event(event):
                return True

        # On resize recreated widgets
        if event.type == pygame.VIDEORESIZE:
            self.widgets = []
            self.create_widgets()

        return False

    # Update page
    def update(self, delta):
        pass

    # Draw page
    def draw(self, surface):
        # Draw background
        surface.fill(self.backgroundColor)

        # Draw widgets
        for widget in self.widgets:
            widget.draw(surface)

# The intro page class
class IntroPage(Page):
    # Create menu page
    def __init__(self, game):
        Page.__init__(self, game, Color.WHITE)

        # Load and play intro sound
        if game.settings['sound-effects']['enabled']:
            game.introSound.set_volume(0.75)
        else:
            game.introSound.set_volume(0)
        self.introSoundChannel = game.introSound.play()
        self.introSoundChannel.set_endevent(pygame.USEREVENT + 2)

    # Create intro page widgets
    def create_widgets(self):
        y = (self.game.height - (256 + 32 + 96 + 16 + 64)) // 2
        self.widgets.append(Image('assets/images/logo.png', 0, y, self.game.width, 256))
        y += 256 + 32
        self.widgets.append(Label(self.game, 'BassieSoft', 0, y, self.game.width, 96, self.game.titleFont, Color.BLACK))
        y += 96 + 16
        self.widgets.append(Label(self.game, 'Presents a new racing game...', 0, y, self.game.width, 64, self.game.textFont, Color.BLACK))

    # Handle intro page events
    def handle_event(self, event):
        if Page.handle_event(self, event):
            return True

        if event.type == pygame.MOUSEBUTTONUP:
            self.introSoundChannel.set_endevent()
            self.introSoundChannel.fadeout(250)
            if self.game.settings['sound-effects']['enabled']:
                self.game.clickSound.play()
            self.game.page = MenuPage(self.game)
            return True

        if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
            self.introSoundChannel.set_endevent()
            self.introSoundChannel.fadeout(250)
            self.game.page = MenuPage(self.game)

        if event.type == pygame.USEREVENT + 2:
            self.game.page = MenuPage(self.game)

        return False

# The menu page class
class MenuPage(Page):
    # Create menu page
    def __init__(self, game):
        Page.__init__(self, game)

        # Start music if enabled in settings
        if game.settings['music']['enabled'] and not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(0, game.settings['music']['position'])

    # Create menu page widgets
    def create_widgets(self):
        y = ((self.game.height - 32) - (72 + (64 + 16) * 5)) // 2
        self.widgets.append(Label(self.game, 'BassieRacing', 0, y, self.game.width, 72, self.game.titleFont, Color.WHITE))
        y += 72 + 16
        self.widgets.append(Button(self.game, 'Play', self.game.width // 4, y, self.game.width // 2, 64, self.game.textFont, Color.BLACK, Color.WHITE, self.play_button_clicked))
        y += 64 + 16
        self.widgets.append(Button(self.game, 'Map Editor', self.game.width // 4, y, self.game.width // 2, 64, self.game.textFont, Color.BLACK, Color.WHITE, self.edit_button_clicked))
        y += 64 + 16
        self.widgets.append(Button(self.game, 'Help', self.game.width // 4, y, self.game.width // 2, 64, self.game.textFont, Color.BLACK, Color.WHITE, self.help_button_clicked))
        y += 64 + 16
        self.widgets.append(Button(self.game, 'Settings', self.game.width // 4, y, self.game.width // 2, 64, self.game.textFont, Color.BLACK, Color.WHITE, self.settings_button_clicked))
        y += 64 + 16
        self.widgets.append(Button(self.game, 'Exit', self.game.width // 4, y, self.game.width // 2, 64, self.game.textFont, Color.BLACK, Color.WHITE, self.exit_button_clicked))

        if self.game.newVersionAvailable != None:
            self.widgets.append(Label(self.game, 'A newer version (v' + self.game.newVersionAvailable + ') is available', 16, 16, self.game.width - 16 - 256 - 16, 32, self.game.textFont, Color.WHITE, TextAlign.LEFT, self.new_version_label_clicked))
        self.widgets.append(Label(self.game, 'v' + Config.VERSION, self.game.width - 16 - 256, 16, 256, 32, self.game.textFont, Color.WHITE, TextAlign.RIGHT, self.version_label_clicked))

        self.widgets.append(Label(self.game, 'Made by Bastiaan van der Plaat', 0, self.game.height - 64 - 16, self.game.width, 64, self.game.textFont, Color.WHITE, TextAlign.CENTER, self.footer_label_clicked))

    # New version label clicked
    def new_version_label_clicked(self):
        webbrowser.open_new(Config.GIT_REPO_URL + '/releases')

    # Version label clicked
    def version_label_clicked(self):
        webbrowser.open_new(Config.GIT_REPO_URL)

    # Play button clicked
    def play_button_clicked(self):
        self.game.page = PlayPage(self.game)

    # Edit button clicked
    def edit_button_clicked(self):
        self.game.page = EditorPage(self.game)

    # Help button clicked
    def help_button_clicked(self):
        self.game.page = HelpPage(self.game)

    # Settings button clicked
    def settings_button_clicked(self):
        self.game.page = SettingsPage(self.game)

    # Exit button clicked
    def exit_button_clicked(self):
        self.game.save_settings()
        self.game.running = False

    # Footer label clicked
    def footer_label_clicked(self):
        webbrowser.open_new('https://bastiaan.ml/')

# The play page class
class PlayPage(Page):
    # Create play page
    def __init__(self, game):
        Page.__init__(self, game)

    # Create play page widgets
    def create_widgets(self):
        y = (self.game.height - (96 + (64 + 16) * 3 + 24 + 64)) // 2
        self.widgets.append(Label(self.game, 'Select a game mode', 0, y, self.game.width, 96, self.game.titleFont, Color.WHITE))
        y += 96 + 16
        self.widgets.append(Button(self.game, 'Single Player', self.game.width // 6, y, self.game.width // 3 * 2, 64, self.game.textFont, Color.BLACK, Color.WHITE, self.single_player_button_clicked))
        y += 64 + 16
        self.widgets.append(Button(self.game, 'Split Screen', self.game.width // 6, y, self.game.width // 3 * 2, 64, self.game.textFont, Color.BLACK, Color.WHITE, self.split_screen_button_clicked))
        y += 64 + 16
        self.widgets.append(Button(self.game, 'Multi Player', self.game.width // 6, y, self.game.width // 3 * 2, 64, self.game.textFont, Color.BLACK, Color.WHITE, self.multi_player_button_clicked))
        y += 64 + 24
        self.widgets.append(Button(self.game, 'Back', self.game.width // 4, y, self.game.width // 2, 64, self.game.textFont, Color.BLACK, Color.WHITE, self.back_button_clicked))

    # Single Player button clicked
    def single_player_button_clicked(self):
        self.game.page = SelectMapPage(self.game, GameMode.SINGLE_PLAYER)

    # Split Screen button clicked
    def split_screen_button_clicked(self):
        self.game.page = SelectMapPage(self.game, GameMode.SPLIT_SCREEN)

    # Multi Player button clicked
    def multi_player_button_clicked(self):
        self.game.page = MultiPlayerPage(self.game)

    # Back button clicked event
    def back_button_clicked(self):
        self.game.page = MenuPage(self.game)

# The select map page class
class SelectMapPage(Page):
    # Create select map page
    def __init__(self, game, gamemode):
        self.gamemode = gamemode
        self.selectedMapIndex = None
        Page.__init__(self, game)

    # Create select map page widgets
    def create_widgets(self):
        self.widgets.append(Label(self.game, 'Select a map to race', 0, 24, self.game.width, 72, self.game.titleFont, Color.WHITE))
        self.mapSelector = MapSelector(self.game, 16, 24 + 72 + 16, self.game.width - 16 - 16, self.game.height - (24 + 72 + 16) - (48 + 64 + 16), self.selectedMapIndex, self.map_selector_changed)
        self.widgets.append(self.mapSelector)
        self.widgets.append(Button(self.game, 'Back', 16, self.game.height - 64 - 16, 240, 64, self.game.textFont, Color.BLACK, Color.WHITE, self.back_button_clicked))
        self.widgets.append(Button(self.game, 'Load custom map', (self.game.width - 420) // 2, self.game.height - 64 - 16, 420, 64, self.game.textFont, Color.BLACK, Color.WHITE, self.load_button_clicked))
        self.widgets.append(Button(self.game, 'Continue', self.game.width - 16 - 240, self.game.height - 64 - 16, 240, 64, self.game.textFont, Color.BLACK, Color.WHITE, self.continue_button_clicked))

    # Map selector changed
    def map_selector_changed(self, selectedMapIndex):
        self.selectedMapIndex = selectedMapIndex

    # Back button clicked
    def back_button_clicked(self):
        self.game.page = PlayPage(self.game)

    # Load button clicked
    def load_button_clicked(self):
        file_path = tkinter.filedialog.askopenfilename(title='Select a BassieRacing Map to load...', filetypes=[ ( 'JSON files', '*.json' ) ])
        if file_path:
            self.game.focus()
            self.mapSelector.load_map(file_path)

    # Continue button clicked
    def continue_button_clicked(self):
        self.game.page = SelectVehiclePage(self.game, self.gamemode, self.mapSelector.selectedMap)

# The select vehicle page class
class SelectVehiclePage(Page):
    # Create select vehicle page
    def __init__(self, game, gamemode, map):
        self.gamemode = gamemode
        self.map = map
        self.leftSelectedVehicleIndex = None
        self.rightSelectedVehicleIndex = None
        Page.__init__(self, game)

    # Create select vehicle page widgets
    def create_widgets(self):
        if self.gamemode == GameMode.SINGLE_PLAYER:
            self.widgets.append(Label(self.game, 'Select a vehicle', 0, 24, self.game.width, 72, self.game.titleFont, Color.WHITE))
            self.leftVehicleSelector = VehicleSelector(self.game, 16, 24 + 72 + 16, self.game.width - (16 + 16), self.game.height - (24 + 72 + 16) - (48 + 64 + 16), VehicleColor.BLUE, self.leftSelectedVehicleIndex, self.left_vehicle_selector_changed)
            self.widgets.append(self.leftVehicleSelector)

        if self.gamemode == GameMode.SPLIT_SCREEN:
            self.widgets.append(Label(self.game, 'Select both a vehicle', 0, 24, self.game.width, 72, self.game.titleFont, Color.WHITE))
            self.leftVehicleSelector = VehicleSelector(self.game, 16, 24 + 72 + 16, self.game.width // 2 - (16 + 16), self.game.height - (24 + 72 + 16) - (48 + 64 + 16), VehicleColor.BLUE, self.leftSelectedVehicleIndex, self.left_vehicle_selector_changed)
            self.widgets.append(self.leftVehicleSelector)
            self.rightVehicleSelector = VehicleSelector(self.game, 16 + self.game.width // 2, 24 + 72 + 16, self.game.width // 2 - (16 + 16), self.game.height - (24 + 72 + 16) - (48 + 64 + 16), VehicleColor.RED, self.rightSelectedVehicleIndex, self.right_vehicle_selector_changed)
            self.widgets.append(self.rightVehicleSelector)

        self.widgets.append(Button(self.game, 'Back', 16, self.game.height - 64 - 16, 240, 64, self.game.textFont, Color.BLACK, Color.WHITE, self.back_button_clicked))
        self.widgets.append(Button(self.game, 'Race!', self.game.width - 16 - 240, self.game.height - 64 - 16, 240, 64, self.game.textFont, Color.BLACK, Color.WHITE, self.race_button_clicked))

    # Left vehicle selector changed
    def left_vehicle_selector_changed(self, selectedVehicleIndex):
        self.leftSelectedVehicleIndex = selectedVehicleIndex

    # Right vehicle selector changed
    def right_vehicle_selector_changed(self, selectedVehicleIndex):
        self.rightSelectedVehicleIndex = selectedVehicleIndex

    # Back button clicked
    def back_button_clicked(self):
        self.game.page = SelectMapPage(self.game, self.gamemode)

    # Race button clicked
    def race_button_clicked(self):
        if self.gamemode == GameMode.SINGLE_PLAYER:
            self.game.page = GamePage(self.game, self.gamemode, self.map, [
                self.leftVehicleSelector.selectedVehicle
            ])
        if self.gamemode == GameMode.SPLIT_SCREEN:
            self.game.page = GamePage(self.game, self.gamemode, self.map, [
                self.leftVehicleSelector.selectedVehicle,
                self.rightVehicleSelector.selectedVehicle
            ])

# The game page class
class GamePage(Page):
    # Create game page
    def __init__(self, game, gamemode, map, vehicleTypes):
        self.gamemode = gamemode
        self.map = map

        # Create the vehicles
        self.vehicles = []

        # Check if finish is horizontal
        if map.finish['height'] > map.finish['width']:
            self.leftVehicle = Vehicle(game, VehicleId.LEFT, vehicleTypes[0], VehicleColor.BLUE, map, self.vehicles,
                (map.finish['x'] - 1) * Config.TILE_SPRITE_SIZE + Config.TILE_SPRITE_SIZE / 2,
                (map.finish['y'] + map.finish['height'] // 2 - 1) * Config.TILE_SPRITE_SIZE + Config.TILE_SPRITE_SIZE / 2,
                math.radians(270)
            )
            self.vehicles.append(self.leftVehicle)

            if gamemode == GameMode.SPLIT_SCREEN:
                self.rightVehicle = Vehicle(game, VehicleId.RIGHT, vehicleTypes[1], VehicleColor.RED, map, self.vehicles,
                    (map.finish['x'] - 1)  * Config.TILE_SPRITE_SIZE + Config.TILE_SPRITE_SIZE / 2,
                    (map.finish['y'] + map.finish['height'] // 2)  * Config.TILE_SPRITE_SIZE + Config.TILE_SPRITE_SIZE / 2,
                    math.radians(270)
                )
                self.vehicles.append(self.rightVehicle)

        # Or when the finish is vertical
        else:
            self.leftVehicle = Vehicle(game, VehicleId.LEFT, vehicleTypes[0], VehicleColor.BLUE, map, self.vehicles,
                (map.finish['x'] + map.finish['width'] // 2 - 1) * Config.TILE_SPRITE_SIZE + Config.TILE_SPRITE_SIZE / 2,
                (map.finish['y'] + map.finish['height']) * Config.TILE_SPRITE_SIZE + Config.TILE_SPRITE_SIZE / 2,
                0
            )
            self.vehicles.append(self.leftVehicle)

            if gamemode == GameMode.SPLIT_SCREEN:
                self.rightVehicle = Vehicle(game, VehicleId.RIGHT, vehicleTypes[1], VehicleColor.RED, map, self.vehicles,
                    (map.finish['x'] + map.finish['width'] // 2)  * Config.TILE_SPRITE_SIZE + Config.TILE_SPRITE_SIZE / 2,
                    (map.finish['y'] + map.finish['height'])  * Config.TILE_SPRITE_SIZE + Config.TILE_SPRITE_SIZE / 2,
                    0
                )
                self.vehicles.append(self.rightVehicle)

        # Create page
        Page.__init__(self, game, Color.BLACK)

    # Create game page widgets
    def create_widgets(self):
        minimap_size = self.game.width / 5

        if self.gamemode == GameMode.SINGLE_PLAYER:
            self.leftVehicleViewport = VehicleViewport(self.game, self.leftVehicle, 0, 0, self.game.width, self.game.height, self.map, self.vehicles)
            self.widgets.append(self.leftVehicleViewport)

            self.widgets.append(Rect(self.game, self.game.width - minimap_size - 12, self.game.height - minimap_size - 12, minimap_size + 4, minimap_size + 4, Color.BLACK))
            self.widgets.append(MiniMap(self.game, self.map, self.vehicles, self.game.width - minimap_size - 10, self.game.height - minimap_size - 10, minimap_size, minimap_size))

        if self.gamemode == GameMode.SPLIT_SCREEN:
            self.leftVehicleViewport = VehicleViewport(self.game, self.leftVehicle, 0, 0, self.game.width // 2 - 1, self.game.height, self.map, self.vehicles)
            self.widgets.append(self.leftVehicleViewport)
            self.rightVehicleViewport = VehicleViewport(self.game, self.rightVehicle, self.game.width // 2 + 1, 0, self.game.width // 2 - 1, self.game.height, self.map, self.vehicles)
            self.widgets.append(self.rightVehicleViewport)

            self.widgets.append(Rect(self.game, (self.game.width - minimap_size) // 2 - 2, 8, minimap_size + 4, minimap_size + 4, Color.BLACK))
            self.widgets.append(MiniMap(self.game, self.map, self.vehicles, (self.game.width - minimap_size) // 2, 10, minimap_size, minimap_size))

        self.widgets.append(Button(self.game, 'Back', self.game.width - 16 - 128, 16, 128, 64, self.game.textFont, Color.BLACK, Color.WHITE, self.back_button_clicked))

    # Back button clicked
    def back_button_clicked(self):
        self.game.page = MenuPage(self.game)

    # Update game page
    def update(self, delta):
        # Update vehicle viewports
        self.leftVehicleViewport.update(delta)
        if self.gamemode == GameMode.SPLIT_SCREEN:
            self.rightVehicleViewport.update(delta)

        # When countdown is over start vehicle
        if not self.leftVehicle.started and self.leftVehicleViewport.countdownClock.ended:
            self.leftVehicle.started = True
            self.leftVehicle.startTime = self.game.time

        if self.gamemode == GameMode.SPLIT_SCREEN and not self.rightVehicle.started and self.rightVehicleViewport.countdownClock.ended:
            self.rightVehicle.started = True
            self.rightVehicle.startTime = self.game.time

        # Update all the vehicles
        for vehicle in self.vehicles:
            if vehicle.id == VehicleId.LEFT:
                vehicle.update(delta, self.leftVehicleViewport.camera)
            if vehicle.id == VehicleId.RIGHT:
                vehicle.update(delta, self.rightVehicleViewport.camera)

        # When both vehicles are finished go to the stats page
        if self.gamemode == GameMode.SINGLE_PLAYER and self.leftVehicle.finished:
            self.game.page = StatsPage(self.game, self.gamemode, self.map, self.vehicles)
        if self.gamemode == GameMode.SPLIT_SCREEN and self.leftVehicle.finished and self.rightVehicle.finished:
            self.game.page = StatsPage(self.game, self.gamemode, self.map, self.vehicles)

# The stats page class
class StatsPage(Page):
    # Create stats page
    def __init__(self, game, gamemode, map, vehicles):
        self.gamemode = gamemode
        self.map = map
        self.vehicles = vehicles

        # Calculate fastest time
        if gamemode == GameMode.SINGLE_PLAYER:
            fastestTime = self.vehicles[VehicleId.LEFT].finishTime - self.vehicles[VehicleId.LEFT].startTime
        if game == GameMode.SPLIT_SCREEN:
            fastestTime = min(
                self.vehicles[VehicleId.LEFT].finishTime - self.vehicles[VehicleId.LEFT].startTime,
                self.vehicles[VehicleId.RIGHT].finishTime - self.vehicles[VehicleId.RIGHT].startTime
            )

        # Save high score
        highscoreExisted = False
        for score in game.settings['high-scores']:
            if score['map-id'] == map.id and score['time'] > fastestTime:
                score['time'] = round(fastestTime, 3)
                highscoreExisted = True
                break

        if not highscoreExisted:
            game.settings['high-scores'].append({
                'map-id': map.id,
                'time': round(fastestTime, 3)
            })

        game.save_settings()

        Page.__init__(self, game)

    # Create stats page widgets
    def create_widgets(self):
        y = (self.game.height - (72 + 16 + 128 + 16 + (48 + 16) * (2 + len(self.vehicles[VehicleId.LEFT].lapTimes)) + 16 + 64)) // 2
        self.widgets.append(Label(self.game, 'Game stats', 0, y, self.game.width, 72, self.game.titleFont, Color.WHITE))
        y += 72 + 16

        # Create stats for the single player gamemode
        if self.gamemode == GameMode.SINGLE_PLAYER:
            # Create vehicle image
            vehicleImageSurface = self.game.vehiclesImage.subsurface((
                self.vehicles[VehicleId.LEFT].vehicleType['colors'][self.vehicles[VehicleId.LEFT].color]['x'],
                self.vehicles[VehicleId.LEFT].vehicleType['colors'][self.vehicles[VehicleId.LEFT].color]['y'],
                self.vehicles[VehicleId.LEFT].vehicleType['width'],
                self.vehicles[VehicleId.LEFT].vehicleType['height']
            ))
            self.widgets.append(Image(vehicleImageSurface, self.game.width // 4, y, self.game.width // 2, 128))
            y += 128 + 16

            self.widgets.append(Label(self.game, 'You won!', self.game.width // 4, y, self.game.width // 2, 48, self.game.textFont, Color.WHITE))
            y += 48 + 16

            self.widgets.append(Label(self.game, 'Total: %s' % (formatTime(self.vehicles[VehicleId.LEFT].finishTime - self.vehicles[VehicleId.LEFT].startTime)), self.game.width // 4, y, self.game.width // 2, 48, self.game.textFont, Color.WHITE))
            y += 48 + 16

            for i, time in enumerate(self.vehicles[VehicleId.LEFT].lapTimes):
                self.widgets.append(Label(self.game, 'Lap %d: %s' % (i + 1, formatTime(time)), self.game.width // 4, y, self.game.width // 2, 48, self.game.textFont, Color.WHITE))
                y += 48 + 16
            y += 16

        # Create stats for the split screen gamemode
        if self.gamemode == GameMode.SPLIT_SCREEN:
            if self.vehicles[VehicleId.LEFT].finishTime - self.vehicles[VehicleId.LEFT].startTime < self.vehicles[VehicleId.RIGHT].finishTime - self.vehicles[VehicleId.RIGHT].startTime:
                # Create vehicle image
                vehicleImageSurface = self.game.vehiclesImage.subsurface((
                    self.vehicles[VehicleId.LEFT].vehicleType['colors'][self.vehicles[VehicleId.LEFT].color]['x'],
                    self.vehicles[VehicleId.LEFT].vehicleType['colors'][self.vehicles[VehicleId.LEFT].color]['y'],
                    self.vehicles[VehicleId.LEFT].vehicleType['width'],
                    self.vehicles[VehicleId.LEFT].vehicleType['height']
                ))
                self.widgets.append(Image(vehicleImageSurface, self.game.width // 4, y, self.game.width // 2, 128))
                y += 128 + 16

                self.widgets.append(Label(self.game, 'Left player wins!', self.game.width // 4, y, self.game.width // 2, 48, self.game.textFont, Color.WHITE))
                y += 48 + 16
            else:
                # Create vehicle image
                vehicleImageSurface = self.game.vehiclesImage.subsurface((
                    self.vehicles[VehicleId.RIGHT].vehicleType['colors'][self.vehicles[VehicleId.RIGHT].color]['x'],
                    self.vehicles[VehicleId.RIGHT].vehicleType['colors'][self.vehicles[VehicleId.RIGHT].color]['y'],
                    self.vehicles[VehicleId.RIGHT].vehicleType['width'],
                    self.vehicles[VehicleId.RIGHT].vehicleType['height']
                ))
                self.widgets.append(Image(vehicleImageSurface, self.game.width // 4, y, self.game.width // 2, 128))
                y += 128 + 16

                self.widgets.append(Label(self.game, 'Right player wins!', self.game.width // 4, y, self.game.width // 2, 64, self.game.textFont, Color.WHITE))
                y += 64 + 16

            self.widgets.append(Label(self.game, 'Total: %s  -  %s' % (formatTime(self.vehicles[VehicleId.LEFT].finishTime - self.vehicles[VehicleId.LEFT].startTime), formatTime(self.vehicles[VehicleId.RIGHT].finishTime - self.vehicles[VehicleId.RIGHT].startTime)), self.game.width // 4, y, self.game.width // 2, 48, self.game.textFont, Color.WHITE))
            y += 48 + 16

            for i, time in enumerate(self.vehicles[VehicleId.LEFT].lapTimes):
                self.widgets.append(Label(self.game, 'Lap %d: %s  -  %s' % (i + 1, formatTime(time), formatTime(self.vehicles[VehicleId.RIGHT].lapTimes[i])), self.game.width // 4, y, self.game.width // 2, 48, self.game.textFont, Color.WHITE))
                y += 48 + 16
            y += 16

        self.widgets.append(Button(self.game, 'Continue', self.game.width // 4, y, self.game.width // 2, 64, self.game.textFont, Color.BLACK, Color.WHITE, self.continue_button_clicked))

    # Continue button clicked event
    def continue_button_clicked(self):
        self.game.page = MenuPage(self.game)

# The multi player page class
class MultiPlayerPage(Page):
    # Create multi player page
    def __init__(self, game):
        Page.__init__(self, game)

    # Create multi player page widgets
    def create_widgets(self):
        y = (self.game.height - (72 + 64 + 16 + 24 + 64)) // 2
        self.widgets.append(Label(self.game, 'Multi Player', 0, y, self.game.width, 72, self.game.titleFont, Color.WHITE))
        y += 72 + 16
        self.widgets.append(Label(self.game, 'Coming soon...', 0, y, self.game.width, 64, self.game.textFont, Color.WHITE))
        y += 64 + 24
        self.widgets.append(Button(self.game, 'Back', self.game.width // 4, y, self.game.width // 2, 64, self.game.textFont, Color.BLACK, Color.WHITE, self.back_button_clicked))

    # Back button clicked event
    def back_button_clicked(self):
        self.game.page = PlayPage(self.game)

# The edit page class
class EditorPage(Page):
    # Create edit page
    def __init__(self, game):
        self.file_path = None
        pygame.display.set_caption('Unsaved - BassieRacing')
        self.map = Map.generate_map(game, 32, 32)
        self.grid = False
        self.mapCamera = { 'x': None, 'y': None }
        self.selectedSizeIndex = 1
        self.selectedBrushIndex = 3
        Page.__init__(self, game, Color.DARK)

    # Create edit page widgets
    def create_widgets(self):
        self.mapEditor = MapEditor(self.game, self.map, 0, 0, self.game.width, self.game.height, self.selectedBrushIndex, self.grid, self.mapCamera)
        self.widgets.append(self.mapEditor)

        self.widgets.append(Button(self.game, 'New', 16, 16, 128, 64, self.game.textFont, Color.BLACK, Color.WHITE, self.new_button_clicked))
        self.widgets.append(Button(self.game, 'Open', 16 + (128 + 16), 16, 128, 64, self.game.textFont, Color.BLACK, Color.WHITE, self.open_button_clicked))
        self.widgets.append(Button(self.game, 'Save', 16 + (128 + 16) * 2, 16, 128, 64, self.game.textFont, Color.BLACK, Color.WHITE, self.save_button_clicked))
        self.widgets.append(ToggleButton(self.game, [ 'Grid off', 'Grid on' ], self.grid, 16 + (128 + 16) * 3 + 16, 16, 256, 64, self.game.textFont, Color.BLACK, Color.WHITE, Color.LIGHT_GRAY, self.grid_togglebutton_changed))
        self.widgets.append(Button(self.game, 'Back', self.game.width - (16 + 128), 16, 128, 64, self.game.textFont, Color.BLACK, Color.WHITE, self.back_button_clicked))

        self.sizeComboBox = ComboBox(self.game, [ '%s (%dx%d)' % (Config.MAP_SIZE_LABELS[i], size, size) for i, size in enumerate(Config.MAP_SIZES) ],
            0 if self.selectedSizeIndex == len(Config.MAP_SIZES) else self.selectedSizeIndex, 16, self.game.height - 64 - 16, (self.game.width - 16 * 3) // 2, 64, self.game.textFont, Color.BLACK, Color.WHITE, Color.LIGHT_GRAY, self.size_combo_box_changed)
        if self.selectedSizeIndex == len(Config.MAP_SIZES):
            self.sizeComboBox.set_text('Custom (%dx%d) \u25BC' % (self.map.width, self.map.height))
        self.widgets.append(self.sizeComboBox)
        self.brushComboBox = ComboBox(self.game, MapEditor.TOOL_LABELS, self.selectedBrushIndex, self.game.width // 2 + 8, self.game.height - 64 - 16, (self.game.width - 16 * 3) // 2, 64, self.game.textFont, Color.BLACK, Color.WHITE, Color.LIGHT_GRAY, self.brush_combo_box_changed)
        self.widgets.append(self.brushComboBox)

    # Handle map editor page events
    def handle_event(self, event):
        if Page.handle_event(self, event):
            return True

        # Handle key up events
        if event.type == pygame.KEYUP:
            if event.mod & pygame.KMOD_CTRL and event.key == pygame.K_n:
                self.new_button_clicked()
            if event.mod & pygame.KMOD_CTRL and event.key == pygame.K_o:
                self.open_button_clicked()
            if event.mod & pygame.KMOD_CTRL and event.key == pygame.K_s:
                self.save_button_clicked()

        return False

    # Update map editor widget
    def update(self, delta):
        self.mapEditor.update(delta)
        self.mapCamera['x'] = self.mapEditor.camera.x
        self.mapCamera['y'] = self.mapEditor.camera.y

    # New button clicked
    def new_button_clicked(self):
        self.file_path = None
        pygame.display.set_caption('Unsaved - BassieRacing')

        # When standard size
        for i, size in enumerate(Config.MAP_SIZES):
            if i == self.sizeComboBox.selectedOptionIndex:
                self.map = Map.generate_map(self.game, size, size)
                self.mapEditor.map = self.map
                self.mapEditor.center_camera()
                return

        # When custom size
        self.map = Map.generate_map(self.game, 32, 32)
        self.mapEditor.map = self.map
        self.mapEditor.center_camera()
        self.sizeComboBox.set_selected(1)

    # Open button clicked
    def open_button_clicked(self):
        file_path = tkinter.filedialog.askopenfilename(title='Select a BassieRacing Map to open...', filetypes=[ ( 'JSON files', '*.json' ) ])
        if file_path:
            self.game.focus()
            self.file_path = file_path
            pygame.display.set_caption(file_path + ' - BassieRacing')
            self.map = Map.load_from_file(file_path)
            if self.map != None:
                self.mapEditor.map = self.map
                self.mapEditor.center_camera()

                for i, size in enumerate(Config.MAP_SIZES):
                    if size == self.map.width:
                        self.selectedSizeIndex = i
                        self.sizeComboBox.set_selected(i)
                        return

                self.selectedSizeIndex = len(Config.MAP_SIZES)
                self.sizeComboBox.set_text('Custom (%dx%d) \u25BC' % (self.map.width, self.map.height))

    # Save button clicked
    def save_button_clicked(self):
        if self.file_path == None:
            file_path = tkinter.filedialog.asksaveasfilename(title='Select a location to save the BassieRacing Map...', filetypes=[ ( 'JSON files', '*.json' ) ], defaultextension='.json')
            if file_path:
                self.game.focus()
                self.file_path = file_path
                pygame.display.set_caption(file_path + ' - BassieRacing')

        if self.file_path != None:
            self.map.save_to_file(self.file_path)

    # Grid toggle button changed
    def grid_togglebutton_changed(self, active):
        self.grid = active
        self.mapEditor.grid = active
        self.mapEditor.camera.grid = active

    # Back button clicked
    def back_button_clicked(self):
        pygame.display.set_caption('BassieRacing')
        self.game.page = MenuPage(self.game)

    # Size combo box changed
    def size_combo_box_changed(self, selectedOptionIndex):
        self.selectedSizeIndex = selectedOptionIndex
        for i, size in enumerate(Config.MAP_SIZES):
            if i == selectedOptionIndex:
                self.map.resize(size, size)
                self.mapEditor.center_camera()
                break

    # Brush combo box changed
    def brush_combo_box_changed(self, selectedOptionIndex):
        self.selectedBrushIndex = selectedOptionIndex
        for i, label in enumerate(MapEditor.TOOL_LABELS):
            if i == selectedOptionIndex:
                self.mapEditor.tool = i
                break

# The help page class
class HelpPage(Page):
    # Create help page
    def __init__(self, game):
        Page.__init__(self, game)

    # Create help page widgets
    def create_widgets(self):
        y = (self.game.height - (72 + (64 + 16) * 5 + 64 + 32)) // 2
        self.widgets.append(Label(self.game, 'Help', 0, y, self.game.width, 72, self.game.titleFont, Color.WHITE))
        y += 72 + 16
        self.widgets.append(Label(self.game, 'BassieRacing is a topdown 2D two player racing game', 0, y, self.game.width, 64, self.game.textFont, Color.WHITE))
        y += 64 + 16
        self.widgets.append(Label(self.game, 'You can control the main/left car by using WASD keys', 0, y, self.game.width, 64, self.game.textFont, Color.WHITE))
        y += 64 + 16
        self.widgets.append(Label(self.game, 'You can control the right car by using the arrow keys', 0, y, self.game.width, 64, self.game.textFont, Color.WHITE))
        y += 64 + 16
        self.widgets.append(Label(self.game, 'There are multiple maps and vehicles that you can try', 0, y, self.game.width, 64, self.game.textFont, Color.WHITE))
        y += 64 + 16
        self.widgets.append(Label(self.game, 'You can also create or edit custom maps', 0, y, self.game.width, 64, self.game.textFont, Color.WHITE))
        y += 64 + 32
        self.widgets.append(Button(self.game, 'Back', self.game.width // 4, y, self.game.width // 2, 64, self.game.textFont, Color.BLACK, Color.WHITE, self.back_button_clicked))

    # Back button clicked event
    def back_button_clicked(self):
        self.game.page = MenuPage(self.game)

# The settings page class
class SettingsPage(Page):
    # Create settings page
    def __init__(self, game):
        Page.__init__(self, game)

    # Create settings page widgets
    def create_widgets(self):
        y = (self.game.height - (72 + (64 + 16) * 5 + 8 + 24 + 64)) // 2
        self.widgets.append(Label(self.game, 'Settings', 0, y, self.game.width, 72, self.game.titleFont, Color.WHITE))
        y += 72 + 16
        self.widgets.append(ToggleButton(self.game, [ 'Intro disabled', 'Intro enabled' ], self.game.settings['intro']['enabled'], self.game.width // 6, y, self.game.width // 3 * 2, 64, self.game.textFont, Color.BLACK, Color.WHITE, Color.LIGHT_GRAY, self.intro_toggle_button_changed))
        y += 64 + 16
        self.widgets.append(ToggleButton(self.game, [ 'Fancy music disabled', 'Fancy music enabled' ], self.game.settings['music']['enabled'], self.game.width // 6, y, self.game.width // 3 * 2, 64, self.game.textFont, Color.BLACK, Color.WHITE, Color.LIGHT_GRAY, self.music_toggle_button_changed))
        y += 64 + 16
        self.widgets.append(ToggleButton(self.game, [ 'Sound effects disabled', 'Sound effects enabled' ], self.game.settings['sound-effects']['enabled'], self.game.width // 6, y, self.game.width // 3 * 2, 64, self.game.textFont, Color.BLACK, Color.WHITE, Color.LIGHT_GRAY, self.sound_effects_toggle_button_changed))
        y += 64 + 24
        self.widgets.append(Button(self.game, 'Resest high scores', self.game.width // 6, y, self.game.width // 3 * 2, 64, self.game.textFont, Color.BLACK, Color.WHITE, self.reset_high_scores_button_clicked))
        y += 64 + 16
        self.widgets.append(Button(self.game, 'Clear custom maps cache', self.game.width // 6, y, self.game.width // 3 * 2, 64, self.game.textFont, Color.BLACK, Color.WHITE, self.clear_custom_maps_cache_button_clicked))
        y += 64 + 24
        self.widgets.append(Button(self.game, 'Back', self.game.width // 4, y, self.game.width // 2, 64, self.game.textFont, Color.BLACK, Color.WHITE, self.back_button_clicked))

    # Intro toggle button changed
    def intro_toggle_button_changed(self, active):
        self.game.settings['intro']['enabled'] = active
        self.game.save_settings()

    # Music toggle button changed
    def music_toggle_button_changed(self, active):
        self.game.settings['music']['enabled'] = active
        self.game.save_settings()

        if active:
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.play(0, self.game.settings['music']['position'])
            else:
                pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()

    # Sound effects toggle button changed
    def sound_effects_toggle_button_changed(self, active):
        self.game.settings['sound-effects']['enabled'] = active
        self.game.save_settings()

    # Reset high scores button clicked
    def reset_high_scores_button_clicked(self):
        self.game.settings['high-scores'] = []
        self.game.save_settings()

    # Clear custom maps cache button clicked
    def clear_custom_maps_cache_button_clicked(self):
        self.game.settings['custom-maps'] = []
        self.game.save_settings()

    # Back button clicked event
    def back_button_clicked(self):
        self.game.page = MenuPage(self.game)
