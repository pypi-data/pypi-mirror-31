# ScreenAmbience
The ***ScreenAmbience*** package provides helpful modules and methods for calculating the _average_ color of the screen and sending the color to your LIFX-Z Strip.

Intended for use with LIFX Lights.

**Note** This is NOT an API for LIFX LAN communication. For that, check out the extensive [lifxlan](https://github.com/mclarkk/lifxlan) package



## References:
---
[LIFX forums for packet building](https://community.lifx.com/t/building-a-lifx-packet/59/3)

[colorsys package for pixel color data and conversions](https://docs.python.org/2/library/colorsys.html)

## Installation
```python
pip install ScreenAmbience
```

## How to use:

Create a ScreenRegion object by providing starting and ending x_coordinates, starting and ending y-coordinates, and an image resize ratio (can be default screen resolution but resizing speeds up pixel color processing). Optionally, set values for kelvin, jump, and brightness_multiplier.

```python
"""
Attributes:
        start_x: starting x coordinate
        end_x: ending x coordinate
        start_y: staring y coordinate
        end_y: ending y coordinate
        kelvin: the warmth-coolness of the color (2500-9000)
        jump: the interval of pixels to process (1: every pixel on the screen is processed)
        brightness_multiplier: (0.0-1.0: I've noticed 1.0 is too bright at times, 0.5 seems to give a nice balance)
"""
# This will process all pixels in the image once resized to 128x72
# Ending coordinates shouldn't exceed width or height of resized dimensions
screen_region = ScreenRegion(0, 128, 0, 72, (128, 72))
# Say you want this object to only process pixels (start_x, start_y) -> (end_x, end_y)
screen_region = ScreenRegion(start_x, end_x, start_y, end_y, (128, 72))
```

After obtaining the HSBKD value, create a LightStrip object from the strip module and send the color to your light. A LightStrip object is initialized with a mac_address string and the number of LED zones in the strip.

```python
screen_region = ScreenRegion(0, 128, 0, 72, (128, 72))
# Get the average color of the screen, returns an HSBKD tuple
# (Hue, Saturation, Brightness, Kelvin)
average_color = screen_region.get_average_color()

light = LightStrip('MA:CA:DD:RE:SS', 10)
# Pass in the color, duration, and the zone range for which you want to set the color.
light.set_light_color(average_color, 200, 0, 10)
```

That's it! So long as your light is on, it should update with the average color of the entire screen for zones 0-10

## Example:

Now for the fun bit. With the above, we can now split the screen up into vertical regions. Say we want to split it down the middle and set the first 5 LED zones to match the average color on the left, and the next five the average color on right of the screen:

```python
light = LightStrip("MA:CA:DD:RE:SS", 10)

left_region = ScreenRegion(0, 63, 0, 72, (128, 72))
right_region = ScreenRegion(64, 128, 0, 72, (128, 72))
duration = 200
light.set_light_color(left_region.get_average_color(), duration, 0, 3)
light.set_light_color(left_region.get_average_color(), duration, 4, 9)
```

## Example (Match individual zones):

This script should divide the screen into N regions, where N is the number of LED zones in your LIFX-Z strip, and set the color of each zone while the script runs.

MAKE SURE YOUR LIGHT IS ON BEFORE RUNNING

```python

from ScreenAmbience.colors import ScreenRegion
from ScreenAmbience.strip import LightStrip
from ScreenAmbience.ratios import get_transformed_ratio

def get_color_regions(zones, screen_width, screen_height):
    width = screen_width / zones
    screen_spaces = []
    for zone in range(zones):
        screen_region = ScreenRegion(
            zone*width, (zone+1)*width, 0, screen_height, (screen_width, screen_height))
        screen_spaces.append(screen_region)
    return screen_spaces

def stream_lights(screen_width, screen_height, light):
    color_regions = get_color_regions(light.zones, screen_width, screen_height)
    duration = 200
    while True:
        for i, region in enumerate(color_regions):
            light.set_light_color(region.get_average_color(), duration, i, i)

mac = '1234567890'
light = LightStrip(mac, 10)
stream_lights(*get_transformed_ratio(), light)
```