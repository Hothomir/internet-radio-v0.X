import time
import subprocess
import digitalio
import board
import miniaudio
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7789

def title_printer(client: miniaudio.IceCastClient, new_title: str) -> None:
    print("Stream title: ", new_title)

def stream_access():
    with miniaudio.IceCastClient("https://stream.skylab-radio.com/live", update_stream_title=title_printer) as source:
        print("Connected to internet stream, audio format:", source.audio_format.name)
        station_name = "Station name: " + source.station_name
        print("Press <enter> to quit playing.\n")
        stream = miniaudio.stream_any(source, source.audio_format)
        
    with miniaudio.PlaybackDevice() as device:
        device.start(stream)
        input()   # wait for user input, stream plays in background

# Configuration for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 64000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# Create the ST7789 display:
disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    width=135,
    height=240,
    x_offset=53,
    y_offset=40,
)

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
height = disp.width  # we swap height/width to rotate it to landscape!
width = disp.height
image = Image.new("RGB", (width, height))
rotation = 90

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image, rotation)
# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

while True:
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    # Write four lines of text.
    y = top
    draw.text((x, y), stream_access.station_name, font=font, fill="#FFFFFF")
    y += font.getsize(stream_access.station_name)[1]
    draw.text((x, y), stream_access.new_title, font=font, fill="#FFFFFF")

    # Display image.
    disp.image(image, rotation)
    time.sleep(0.1)
