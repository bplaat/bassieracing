# BassieRacing - Widgets

# Import modules
from constants import *
from objects import *
import os
import pygame
import random
from stats import *
from utils import *

# The rect widget class
class Rect:
    # Create rect
    def __init__(self, game, x, y, width, height, color, clickCallback = None, callbackExtra = None):
        self.game = game
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.clickCallback = clickCallback
        self.callbackExtra = callbackExtra

    # Handle rect events
    def handle_event(self, event):
        # Handle mouse events
        if (
            self.clickCallback != None and
            event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP) and
            event.pos[0] >= self.x and event.pos[1] >= self.y and
            event.pos[0] < self.x + self.width and event.pos[1] < self.y + self.height
        ):
            if event.type == pygame.MOUSEBUTTONUP:
                if self.game.settings['sound-effects']['enabled']:
                    self.game.clickSound.play()

                if self.callbackExtra != None:
                    self.clickCallback(self.callbackExtra)
                else:
                    self.clickCallback()
            return True

        return False

    # Draw rect
    def draw(self, surface):
        if self.color != None:
            surface.fill(self.color, ( self.x, self.y, self.width, self.height ))

# The label widget class
class Label:
    # Create label
    def __init__(self, game, text, x, y, width, height, font, color, align = TextAlign.CENTER, clickCallback = None, callbackExtra = None):
        self.game = game
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font = font
        self.color = color
        self.align = align
        self.text = text
        self.textSurface = font.render(text, True, color)
        self.clickCallback = clickCallback
        self.callbackExtra = callbackExtra

    # Update label text
    def set_text(self, text):
        if text != self.text:
            self.text = text
            self.textSurface = self.font.render(self.text, True, self.color)

    # Handle label events
    def handle_event(self, event):
        # Handle mouse events
        if (
            self.clickCallback != None and
            event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP) and
            event.pos[0] >= self.x and event.pos[1] >= self.y and
            event.pos[0] < self.x + self.width and event.pos[1] < self.y + self.height
        ):
            if event.type == pygame.MOUSEBUTTONUP:
                if self.game.settings['sound-effects']['enabled']:
                    self.game.clickSound.play()

                if self.callbackExtra != None:
                    self.clickCallback(self.callbackExtra)
                else:
                    self.clickCallback()
            return True

        return False

    # Draw label
    def draw(self, surface):
        if self.align == TextAlign.LEFT:
            surface.blit(self.textSurface, (
                self.x,
                self.y + (self.height - self.textSurface.get_height()) // 2
            ))

        if self.align == TextAlign.CENTER:
            surface.blit(self.textSurface, (
                self.x + (self.width - self.textSurface.get_width()) // 2,
                self.y + (self.height - self.textSurface.get_height()) // 2
            ))

        if self.align == TextAlign.RIGHT:
            surface.blit(self.textSurface, (
                self.x + (self.width - self.textSurface.get_width()),
                self.y + (self.height - self.textSurface.get_height()) // 2
            ))

# The button widget class
class Button(Label):
    # Create button
    def __init__(self, game, text, x, y, width, height, font, color, backgroundColor, clickCallback = None, callbackExtra = None):
        Label.__init__(self, game, text, x, y, width, height, font, color, TextAlign.CENTER, clickCallback, callbackExtra)
        self.backgroundColor = backgroundColor

    # Draw button
    def draw(self, surface):
        surface.fill(self.backgroundColor, ( self.x, self.y, self.width, self.height ))
        Label.draw(self, surface)

# The toggle button widget class
class ToggleButton(Button):
    # Create toggle button
    def __init__(self, game, labels, active, x, y, width, height, font, color, backgroundColor, activeBackgroundColor, changedCallback = None, callbackExtra = None):
        self.labels = labels
        self.active = False
        self.blurBackgroundColor = backgroundColor
        self.activeBackgroundColor = activeBackgroundColor
        self.changedCallback = changedCallback
        self.callbackExtra = callbackExtra
        Button.__init__(self, game, labels[0], x, y, width, height, font, color, backgroundColor, self.button_clicked)
        self.set_active(active)

    # Set active item
    def set_active(self, active):
        if active != self.active:
            self.active = active
            self.set_text(self.labels[int(active)])
            if active:
                self.backgroundColor = self.activeBackgroundColor
            else:
                self.backgroundColor = self.blurBackgroundColor

    # Button clicked
    def button_clicked(self):
        self.set_active(not self.active)

        # Call change callback
        if self.changedCallback != None:
            if self.callbackExtra != None:
                self.changedCallback(self.active, self.callbackExtra)
            else:
                self.changedCallback(self.active)

# The combo box widget class
class ComboBox(Button):
    # Create combo box
    def __init__(self, game, options, selectedOptionIndex, x, y, width, height, font, color, backgroundColor, activeBackgroundColor, changedCallback = None, callbackExtra = None):
        self.options = options
        self.selectedOptionIndex = selectedOptionIndex
        self.selectedOption = options[selectedOptionIndex]
        Button.__init__(self, game, options[self.selectedOptionIndex] + ' \u25BC', x, y, width, height, font, color, backgroundColor, self.root_button_clicked)
        self.blurBackgroundColor = backgroundColor
        self.activeBackgroundColor = activeBackgroundColor
        self.changedCallback = changedCallback
        self.callbackExtra = callbackExtra
        self.active = False

        # Create combo box widgets
        ry = y + height
        if len(options) * height > game.height - (y + height):
            ry = y - len(options) * height

        self.widgets = []
        for i, option in enumerate(options):
            self.widgets.append(Button(game, option, x, ry, width, height, font, color, backgroundColor, self.option_button_clicked, i))
            ry += height

    # Set selected option
    def set_selected(self, selectedOptionIndex):
        if selectedOptionIndex != self.selectedOptionIndex:
            self.selectedOptionIndex = selectedOptionIndex
            self.selectedOption = self.options[selectedOptionIndex]
            self.set_text(self.options[selectedOptionIndex] + ' \u25BC')

    # Root button clicked
    def root_button_clicked(self):
        # Toggle active
        self.active = not self.active
        if self.active:
            self.backgroundColor = self.activeBackgroundColor
        else:
            self.backgroundColor = self.blurBackgroundColor

    # Option button clicked
    def option_button_clicked(self, optionIndex):
        # Update root button
        self.active = False
        self.backgroundColor = self.blurBackgroundColor
        self.set_selected(optionIndex)

        # Call change callback
        if self.changedCallback != None:
            if self.callbackExtra != None:
                self.changedCallback(optionIndex, self.callbackExtra)
            else:
                self.changedCallback(optionIndex)

    # Handle combo box events
    def handle_event(self, event):
        # If active handle widget events
        if self.active:
            for widget in reversed(self.widgets):
                if widget.handle_event(event):
                    return True

        # Handle root button events
        return Button.handle_event(self, event)

    # Draw combo box
    def draw(self, surface):
        # Draw root button
        Button.draw(self, surface)

        # If active draw widgets
        if self.active:
            for widget in self.widgets:
                widget.draw(surface)

# The image widget class
class Image:
    # Create image
    def __init__(self, image, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.set_image(image)

    # Set image image
    def set_image(self, image):
        if isinstance(image, str):
            self.surface = pygame.image.load(image).convert_alpha()
        elif isinstance(image, pygame.Surface):
            self.surface = image
        elif image == None:
            self.surface = None
        else:
            raise ValueError('Image is not a file path, a surface or None!')

    # Handle image events
    def handle_event(self, event):
        return False

    # Draw image
    def draw(self, surface):
        if self.surface != None:
            surface.blit(self.surface, (
                self.x + (self.width - self.surface.get_width()) // 2,
                self.y + (self.height - self.surface.get_height()) // 2
            ))

# The mini map widget class
class MiniMap:
    # Create mini map
    def __init__(self, game, map, vehicles, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.game = game
        self.vehicles = vehicles
        self.surface = pygame.Surface(( width, height ), pygame.SRCALPHA)
        self.set_map(map)

    # Set map
    def set_map(self, map):
        self.map = map
        self.tileSize = self.width // map.width
        self.vehicleScale = (self.tileSize * 5) / Config.TILE_SPRITE_SIZE
        self.camera = Camera(
            (map.width * self.tileSize) / 2,
            (map.height * self.tileSize) / 2,
            self.game.tilesImage, self.tileSize,
            self.game.vehiclesImage, self.vehicleScale
        )

        if self.vehicles != None:
            for vehicle in self.vehicles:
                vehicle.cropImage(self.camera)

        # Draw the map tiles once for performace
        self.surface.fill(Color.TRANSPARENT)
        self.map.draw(self.surface, self.camera)

    # Handle mini map events
    def handle_event(self, event):
        return False

    # Draw mini map
    def draw(self, surface):
        # Draw vehicles if given
        if self.vehicles != None:
            # Copy the surface to draw the vehicles
            surfaceCopy = self.surface.copy()

            # Draw the vehicles if given
            for vehicle in self.vehicles:
                rotatedVehicleImage = pygame.transform.rotate(self.camera.vehicleImageCache[vehicle.id], math.degrees(vehicle.angle))
                x = math.floor((vehicle.x / (Config.TILE_SPRITE_SIZE / self.tileSize)) - rotatedVehicleImage.get_width() / 2 - (self.camera.x - self.width / 2))
                y = math.floor((vehicle.y / (Config.TILE_SPRITE_SIZE / self.tileSize)) - rotatedVehicleImage.get_height() / 2 - (self.camera.y - self.height / 2))
                if (
                    x + rotatedVehicleImage.get_width() >= 0 and y + rotatedVehicleImage.get_height() >= 0 and
                    x - rotatedVehicleImage.get_width() < self.width and y - rotatedVehicleImage.get_height() < self.height
                ):
                    surfaceCopy.blit(rotatedVehicleImage, ( x, y ))

            # Draw surface
            surface.blit(surfaceCopy, ( self.x, self.y ))
        else:
            # Draw surface
            surface.blit(self.surface, ( self.x, self.y ))

# The countdown clock widget
class CountdownClock:
    # Create the countdown clock widget
    def __init__(self, game, x, y, width, height):
        self.game = game
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.tickPadding = 8
        self.tickSize = width // Config.COUNTDOWN_CLOCK_TICKS - self.tickPadding * 2

        self.ended = False
        self.tick = 0
        self.tickTime = self.game.time

    # Update the countdown clock widget
    def update(self, delta):
        # Only draw the clock when not ended
        if not self.ended:
            # When the tick time passed
            if self.game.time - self.tickTime > Config.COUNTDOWN_CLOCK_TICK_TIME:
                # Stop the clock
                if self.tick == Config.COUNTDOWN_CLOCK_TICKS:
                    self.ended = True
                    return

                # Go to the next tick
                self.tick += 1
                self.tickTime = self.game.time

                # When the final tick has been reached stop and play sound
                if self.tick == Config.COUNTDOWN_CLOCK_TICKS:
                    if self.game.settings['sound-effects']['enabled']:
                        self.game.tockSound.play()
                else:
                    if self.game.settings['sound-effects']['enabled']:
                        self.game.tickSound.play()

    # Draw the countdown clock widget
    def draw(self, surface):
        # Only draw the clock when not ended
        if not self.ended:
            # Draw dark frame
            pygame.draw.rect(surface, Color.DARK, ( self.x, self.y, self.width, self.height))

            # Draw the ticks
            for i in range(Config.COUNTDOWN_CLOCK_TICKS):
                if self.tick == Config.COUNTDOWN_CLOCK_TICKS:
                    tickColor = Color.GREEN
                elif (i + 1) <= self.tick:
                    tickColor = Color.ORANGE
                else:
                    tickColor = Color.YELLOW

                pygame.draw.circle(surface, tickColor, (
                    self.x + self.tickPadding + i * (self.tickSize + self.tickPadding * 2) + self.tickSize // 2,
                    self.y + self.tickPadding + self.tickSize // 2
                ), self.tickSize // 2)

# The map selector widget
class MapSelector:
    # Create map selector widget
    def __init__(self, game, x, y, width, height, selectedMapIndex, changedCallback = None, callbackExtra = None):
        self.game = game
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.changedCallback = changedCallback
        self.callbackExtra = callbackExtra

        # List default maps
        self.mapPaths = [ os.path.abspath('assets/maps/' + filename) for filename in os.listdir('assets/maps/') if os.path.isfile('assets/maps/' + filename) ]

        # Add custom maps from settings
        customMapToRemove = []
        for customMapPath in game.settings['custom-maps']:
            customMapPath = os.path.abspath(customMapPath)
            if customMapPath not in self.mapPaths:
                if os.path.isfile(customMapPath):
                    self.mapPaths.append(customMapPath)
                else:
                    customMapToRemove.append(customMapPath)

        # Remove deleted or moved custom maps
        for customMapPath in customMapToRemove:
            del game.settings['custom-maps'][game.settings['custom-maps'].index(customMapPath)]
        game.save_settings()

        # Load maps
        self.maps = []
        for i, mapPath in enumerate(self.mapPaths):
            map = Map.load_from_file(mapPath)
            if map != None:
                self.maps.append(map)
            else:
                del self.mapPaths[i]

        # Set selected or selected a random one
        if selectedMapIndex != None:
            self.set_selected(selectedMapIndex)
        else:
            self.set_selected(random.randint(0, len(self.maps) - 1))

    # Create map selector widgets
    def create_widgets(self):
        self.widgets = []

        column_width = (self.width - 48 - 48) // 3
        rx = self.x + 48
        for i in range(3):
            position = (self.selectedMapIndex - 1) + i
            if position == -1:
                map = self.maps[len(self.maps) - 1]
            elif position == len(self.maps):
                map = self.maps[0]
            else:
                map = self.maps[position]

            if i == 0:
                self.widgets.append(Rect(self.game, rx, self.y, column_width, self.height, None, self.rotate_left_button_clicked))
            if i == 1:
                self.widgets.append(Rect(self.game, rx, self.y, column_width, self.height, Color.WHITE))
            if i == 2:
                self.widgets.append(Rect(self.game, rx, self.y, column_width, self.height, None, self.rotate_right_button_clicked))

            color = Color.BLACK if i == 1 else Color.WHITE

            minmap_size = self.game.width // 5
            ry = self.y + (self.height - (minmap_size + 32 + 32 + 24 + 24)) // 2
            self.widgets.append(MiniMap(self.game, map, None, rx + (column_width - minmap_size) / 2, ry, minmap_size, minmap_size))
            ry += minmap_size + 32
            self.widgets.append(Label(self.game, map.name, rx, ry, column_width, 32, self.game.textFont, color))
            ry += 32 + 24
            self.widgets.append(Label(self.game, 'Size: %dx%d' % (map.width, map.height), rx, ry, column_width, 24, self.game.smallFont, color))
            rx += column_width

        self.widgets.append(Button(self.game, '<', self.x, self.y, 48, self.height, self.game.titleFont, Color.BLACK, Color.WHITE, self.rotate_left_button_clicked))
        self.widgets.append(Button(self.game, '>', self.x + self.width - 48, self.y, 48, self.height, self.game.titleFont, Color.BLACK, Color.WHITE, self.rotate_right_button_clicked))

    # Set selected map
    def set_selected(self, selectedMapIndex):
        self.selectedMapIndex = selectedMapIndex
        self.selectedMap = self.maps[self.selectedMapIndex]
        self.create_widgets()

        # Call change callback
        if self.changedCallback != None:
            if self.callbackExtra != None:
                self.changedCallback(selectedMapIndex, self.callbackExtra)
            else:
                self.changedCallback(selectedMapIndex)

    # Load and add map file
    def load_map(self, file_path):
        file_path = os.path.abspath(file_path)

        # Check if map is not already pressent
        if file_path not in self.mapPaths:
            # Add and select it
            map = Map.load_from_file(file_path)
            if map != None:
                self.mapPaths.append(file_path)
                if file_path not in self.game.settings['custom-maps']:
                    self.game.settings['custom-maps'].append(file_path)
                    self.game.save_settings()
                self.maps.append(map)
                self.set_selected(len(self.maps) - 1)

        # Just selected the map
        else:
            self.set_selected(self.mapPaths.index(file_path))

    # Handle rotate left button click
    def rotate_left_button_clicked(self):
        if self.selectedMapIndex == 0:
            self.set_selected(len(self.maps) - 1)
        else:
            self.set_selected(self.selectedMapIndex - 1)

    # Handle rotate right button click
    def rotate_right_button_clicked(self):
        if self.selectedMapIndex == len(self.maps) - 1:
            self.set_selected(0)
        else:
            self.set_selected(self.selectedMapIndex + 1)

    # Handle map selector events
    def handle_event(self, event):
        # Send all events to the widgets
        for widget in reversed(self.widgets):
            if widget.handle_event(event):
                return True

        return False

    # Draw map selector
    def draw(self, surface):
        # Draw widgets
        for widget in self.widgets:
            widget.draw(surface)

# The vehicle selector widget class
class VehicleSelector:
    def __init__(self, game, x, y, width, height, color, selectedVehicleIndex, changedCallback = None, callbackExtra = None):
        self.game = game
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.changedCallback = changedCallback
        self.callbackExtra = callbackExtra

        # Create vehicle selector widget widgets
        self.widgets = []

        ry = y + (height - (128 + 32 + 48 + (32 + 16) * 3)) // 2
        self.vehicleImage = Image(None, x, ry, width, 128)
        self.widgets.append(self.vehicleImage)
        ry += 128 + 32
        self.nameLabel = Label(self.game, '', x, ry, width, 48, game.textFont, Color.WHITE)
        self.widgets.append(self.nameLabel)
        ry += 48 + 16
        self.maxForwardSpeed = Label(self.game, '', x, ry, width, 32, game.smallFont, Color.WHITE)
        self.widgets.append(self.maxForwardSpeed)
        ry += 32 + 16
        self.maxBackwardSpeed = Label(self.game, '', x, ry, width, 32, game.smallFont, Color.WHITE)
        self.widgets.append(self.maxBackwardSpeed)
        ry += 32 + 16
        self.turningSpeed = Label(self.game, '', x, ry, width, 32, game.smallFont, Color.WHITE)
        self.widgets.append(self.turningSpeed)

        self.widgets.append(Button(self.game, '<', x, y, 48, height, game.titleFont, Color.BLACK, Color.WHITE, self.rotate_left_button_clicked))
        self.widgets.append(Button(self.game, '>', x + width - 48, y, 48, height, game.titleFont, Color.BLACK, Color.WHITE, self.rotate_right_button_clicked))

        # Set selected or selected a random one
        if selectedVehicleIndex != None:
            self.set_selected(selectedVehicleIndex)
        else:
            self.set_selected(random.randint(0, len(vehicles) - 1))

    # Set selected vehicle
    def set_selected(self, selectedVehicleIndex):
        self.selectedVehicleIndex = selectedVehicleIndex
        self.selectedVehicle = vehicles[self.selectedVehicleIndex]
        self.update_widgets()

        # Call change callback
        if self.changedCallback != None:
            if self.callbackExtra != None:
                self.changedCallback(selectedVehicleIndex, self.callbackExtra)
            else:
                self.changedCallback(selectedVehicleIndex)

    # Update wigets
    def update_widgets(self):
        vehicleImageSurface = self.game.vehiclesImage.subsurface((
            self.selectedVehicle['colors'][self.color]['x'],
            self.selectedVehicle['colors'][self.color]['y'],
            self.selectedVehicle['width'],
            self.selectedVehicle['height']
        ))
        self.vehicleImage.set_image(vehicleImageSurface)

        self.nameLabel.set_text(self.selectedVehicle['name'])
        self.maxForwardSpeed.set_text('Max Forward Speed: %d km/h' % (self.selectedVehicle['maxForwardVelocity'] / Config.PIXELS_PER_METER * 3.6))
        self.maxBackwardSpeed.set_text('Max Backward Speed: %d km/h' % (self.selectedVehicle['maxBackwardVelocity'] / Config.PIXELS_PER_METER * 3.6))
        self.turningSpeed.set_text('Turing Speed: %d \u00B0/s' % math.degrees(self.selectedVehicle['turningSpeed']))

    # Handle rotate left button click
    def rotate_left_button_clicked(self):
        if self.selectedVehicleIndex == 0:
            self.set_selected(len(vehicles) - 1)
        else:
            self.set_selected(self.selectedVehicleIndex - 1)

    # Handle rotate right button click
    def rotate_right_button_clicked(self):
        if self.selectedVehicleIndex == len(vehicles) - 1:
            self.set_selected(0)
        else:
            self.set_selected(self.selectedVehicleIndex + 1)

    # Handle vehicle selector events
    def handle_event(self, event):
        # Send all events to the widgets
        for widget in reversed(self.widgets):
            if widget.handle_event(event):
                return True

        return False

    # Draw vehicle selector
    def draw(self, surface):
        # Draw widgets
        for widget in self.widgets:
            widget.draw(surface)

# The vehicle viewport widget class
class VehicleViewport:
    def __init__(self, game, vehicle, x, y, width, height, map, vehicles):
        self.game = game
        self.vehicle = vehicle
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.map = map
        self.vehicles = vehicles
        self.surface = pygame.Surface(( width, height ))
        self.camera = Camera(self.vehicle.x, self.vehicle.y, self.game.tilesImage, Config.TILE_SPRITE_SIZE, self.game.vehiclesImage)
        for vehicle in self.vehicles:
            vehicle.cropImage(self.camera)

        # Create vehicle viewport widgets
        self.widgets = []
        time = 0 if self.vehicle.startTime == None else self.game.time - self.vehicle.startTime
        self.timeLabel = Label(self.game, 'Time: ' + formatTime(time),
            24, height - 24 - 24 - (24 + 16) * 2, width - 24 - 24, 24, game.textFont, Color.BLACK, TextAlign.LEFT)
        self.widgets.append(self.timeLabel)
        self.lapLabel = Label(self.game, 'Lap: %d/%d' % (map.laps if vehicle.lap + 1 > map.laps else vehicle.lap + 1, self.map.laps), 24, height - 24 - 24 - (24 + 16), width - 24 - 24, 24, game.textFont, Color.BLACK, TextAlign.LEFT)
        self.widgets.append(self.lapLabel)
        self.speedLabel = Label(self.game, 'Speed: %3d km/h' % (vehicle.velocity / Config.PIXELS_PER_METER * 3.6), 24, height - 24 - 24, width - 24 - 24, 24, game.textFont, Color.BLACK, TextAlign.LEFT)
        self.widgets.append(self.speedLabel)

        # Check if the car is already started
        if not self.vehicle.started:
            tickSize = self.width // 8
            self.countdownClock = CountdownClock(self.game, (width - Config.COUNTDOWN_CLOCK_TICKS * tickSize) // 2, ((height - 256) - tickSize) // 2, Config.COUNTDOWN_CLOCK_TICKS * tickSize, tickSize)
            self.widgets.append(self.countdownClock)

        # Create finish label but hide it
        self.finishLabel = Label(self.game, 'Finished!', 0, 0, width, height - 128, game.titleFont, Color.BLACK, TextAlign.CENTER)

    # Handle vehicle viewport events
    def handle_event(self, event):
        # Handle keydown events
        if event.type == pygame.KEYDOWN:
            # Handle left player movement
            if self.vehicle.id == VehicleId.LEFT:
                if event.key == pygame.K_w:
                    self.vehicle.moving = Vehicle.MOVING_FORWARD
                if event.key == pygame.K_s:
                    self.vehicle.moving = Vehicle.MOVING_BACKWARD
                if event.key == pygame.K_a:
                    self.vehicle.turning = Vehicle.TURNING_LEFT
                if event.key == pygame.K_d:
                    self.vehicle.turning = Vehicle.TURNING_RIGHT

            # Handle right player movement
            if self.vehicle.id == VehicleId.RIGHT:
                if event.key == pygame.K_UP:
                    self.vehicle.moving = Vehicle.MOVING_FORWARD
                if event.key == pygame.K_DOWN:
                    self.vehicle.moving = Vehicle.MOVING_BACKWARD
                if event.key == pygame.K_LEFT:
                    self.vehicle.turning = Vehicle.TURNING_LEFT
                if event.key == pygame.K_RIGHT:
                    self.vehicle.turning = Vehicle.TURNING_RIGHT

         # Handle keyup events
        if event.type == pygame.KEYUP:
            # Handle left player movement
            if self.vehicle.id == VehicleId.LEFT:
                if event.key == pygame.K_w or event.key == pygame.K_s:
                    self.vehicle.moving = Vehicle.NOT_MOVING
                if event.key == pygame.K_a or event.key == pygame.K_d:
                    self.vehicle.turning = Vehicle.NOT_TURNING

            # Handle right player movement
            if self.vehicle.id == VehicleId.RIGHT:
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    self.vehicle.moving = Vehicle.NOT_MOVING
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    self.vehicle.turning = Vehicle.NOT_TURNING

        return False

    # Update the vehicle viewport
    def update(self, delta):
        # Update countdown clock if vehicle is not started
        if not self.vehicle.started:
            self.countdownClock.update(delta)

        # When vehicle is finished display finished lap
        if self.vehicle.finished:
            if self.finishLabel not in self.widgets:
                self.widgets.append(self.finishLabel)

    # Draw the vehicle viewport
    def draw(self, surface):
        # Clear the surface
        self.surface.fill(Color.DARK)

        # Update camera
        self.camera.x = self.vehicle.x
        self.camera.y = self.vehicle.y

        # Draw the map to surface
        self.map.draw(self.surface, self.camera)

        # Draw all the vehicles to surface
        for vehicle in self.vehicles:
            vehicle.draw(self.surface, self.camera)

        # Update time label
        if self.vehicle.finishTime != None and self.game.time - self.vehicle.finishTime < Config.FINISH_LAP_TIME_TIMEOUT:
            time = self.vehicle.lapTimes[self.vehicle.lap - 1]
        else:
            time = 0 if self.vehicle.startTime == None else self.game.time - self.vehicle.startTime
        self.timeLabel.set_text('Time: ' + formatTime(time))

        # Update lap label
        self.lapLabel.set_text('Lap: %d/%d' % (self.map.laps if self.vehicle.lap + 1 > self.map.laps else self.vehicle.lap + 1, self.map.laps))

        # Update speed label
        self.speedLabel.set_text('Speed: %d km/h' % (self.vehicle.velocity / Config.PIXELS_PER_METER * 3.6))

        # Draw widgets
        for widget in self.widgets:
            widget.draw(self.surface)

        # Draw own surface to the screen
        surface.blit(self.surface, ( self.x, self.y ))

# The map editor widget class
class MapEditor:
    GRASS_BRUSH = 0
    DIRT_BRUSH = 1
    SAND_BRUSH = 2
    ASPHALT_BRUSH = 3
    FINISH_BRUSH = 4
    CHECKPOINT_BRUSH = 5
    TRACK_ERASER = 6
    TOOL_LABELS =  [ 'Grass Brush', 'Dirt Brush', 'Sand Brush', 'Asphalt Brush', 'Finish Brush', 'Checkpoint Brush', 'Track Eraser' ]

    # Create map editor
    def __init__(self, game, map, x, y, width, height, tool, grid, camera = None):
        self.game = game
        self.map = map
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.tool = tool
        self.grid = grid
        self.center_camera(camera)
        self.mouseDown = False
        self.surface = pygame.Surface(( width, height ))

    # Center camera
    def center_camera(self, camera = None):
        self.camera = Camera(
            camera['x'] if camera != None and camera['x'] != None else (self.map.finish['x'] + self.map.finish['width'] // 2) * Config.EDITOR_TILE_SIZE + Config.EDITOR_TILE_SIZE / 2,
            camera['y'] if camera != None and camera['y'] != None else (self.map.finish['y'] + self.map.finish['height'] // 2) * Config.EDITOR_TILE_SIZE + Config.EDITOR_TILE_SIZE / 2,
            self.game.tilesImage, Config.EDITOR_TILE_SIZE, self.game.vehiclesImage, None, self.grid
        )

    # Use tool
    def use_tool(self, mouse):
        tile = {
            'x': math.floor((mouse['x'] + self.camera.x - self.width / 2) / Config.EDITOR_TILE_SIZE),
            'y': math.floor((mouse['y'] + self.camera.y - self.height / 2) / Config.EDITOR_TILE_SIZE)
        }

        if tile['x'] >= 0 and tile['y'] >= 0 and tile['x'] < self.map.width and tile['y'] < self.map.height:
            if self.tool == MapEditor.GRASS_BRUSH:
                self.map.terrain[tile['y']][tile['x']] = 0
                self.map.blend_terrain()

            if self.tool == MapEditor.DIRT_BRUSH:
                self.map.terrain[tile['y']][tile['x']] = 1
                self.map.blend_terrain()

            if self.tool == MapEditor.SAND_BRUSH:
                self.map.terrain[tile['y']][tile['x']] = 2
                self.map.blend_terrain()

            if self.tool == MapEditor.ASPHALT_BRUSH:
                self.map.track[tile['y']][tile['x']] = 1
                self.map.blend_track(False)

            if self.tool == MapEditor.FINISH_BRUSH:
                self.map.track[tile['y']][tile['x']] = 2
                self.map.blend_track(False)

            if self.tool == MapEditor.CHECKPOINT_BRUSH:
                self.map.track[tile['y']][tile['x']] = 3
                self.map.blend_track(False)

            if self.tool == MapEditor.TRACK_ERASER:
                self.map.track[tile['y']][tile['x']] = 0
                self.map.blend_track(False)

    # Handle page events
    def handle_event(self, event):
        # Handle mousedown events
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.mouseDown = True
            self.use_tool({ 'x': event.pos[0], 'y': event.pos[1] })
            return True

        # Handle mousemove events
        if event.type == pygame.MOUSEMOTION:
            mouse = {
                'x': event.pos[0],
                'y': event.pos[1]
            }

            if self.mouseDown:
                self.use_tool(mouse)
            else:
                self.camera.movingUp = mouse['y'] >= 2 and mouse['y'] < Config.EDITOR_CAMERA_BORDER
                self.camera.movingDown = mouse['y'] >= self.game.height - Config.EDITOR_CAMERA_BORDER and mouse['y'] < self.game.height - 2
                self.camera.movingLeft = mouse['x'] >= 2 and mouse['x'] < Config.EDITOR_CAMERA_BORDER
                self.camera.movingRight = mouse['x'] >= self.game.width - Config.EDITOR_CAMERA_BORDER and mouse['x'] < self.game.width - 2

            return True

        # Handle mouseup events
        if event.type == pygame.MOUSEBUTTONUP:
            self.mouseDown = False
            return True

        # Handle keydown events
        if event.type == pygame.KEYDOWN:
            # Handle camera movement
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                self.camera.movingUp = True
            if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                self.camera.movingDown = True
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                self.camera.movingLeft = True
            if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                self.camera.movingRight = True

        # Handle keyup events
        if event.type == pygame.KEYUP:
            # Handle camera movement
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                self.camera.movingUp = False
            if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                self.camera.movingDown = False
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                self.camera.movingLeft = False
            if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                self.camera.movingRight = False

        return False

    # Update map editor
    def update(self, delta):
        # Update camera
        self.camera.update(delta)

    # Draw map editor
    def draw(self, surface):
        # Draw background
        self.surface.fill(Color.DARK)

        # Draw the map
        self.map.draw(self.surface, self.camera)

        # Draw surface
        surface.blit(self.surface, ( self.x, self.y ))
