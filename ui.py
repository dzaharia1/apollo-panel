import time
from adafruit_display_shapes.rect import Rect
from analogio import AnalogOut
import displayio
from displayio import ColorConverter, Display, Group
import board
import terminalio
import neopixel
from adafruit_display_text.label import Label
from adafruit_button import Button
from adafruit_bitmap_font import bitmap_font
from adafruit_display_shapes.roundrect import RoundRect
import adafruit_touchscreen
import styles

font = terminalio.FONT
display = board.DISPLAY
display.rotation = 180
screen_width = 320
screen_height = 240
status_light = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.2)
smallText = bitmap_font.load_font("fonts/futura-17.bdf")
largeText = bitmap_font.load_font("fonts/futura-32.bdf")

ts = adafruit_touchscreen.Touchscreen(
        board.TOUCH_YD,
        board.TOUCH_YU,
        board.TOUCH_XR,
        board.TOUCH_XL,
        calibration=((8938, 53100), (9065, 59629)),
        z_threshold=100,
        size=(screen_width, screen_height))

cwd = ("/"+__file__).rsplit('/', 1)[0]

def createImage(imagePath):
    image_file = open(imagePath, "rb")
    image = displayio.OnDiskBitmap(image_file)
    return displayio.TileGrid(image, pixel_shader=getattr(image, 'pixel_shader', displayio.ColorConverter()))

tempGraduationImage = createImage(cwd + "images/TemperatureGaugeGraduation.bmp")
humidityGraduationImage = createImage(cwd + "images/HumidityGaugeGraduation.bmp")
temperatureTicImage = createImage(cwd + "images/temperatureTic.bmp")
humidityTicImage = createImage(cwd + "images/humidityTic.bmp")

fanSpeed = 1
temperatureSetting = 70
fanToggle = 1
modeSetting = "manual"
screenEnabled = True

ui = Group(x=0, y=0)
temperatureGauge = Group(x=0, y=0)
humidityGauge = Group(x=254, y=0)
fanSpeedControls = Group(x=90, y=18)
modeControls = Group(x=185, y=38)
ui.append(temperatureGauge)
ui.append(humidityGauge)
ui.append(fanSpeedControls)
ui.append(modeControls)

# Connection indicator
connectionIndicator = Group(x=0, y = 0)
connectionLabel = Label(
    x = 12, y = 8,
    font=smallText,
    color=styles.colors["black"]
)
connectionLabel.text = "connecting..."
connectionIndicatorBackground = Rect(
    x = 0, y = 0,
    width=150, height = 21,
    fill=styles.colors["heat"]
)
connectionIndicator.append(connectionIndicatorBackground)
connectionIndicator.append(connectionLabel)

# build out temperature gauge
temperatureTic = Group(x=0, y=116)
temperatureTic.append(temperatureTicImage)
temperatureGraduation = Group(x=17, y=0)
temperatureGraduation.append(tempGraduationImage)
temperatureScale = Group(x=44, y=0)
temperatureScaleItems = []

# startingCoordinate = 0
startingNumber = temperatureSetting + 5
for i in range(0, 11):
    thisItemNumber = startingNumber - i
    temperatureScaleItems.append(Label(font=smallText,
        color=0x6B6B6B,
        x=0,
        y=(i * 24),
        line_spacing=0))
    if thisItemNumber == temperatureSetting:
        temperatureScaleItems[i].color = styles.colors["white"]
    temperatureScaleItems[i].text = str(thisItemNumber)
    temperatureScale.append(temperatureScaleItems[i])
temperatureGauge.append(temperatureTic)
temperatureGauge.append(temperatureGraduation)
temperatureGauge.append(temperatureScale)

# build out humidity gauge
humidityTic = Group(x=54, y=116)
humidityTic.append(humidityTicImage)
humidityGraduation = Group(x=27, y=0)
humidityGraduation.append(humidityGraduationImage)
humidityScale = Group(x=0, y=0)
humidityScaleItems = []

startingNumber = 65
for i in range(0, 11):
    thisItem = startingNumber - (i * 5)
    humidityScaleItems.append(Label(font=smallText,
        color=0x6B6B6B,
        x=0,
        y=(i * 24),
        line_spacing=0))
    if thisItem == 40:
        humidityScaleItems[i].color = styles.colors["white"]
    humidityScaleItems[i].text = str(thisItem)
    humidityScale.append(humidityScaleItems[i])
humidityGauge.append(humidityTic)
humidityGauge.append(humidityGraduation)
humidityGauge.append(humidityScale)

# build out fan speed buttons
speedButtonWidth = 64
speedButtonHeight = 45
fanButtons = []
fanButtonTargets = []
fanButtonBackgrounds = []
fanButtonLabels = []
for i in range(4):
    fanButtons.append(Group(x=0, y=i * 53))
    fanSpeedControls.append(fanButtons[i])
    fanButtonBackgrounds.append(RoundRect(x=0,
        y=0,
        width=64,
        height=45,
        r=4,
        fill=0x000000))
    fanButtonTargets.append(Button(x=0,
        y=0,
        width=64,
        height=45,
        fill_color=None,
        outline_color=None))
    fanButtonLabels.append(Label(font=largeText,
        color=styles.colors["white"],
        x=2,
        y=23,
        line_spacing=0))
    fanButtons[i].append(fanButtonBackgrounds[i])
    fanButtons[i].append(fanButtonLabels[i])
    fanButtons[i].append(fanButtonTargets[i])

fanButtonBackgrounds[fanSpeed].fill = styles.colors["white"]
fanButtonLabels[fanSpeed].color = 0x000000
fanButtonLabels[0].text = "OFF"
fanButtonLabels[0].x = 2
fanButtonLabels[1].text = "LO"
fanButtonLabels[1].x = 12
fanButtonLabels[2].text = "MD"
fanButtonLabels[2].x = 4
fanButtonLabels[3].text = "HI"
fanButtonLabels[3].x = 16

# build out mode buttons
modeButtons = []
modeButtonTargets = []
modeButtonBackgrounds = []
modeButtonLabels = []
for i in range(3):
    modeButtons.append(Group(x=0, y=i * 62))
    modeControls.append(modeButtons[i])
    modeButtonBackgrounds.append(RoundRect(
        x=0,
        y=0,
        width=50,
        height=45,
        r=4,
        fill=0x000000))
    modeButtonTargets.append(Button(
        x=0,
        y=0,
        width=50,
        height=45,
        fill_color=None,
        outline_color=None))
    modeButtonLabels.append(Label(font=largeText,
        color=styles.colors["white"],
        x=2,
        y=23,
        line_spacing=0))
    modeButtons[i].append(modeButtonBackgrounds[i])
    modeButtons[i].append(modeButtonLabels[i])
    modeButtons[i].append(modeButtonTargets[i])

def getModeIndex(mode):
    if mode == "manual":
        return 0
    elif mode == "heat":
        return 1
    elif mode == "cool":
        return 2

modeButtonBackgrounds[getModeIndex(modeSetting)].fill = styles.colors["white"]
modeButtonLabels[getModeIndex(modeSetting)].color = 0x000000
modeButtonLabels[0].text = "M"
modeButtonLabels[0].x = 10
modeButtonLabels[1].text = "H"
modeButtonLabels[1].x = 13
modeButtonLabels[2].text = "C"
modeButtonLabels[2].x = 12

# button so that user can brighten screen to check stats
screenActivateButton = Button(
    x=50,
    y=100,
    width=screen_width - (100),
    height=screen_height - (200),
    fill_color=None,
    outline_color=None,
    style=Button.RECT
)
ui.append(screenActivateButton)
display.show(ui)

def updateMode(newMode):
    global modeSetting
    modeSetting = newMode
    for i in range(3):
        modeButtonBackgrounds[i].fill = 0x000000
        modeButtonLabels[i].color = styles.colors["white"]

    modeButtonBackgrounds[getModeIndex(modeSetting)].fill = styles.colors["white"]
    modeButtonLabels[getModeIndex(modeSetting)].color = 0x000000

def updateTemperatureSetting(newTemperature):
    global temperatureSetting
    temperatureSetting = newTemperature
    startingTemperature = temperatureSetting + 5
    for i in range(len(temperatureScaleItems)):
        thisItemNumber = startingTemperature - i
        temperatureScaleItems[i].text = str(thisItemNumber)

def updateFanSpeedSetting(newSpeed):
    global fanSpeed
    fanSpeed = newSpeed
    for i in range(len(fanButtons)):
        fanButtonBackgrounds[i].fill = 0x000000
        fanButtonLabels[i].color = styles.colors["white"]
    fanButtonBackgrounds[fanSpeed].fill = styles.colors["white"]
    fanButtonLabels[fanSpeed].color = 0x000000
    
def updateTemperature(newTemperature):
    minY = 0
    maxY = 232
    minTemp = temperatureSetting - 5
    maxTemp = temperatureSetting + 5
    
    if newTemperature < minTemp:
        temperatureTic.y = maxY
    elif newTemperature > maxTemp:
        temperatureTic.y = minY
    else:
        temperatureTic.y = maxY - int((newTemperature - minTemp) * (maxY / 10))

def updateHumidity(newHumidity):
    minY = 0
    maxY = 232
    minHumidity = 15
    maxHumidity = 65

    if newHumidity < minHumidity:
        humidityTic.y = maxY
    elif newHumidity > maxHumidity:
        humidityTic.y = minY
    else:
        humidityTic.y = maxY - int((newHumidity - minHumidity)/50 * maxY)

def toggleFan(value):
    global fanToggle
    fanToggle = value
    if fanToggle == 1:
        if modeSetting == "heat":
            fanButtonBackgrounds[fanSpeed].fill = styles.colors["heat"]
        if modeSetting == "cool":
            fanButtonBackgrounds[fanSpeed].fill = styles.colors["cool"]
    else:
        fanButtonBackgrounds[fanSpeed].fill = styles.colors["white"]

def refresh_status_light():
    if fanToggle and screenEnabled and fanSpeed != "0":
        status_light.brightness = 1
    elif fanToggle and not screenEnabled and fanSpeed != "0":
        status_light.brightness = .15
    elif not fanToggle or fanSpeed == "0":
        status_light.brightness = 0

    status_light.show()

def set_backlight(val):
    display.brightness = val

def disableScreen(force=False):
    global screenEnabled
    if screenEnabled or force:
        screenEnabled = False
        set_backlight(.35)

def enableScreen():
    global screenEnabled
    screenEnabled = True
    set_backlight(1)
