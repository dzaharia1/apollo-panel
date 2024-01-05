import time
from analogio import AnalogOut
from displayio import Group
import styles
import board
import terminalio
import neopixel
from adafruit_display_text.label import Label
from adafruit_button import Button
from adafruit_bitmap_font import bitmap_font
import adafruit_touchscreen

font = terminalio.FONT
display = board.DISPLAY
display.rotation = 180
screen_width = 240
screen_height = 320
status_light = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.2)
smallText = bitmap_font.load_font("fonts/roboto-mono-32.bdf")
largeText = bitmap_font.load_font("fonts/roboto-mono-90.bdf")

ts = adafruit_touchscreen.Touchscreen(
        board.TOUCH_YD,
        board.TOUCH_YU,
        board.TOUCH_XR,
        board.TOUCH_XL,
        calibration=((8938, 53100), (9065, 59629)),
        z_threshold=100,
        size=(screen_width, screen_height))

fanSpeed = 1
temperatureSetting = 70
fanToggle = 1
modeSetting = "manual"
screenEnabled = True

ui = Group(x=0, y=0)
topBarDiv = Group(x=10, y=10)
temperatureDiv = Group(x=0, y=65)
fanSelectorDiv = Group(x=10, y=262)
ui.append(temperatureDiv)
ui.append(fanSelectorDiv)
ui.append(topBarDiv)

# build out top bar
currTempLabel = Label(font=smallText, color=styles.colors["white"], x=5, y=20, line_spacing=.75)
warmIcon = Group(x=84, y=0)
warmIcon.append(styles.icons['heat'])
coolIcon = Group(x=84, y=0)
coolIcon.append(styles.icons["cool"])
manualIcon = Group(x=84, y=0)
manualIcon.append(styles.icons["manual"])
topBarDiv.append(currTempLabel)
topBarDiv.append(warmIcon)
topBarDiv.append(coolIcon)
topBarDiv.append(manualIcon)

# build out temperatureDiv
increaseIcon = Group(x=92, y=0)
increaseIcon.append(styles.icons["chevron_up"])
decreaseIcon = Group(x=92, y=135)
decreaseIcon.append(styles.icons["chevron_down"])
temperatureSettingLabel = Label(font=largeText, color=styles.colors["white"], x=68, y=90, text=str(temperatureSetting))
temperatureDiv.append(increaseIcon)
temperatureDiv.append(decreaseIcon)
temperatureDiv.append(temperatureSettingLabel)

# build out bottom bar
fanSelectorDiv.append(styles.icons["fan_0"])

display.show(ui)

def updateMode(newMode):
    global modeSetting
    modeSetting = newMode
    temperatureSettingLabel.color = styles.colors[newMode]

    if modeSetting == "heat":
        status_light.fill((245, 83, 2))
        warmIcon.hidden = False
        coolIcon.hidden = True
        manualIcon.hidden = True
        temperatureDiv.hidden = False
    elif modeSetting == "cool":
        status_light.fill((20, 110, 227))
        warmIcon.hidden = True
        coolIcon.hidden = False
        manualIcon.hidden = True
        temperatureDiv.hidden = False
    elif modeSetting == "manual":
        status_light.fill((255, 255, 255))
        warmIcon.hidden = True
        coolIcon.hidden = True
        manualIcon.hidden = False
        temperatureDiv.hidden = True
        refresh_status_light()

def updateTemperature(newTemperature):
    global temperatureSetting
    global temperatureSettingLabel
    temperatureSetting = newTemperature
    temperatureSettingLabel.text = str(temperatureSetting)

def updateFanSpeed(newSpeed):
    global fanSpeed
    global fanSelectorDiv
    fanSpeed = newSpeed
    while True:
        try:
            fanSelectorDiv.pop()
        except:
            break
    fanSelectorDiv.append(styles.icons["fan_" + fanSpeed])

modeButtons = []
temperatureButtons = []
fanButtons = []

manualButton = Button(
    x = topBarDiv.x + warmIcon.x,
    y = 10,
    width = 40,
    height = 40,
    fill_color = None,
    outline_color = None,
    style = Button.RECT,    
)
ui.append(manualButton)
modeButtons.append(manualButton)

warmButton = Button(
    x = topBarDiv.x + warmIcon.x + 48,
    y = 10,
    width = 40,
    height = 40,
    fill_color = None,
    outline_color = None,
    style = Button.RECT,
)
ui.append(warmButton)
modeButtons.append(warmButton)

coolButton = Button(
    x = topBarDiv.x + warmIcon.x + 96,
    y = 10,
    width = 40,
    height = 40,
    fill_color = None,
    outline_color = None,
    style = Button.RECT,    
)
ui.append(coolButton)
modeButtons.append(coolButton)

raiseTemperatureButton = Button(
    x = 92,
    y = 70,
    width = 50,
    height = 50,
    fill_color = None,
    outline_color = None,
    style = Button.RECT,    
)
ui.append(raiseTemperatureButton)
temperatureButtons.append(raiseTemperatureButton)

lowerTemperatureButton = Button(
    x = 92,
    y = 200,
    width = 50,
    height = 50,
    fill_color = None,
    outline_color = None,
    style = Button.RECT
)
ui.append(lowerTemperatureButton)
temperatureButtons.append(lowerTemperatureButton)

fanOffButton = Button(
    x = fanSelectorDiv.x,
    y = fanSelectorDiv.y,
    width = 48,
    height = 48,
    fill_color = None,
    outline_color = None,
    style = Button.RECT
)
ui.append(fanOffButton)
fanButtons.append(fanOffButton)

fanHighButton = Button(
    x = fanSelectorDiv.x + 66,
    y = fanSelectorDiv.y,
    width = 48,
    height = 48,
    fill_color = None,
    outline_color = None,
    style = Button.RECT
)
ui.append(fanHighButton)
fanButtons.append(fanHighButton)

fanMediumButton = Button(
    x = fanSelectorDiv.x + 132,
    y = fanSelectorDiv.y + 5,
    width = 38,
    height = 38,
    fill_color = None,
    outline_color = None,
    style = Button.RECT
)
ui.append(fanMediumButton)
fanButtons.append(fanMediumButton)

fanLowButton = Button(
    x = fanSelectorDiv.x + 188,
    y = fanSelectorDiv.y + 8,
    width = 32,
    height = 32,
    fill_color = None,
    outline_color = None,
    style = Button.RECT
)
ui.append(fanLowButton)
fanButtons.append(fanLowButton)

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

def checkTarget(button, touch):
    touchX = touch[0]
    touchY = touch[1]
    buttonX1 = button.x
    buttonY1 = button.y
    buttonX2 = buttonX1 + button.width
    buttonY2 = buttonY1 + button.height

    if touchX >= buttonX1 and touchX <= buttonX2 and touchY >= buttonY1 and touchY <= buttonY2:
        return True
    else:
        return False

def refresh_status_light():
    if fanToggle and screenEnabled and fanSpeed != "0":
        status_light.brightness = 1
    elif fanToggle and not screenEnabled and fanSpeed != "0":
        status_light.brightness = .15
    elif not fanToggle or fanSpeed == "0":
        status_light.brightness = 0

    status_light.show()

# set backlight with a value between 0 and 1
def set_backlight(val):
    display.brightness = val
    refresh_status_light()

def disableScreen(force=False):
    global screenEnabled
    if screenEnabled or force:
        screenEnabled = False
        set_backlight(.05)
        temperatureDiv.hidden = True
        fanSelectorDiv.hidden = True
        warmIcon.hidden = True
        coolIcon.hidden = True
        manualIcon.hidden = True
        currTempLabel.font = largeText
        currTempLabel.y = 60

def enableScreen():
    global screenEnabled
    # if not screenEnabled:
    screenEnabled = True
    set_backlight(1)
    currTempLabel.font = smallText
    currTempLabel.y = 20
    fanSelectorDiv.hidden = False
    if modeSetting == "heat":
        warmIcon.hidden = False
        temperatureDiv.hidden = False
    elif modeSetting == "cool":
        coolIcon.hidden = False
        temperatureDiv.hidden = False
    if modeSetting == "manual":
        manualIcon.hidden = False