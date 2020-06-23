# BassieRacing - Pages

# Import modules
from constants import *
import math
from objects import *
import random
import tkinter.filedialog
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
        y = ((self.game.height - 32) - (96 + (64 + 16) * 5)) // 2
        self.widgets.append(Label(self.game, 'BassieRacing', 0, y, self.game.width, 96, self.game.titleFont, Color.WHITE))
        y += 96 + 16
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
        self.game.page = SelectMapPage(self.game)

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

# The select map page class
class SelectMapPage(Page):
    # Create select map page
    def __init__(self, game):
        self.selectedMapIndex = None
        self.customMapPaths = []
        Page.__init__(self, game)

    # Create select map page widgets
    def create_widgets(self):
        self.widgets.append(Label(self.game, 'Select a map to race', 0, 24, self.game.width, 96, self.game.titleFont, Color.WHITE))
        self.mapSelector = MapSelector(self.game, 16, 24 + 96 + 16, self.game.width - 16 - 16, self.game.height - (24 + 96 + 16) - (48 + 64 + 16), self.selectedMapIndex, self.customMapPaths, self.map_selector_changed)
        self.widgets.append(self.mapSelector)
        self.widgets.append(Button(self.game, 'Back', 16, self.game.height - 64 - 16, 240, 64, self.game.textFont, Color.BLACK, Color.WHITE, self.back_button_clicked))
        self.widgets.append(Button(self.game, 'Load custom map', (self.game.width - 420) // 2, self.game.height - 64 - 16, 420, 64, self.game.textFont, Color.BLACK, Color.WHITE, self.load_button_clicked))
        self.widgets.append(Button(self.game, 'Continue', self.game.width - 16 - 240, self.game.height - 64 - 16, 240, 64, self.game.textFont, Color.BLACK, Color.WHITE, self.continue_button_clicked))

    # Map selector changed
    def map_selector_changed(self, selectedMapIndex):
        self.selectedMapIndex = selectedMapIndex

    # Back button clicked
    def back_button_clicked(self):
        self.game.page = MenuPage(self.game)

    # Load button clicked
    def load_button_clicked(self):
        file_path = tkinter.filedialog.askopenfilename(title='Select a BassieRacing Map to load...', filetypes=[ ( 'JSON files', '*.json' ) ])
        if file_path:
            self.game.focus()
            self.customMapPaths.append(file_path)
            self.mapSelector.load_map(file_path)

    # Continue button clicked
    def continue_button_clicked(self):
        self.game.page = SelectVehiclePage(self.game, self.mapSelector.selectedMap)

# The select vehicle page class
class SelectVehiclePage(Page):
    # Create select vehicle page
    def __init__(self, game, map):
        self.map = map
        self.leftSelectedVehicleIndex = None
        self.rightSelectedVehicleIndex = None
        Page.__init__(self, game)

    # Create select vehicle page widgets
    def create_widgets(self):
        self.widgets.append(Label(self.game, 'Select both your vehicle', 0, 24, self.game.width, 96, self.game.titleFont, Color.WHITE))
        self.leftVehicleSelector = VehicleSelector(self.game, 16, 24 + 96 + 16, self.game.width // 2 - (16 + 16), self.game.height - (24 + 96 + 16) - (48 + 64 + 16), 0, self.leftSelectedVehicleIndex, self.left_vehicle_selector_changed)
        self.widgets.append(self.leftVehicleSelector)
        self.rightVehicleSelector = VehicleSelector(self.game, 16 + self.game.width // 2, 24 + 96 + 16, self.game.width // 2 - (16 + 16), self.game.height - (24 + 96 + 16) - (48 + 64 + 16), 1, self.rightSelectedVehicleIndex, self.right_vehicle_selector_changed)
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
        self.game.page = SelectMapPage(self.game)

    # Race button clicked
    def race_button_clicked(self):
        self.game.page = GamePage(self.game, self.map, self.leftVehicleSelector.selectedVehicle, self.rightVehicleSelector.selectedVehicle)

# The game page class
class GamePage(Page):
    # Create game page
    def __init__(self, game, map, leftVehicleType, rightVehicleType):
        # Set map
        self.map = map

        # Create the vehicles
        self.vehicles = []

        # Check if finish is horizontal
        if map.finish['height'] > map.finish['width']:
            self.leftVehicle = Vehicle(game, 0, leftVehicleType, 0, map, self.vehicles,
                (map.finish['x'] - 1) * Config.TILE_SPRITE_SIZE + Config.TILE_SPRITE_SIZE / 2,
                (map.finish['y'] + map.finish['height'] // 2 - 1) * Config.TILE_SPRITE_SIZE + Config.TILE_SPRITE_SIZE / 2,
                math.radians(270)
            )
            self.vehicles.append(self.leftVehicle)

            self.rightVehicle = Vehicle(game, 1, rightVehicleType, 1, map, self.vehicles,
                (map.finish['x'] - 1)  * Config.TILE_SPRITE_SIZE + Config.TILE_SPRITE_SIZE / 2,
                (map.finish['y'] + map.finish['height'] // 2)  * Config.TILE_SPRITE_SIZE + Config.TILE_SPRITE_SIZE / 2,
                math.radians(270)
            )
            self.vehicles.append(self.rightVehicle)

        # Or when the finish is vertical
        else:
            self.leftVehicle = Vehicle(game, 0, leftVehicleType, 0, map, self.vehicles,
                (map.finish['x'] + map.finish['width'] // 2 - 1) * Config.TILE_SPRITE_SIZE + Config.TILE_SPRITE_SIZE / 2,
                (map.finish['y'] + map.finish['height']) * Config.TILE_SPRITE_SIZE + Config.TILE_SPRITE_SIZE / 2,
                0
            )
            self.vehicles.append(self.leftVehicle)

            self.rightVehicle = Vehicle(game, 1, rightVehicleType, 1, map, self.vehicles,
                (map.finish['x'] + map.finish['width'] // 2)  * Config.TILE_SPRITE_SIZE + Config.TILE_SPRITE_SIZE / 2,
                (map.finish['y'] + map.finish['height'])  * Config.TILE_SPRITE_SIZE + Config.TILE_SPRITE_SIZE / 2,
                0
            )
            self.vehicles.append(self.rightVehicle)

        # Create page
        Page.__init__(self, game, Color.BLACK)

    # Create game page widgets
    def create_widgets(self):
        self.leftVehicleViewport = VehicleViewport(self.game, self.leftVehicle, 0, 0, self.game.width // 2 - 1, self.game.height, self.map, self.vehicles)
        self.widgets.append(self.leftVehicleViewport)
        self.rightVehicleViewport = VehicleViewport(self.game, self.rightVehicle, self.game.width // 2 + 1, 0, self.game.width // 2 - 1, self.game.height, self.map, self.vehicles)
        self.widgets.append(self.rightVehicleViewport)
        minimap_size = self.game.width / 5
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
        self.rightVehicleViewport.update(delta)

        # When countdown is over start cars
        if not self.leftVehicle.started and self.leftVehicleViewport.countdownClock.ended:
            self.leftVehicle.started = True

        if not self.rightVehicle.started and self.rightVehicleViewport.countdownClock.ended:
            self.rightVehicle.started = True

        # Update all the vehicles
        for vehicle in self.vehicles:
            if vehicle.id == 0:
                vehicle.update(delta, self.leftVehicleViewport.camera)
            if vehicle.id == 1:
                vehicle.update(delta, self.rightVehicleViewport.camera)

# The edit page class
class EditorPage(Page):
    # Create edit page
    def __init__(self, game):
        self.file_path = None
        pygame.display.set_caption('Unsaved - BassieRacing')
        self.map = Map('Custom Map', 32, 32)
        self.map.generate()
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
                self.map = Map('Custom Map', size, size)
                self.map.generate()
                self.mapEditor.map = self.map
                self.mapEditor.center_camera()
                return

        # When custom size
        self.map = Map('Custom Map', 32, 32)
        self.map.generate()
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
        y = (self.game.height - (96 + (64 + 16) * 5 + 64 + 32)) // 2
        self.widgets.append(Label(self.game, 'Help', 0, y, self.game.width, 96, self.game.titleFont, Color.WHITE))
        y += 96 + 16
        self.widgets.append(Label(self.game, 'BassieRacing is a topdown 2D two player racing game', 0, y, self.game.width, 64, self.game.textFont, Color.WHITE))
        y += 64 + 16
        self.widgets.append(Label(self.game, 'You can control the left car by using WASD keys', 0, y, self.game.width, 64, self.game.textFont, Color.WHITE))
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
        y = (self.game.height - (96 + (64 + 16) * 3 + 24 + 64)) // 2
        self.widgets.append(Label(self.game, 'Settings', 0, y, self.game.width, 96, self.game.titleFont, Color.WHITE))
        y += 96 + 16
        self.widgets.append(ToggleButton(self.game, [ 'Intro disabled', 'Intro enabled' ], self.game.settings['intro']['enabled'], self.game.width // 6, y, self.game.width // 3 * 2, 64, self.game.textFont, Color.BLACK, Color.WHITE, Color.LIGHT_GRAY, self.intro_toggle_button_changed))
        y += 64 + 16
        self.widgets.append(ToggleButton(self.game, [ 'Fancy music disabled', 'Fancy music enabled' ], self.game.settings['music']['enabled'], self.game.width // 6, y, self.game.width // 3 * 2, 64, self.game.textFont, Color.BLACK, Color.WHITE, Color.LIGHT_GRAY, self.music_toggle_button_changed))
        y += 64 + 16
        self.widgets.append(ToggleButton(self.game, [ 'Sound effects disabled', 'Sound effects enabled' ], self.game.settings['sound-effects']['enabled'], self.game.width // 6, y, self.game.width // 3 * 2, 64, self.game.textFont, Color.BLACK, Color.WHITE, Color.LIGHT_GRAY, self.sound_effects_toggle_button_changed))
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

    # Back button clicked event
    def back_button_clicked(self):
        self.game.page = MenuPage(self.game)
