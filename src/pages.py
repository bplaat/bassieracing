# BassieRacing - Pages

# Import modules
from constants import *
import math
from objects import *
import random
import tkinter.filedialog
import tkinter.messagebox
import webbrowser
from widgets import *

# The page class
class Page:
    # Create empty page
    def __init__(self, game):
        self.game = game

        # Pick random background
        self.backgroundColor = (random.randint(50, 150), random.randint(50, 150), random.randint(50, 150))

        # Create empty widgets list
        self.widgets = []

    # Handle page events
    def handle_event(self, event):
        # Send all events to the widgets
        for widget in reversed(self.widgets):
            if widget.handle_event(event):
                return True

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

# The menu page class
class MenuPage(Page):
    # Create menu page
    def __init__(self, game):
        Page.__init__(self, game)

        # Create menu page widgets
        y = 128
        self.widgets.append(Label('BassieRacing', 0, y, Config.WIDTH, 96, game.titleFont, Color.WHITE))
        y += 96 + 16
        self.widgets.append(Button('Play', Config.WIDTH // 4, y, Config.WIDTH // 2, 64, game.textFont, Color.BLACK, Color.WHITE, self.play_button_clicked))
        y += 64 + 16
        self.widgets.append(Button('Map Editor', Config.WIDTH // 4, y, Config.WIDTH // 2, 64, game.textFont, Color.BLACK, Color.WHITE, self.edit_button_clicked))
        y += 64 + 16
        self.widgets.append(Button('Help', Config.WIDTH // 4, y, Config.WIDTH // 2, 64, game.textFont, Color.BLACK, Color.WHITE, self.help_button_clicked))
        y += 64 + 16
        self.widgets.append(Button('Exit', Config.WIDTH // 4, y, Config.WIDTH // 2, 64, game.textFont, Color.BLACK, Color.WHITE, self.exit_button_clicked))
        self.widgets.append(Label('v' + Config.VERSION, Config.WIDTH - 16 - 96, 16, 96, 32, game.textFont, Color.WHITE, self.version_label_clicked))
        self.widgets.append(Label('Made by Bastiaan van der Plaat', 0, Config.HEIGHT - 64 - 16, Config.WIDTH, 64, game.textFont, Color.WHITE, self.footer_label_clicked))

    # Version label clicked
    def version_label_clicked(self):
        webbrowser.open_new('https://github.com/bplaat/bassieracing')

    # Play button clicked
    def play_button_clicked(self):
        self.game.page = SelectMapPage(self.game)

    # Edit button clicked
    def edit_button_clicked(self):
        self.game.page = EditorPage(self.game)

     # Help button clicked
    def help_button_clicked(self):
        self.game.page = HelpPage(self.game)

    # Exit button clicked
    def exit_button_clicked(self):
        self.game.running = False

    # Footer label clicked
    def footer_label_clicked(self):
        webbrowser.open_new('https://bastiaan.ml/')

# The select map page class
class SelectMapPage(Page):
    # Create select map page
    def __init__(self, game):
        Page.__init__(self, game)

        # Create select map page widgets
        self.widgets.append(Label('Select a map to race', 0, 24, Config.WIDTH, 96, game.titleFont, Color.WHITE))
        self.widgets.append(Label('Comming soon...', 0, 0, Config.WIDTH, Config.HEIGHT, game.textFont, Color.WHITE))
        self.widgets.append(Button('Back', 16, Config.HEIGHT - 64 - 16, 240, 64, game.textFont, Color.BLACK, Color.WHITE, self.back_button_clicked))
        self.widgets.append(Button('Continue', Config.WIDTH - 16 - 240, Config.HEIGHT - 64 - 16, 240, 64, game.textFont, Color.BLACK, Color.WHITE, self.continue_button_clicked))

    # Back button clicked
    def back_button_clicked(self):
        self.game.page = MenuPage(self.game)

    # Continue button clicked
    def continue_button_clicked(self):
        self.game.page = SelectVehiclePage(self.game)

# The select vehicle page class
class SelectVehiclePage(Page):
    # Create select vehicle page
    def __init__(self, game):
        Page.__init__(self, game)

        # Create select vehicle page widgets
        self.widgets.append(Label('Select both your vehicle', 0, 24, Config.WIDTH, 96, game.titleFont, Color.WHITE))
        self.leftVehicleSelector = VehicleSelector(game, 16, 32 + 96 + 16, Config.WIDTH // 2 - (16 + 16), Config.HEIGHT - (32 + 96 + 16) - (48 + 64 + 16), 0)
        self.widgets.append(self.leftVehicleSelector)
        self.rightVehicleSelector = VehicleSelector(game, 16 + Config.WIDTH // 2, 32 + 96 + 16, Config.WIDTH // 2 - (16 + 16), Config.HEIGHT - (32 + 96 + 16) - (48 + 64 + 16), 1)
        self.widgets.append(self.rightVehicleSelector)
        self.widgets.append(Button('Back', 16, Config.HEIGHT - 64 - 16, 240, 64, game.textFont, Color.BLACK, Color.WHITE, self.back_button_clicked))
        self.widgets.append(Button('Race!', Config.WIDTH - 16 - 240, Config.HEIGHT - 64 - 16, 240, 64, game.textFont, Color.BLACK, Color.WHITE, self.race_button_clicked))

    # Back button clicked
    def back_button_clicked(self):
        self.game.page = SelectMapPage(self.game)

    # Race button clicked
    def race_button_clicked(self):
        self.game.page = GamePage(self.game, self.leftVehicleSelector.selectedVehicle, self.rightVehicleSelector.selectedVehicle)

# The game page class
class GamePage(Page):
    # Create game page
    def __init__(self, game, leftVehicleType, rightVehicleType):
        Page.__init__(self, game)

        # Init the map
        self.map = Map.load_from_file(game.tilesImage, 'assets/maps/map.json')

        # Init the vehicles
        self.vehicles = []

        leftVehicle = Vehicle(game.vehiclesImage, 0, leftVehicleType, 0,
            self.map.startX * Config.TILE_SPRITE_SIZE + Config.TILE_SPRITE_SIZE / 2,
            self.map.startY * Config.TILE_SPRITE_SIZE + Config.TILE_SPRITE_SIZE / 2,
            self.map.startAngle
        )
        self.vehicles.append(leftVehicle)

        rightVehicle = Vehicle(game.vehiclesImage, 1, rightVehicleType, 1,
            self.map.startX * Config.TILE_SPRITE_SIZE + Config.TILE_SPRITE_SIZE / 2,
            self.map.startY * Config.TILE_SPRITE_SIZE + Config.TILE_SPRITE_SIZE * 1.5,
            self.map.startAngle
        )
        self.vehicles.append(rightVehicle)

        # Create game page widgets
        self.widgets.append(VehicleViewport(game, leftVehicle, 0, 0, Config.WIDTH // 2, Config.HEIGHT, self.map, self.vehicles))
        self.widgets.append(VehicleViewport(game, rightVehicle, Config.WIDTH // 2, 0, Config.WIDTH // 2, Config.HEIGHT, self.map, self.vehicles))
        self.widgets.append(Button('Back', Config.WIDTH - 16 - 128, 16, 128, 64, game.textFont, Color.BLACK, Color.WHITE, self.back_button_clicked))

    # Back button clicked
    def back_button_clicked(self):
        self.game.page = MenuPage(self.game)

    # Update game page
    def update(self, delta):
        # Update all the vehicles
        for vehicle in self.vehicles:
            vehicle.update(delta)

# The edit page class
class EditorPage(Page):
    # Create edit page
    def __init__(self, game):
        Page.__init__(self, game)

        self.map = Map(game.tilesImage, 'Custom Map', 32, 32)

        # Create edit page widgets
        self.mapEditor = MapEditor(game, self.map, 0, 0, Config.WIDTH, Config.HEIGHT, MapEditor.ASPHALT_BRUSH)
        self.widgets.append(self.mapEditor)

        self.widgets.append(Button('New', 16, 16, 128, 64, game.textFont, Color.BLACK, Color.WHITE, self.new_button_clicked))
        self.widgets.append(Button('Load', 16 + (128 + 16), 16, 128, 64, game.textFont, Color.BLACK, Color.WHITE, self.load_button_clicked))
        self.widgets.append(Button('Save', 16 + (128 + 16) * 2, 16, 128, 64, game.textFont, Color.BLACK, Color.WHITE, self.save_button_clicked))

        self.widgets.append(Button('Back', Config.WIDTH - (16 + 128), 16, 128, 64, game.textFont, Color.BLACK, Color.WHITE, self.back_button_clicked))

        self.sizeComboBox = ComboBox([ '%s (%dx%d)' % (Config.MAP_SIZE_LABELS[i], Config.MAP_SIZES[i], Config.MAP_SIZES[i]) for i in range(len(Config.MAP_SIZES)) ], 1, 16, Config.HEIGHT - 64 - 16, (Config.WIDTH - 16 * 3) // 2, 64, game.textFont, Color.BLACK, Color.WHITE, Color.LIGHT_GRAY, self.size_combobox_changed)
        self.widgets.append(self.sizeComboBox)
        self.brushComboBox = ComboBox(MapEditor.TOOL_LABELS, 3, Config.WIDTH // 2 + 8, Config.HEIGHT - 64 - 16, (Config.WIDTH - 16 * 3) // 2, 64, game.textFont, Color.BLACK, Color.WHITE, Color.LIGHT_GRAY, self.brush_combobox_changed)
        self.widgets.append(self.brushComboBox)

    # Update map editor
    def update(self, delta):
        self.mapEditor.update(delta)

    # New button clicked
    def new_button_clicked(self):
        for i in range(len(Config.MAP_SIZES)):
            if i == self.sizeComboBox.selectedItem:
                self.map = Map(self.game.tilesImage, 'Custom Map', Config.MAP_SIZES[i], Config.MAP_SIZES[i])
                self.mapEditor.set_map(self.map)
                self.mapEditor.center_camera()
                return

        # When custom size
        self.map = Map(self.game.tilesImage, 'Custom Map', 32, 32)
        self.mapEditor.set_map(self.map)
        self.mapEditor.center_camera()
        self.sizeComboBox.set_selected(1)

    # Load button clicked
    def load_button_clicked(self):
        path = tkinter.filedialog.askopenfilename(filetypes=[ ( 'JSON files', '*.json' ) ])
        if path != '':
            self.map = Map.load_from_file(self.game.tilesImage, path)
            self.mapEditor.set_map(self.map)
            self.mapEditor.center_camera()

            for i in range(len(Config.MAP_SIZES)):
                if Config.MAP_SIZES[i] == self.map.width:
                    self.sizeComboBox.set_selected(i)
                    return

            self.sizeComboBox.selectedItem = len(self.sizeComboBox.options)
            self.sizeComboBox.set_text('Custom (%dx%d) \u25BC' % (self.map.width, self.map.height))

    # Save button clicked
    def save_button_clicked(self):
        path = tkinter.filedialog.asksaveasfilename(filetypes=[ ( 'JSON files', '*.json' ) ], defaultextension='.json')
        if path != '':
            self.map.save_to_file(path)

    # Back button clicked
    def back_button_clicked(self):
        self.game.page = MenuPage(self.game)

    # Size combobox changed
    def size_combobox_changed(self, selectedItem):
        for i in range(len(Config.MAP_SIZES)):
            if selectedItem == i:
                self.map.resize(Config.MAP_SIZES[i], Config.MAP_SIZES[i])
                self.mapEditor.center_camera()
                break

    # Brush combobox changed
    def brush_combobox_changed(self, selectedItem):
        for i in range(len(MapEditor.TOOL_LABELS)):
            if selectedItem == i:
                self.mapEditor.tool = i
                break

# The help page class
class HelpPage(Page):
    # Create help page
    def __init__(self, game):
        Page.__init__(self, game)

        # Create help page widgets
        y = 64
        self.widgets.append(Label('Help', 0, y, Config.WIDTH, 96, game.titleFont, Color.WHITE))
        y += 96 + 16
        self.widgets.append(Label('BassieRacing is a topdown 2D two player racing game', 0, y, Config.WIDTH, 64, game.textFont, Color.WHITE))
        y += 64 + 16
        self.widgets.append(Label('You can control the left car by using WASD keys', 0, y, Config.WIDTH, 64, game.textFont, Color.WHITE))
        y += 64 + 16
        self.widgets.append(Label('You can control the right car by using the arrow keys', 0, y, Config.WIDTH, 64, game.textFont, Color.WHITE))
        y += 64 + 16
        self.widgets.append(Label('There are multiple maps and vehicles that you can try', 0, y, Config.WIDTH, 64, game.textFont, Color.WHITE))
        y += 64 + 16
        self.widgets.append(Label('You can also create or edit custom maps', 0, y, Config.WIDTH, 64, game.textFont, Color.WHITE))
        y += 64 + 32
        self.widgets.append(Button('Back', Config.WIDTH // 4, y, Config.WIDTH // 2, 64, game.textFont, Color.BLACK, Color.WHITE, self.back_button_clicked))

    # Back button clicked event
    def back_button_clicked(self):
        self.game.page = MenuPage(self.game)
