import board
import time
import terminalio
import busio
import adafruit_htu31d
from analogio import AnalogIn
font = terminalio.FONT
from math import floor
import ui
import feeds
from feeds import mqtt_client
from adafruit_seesaw.seesaw import Seesaw
from adafruit_seesaw.digitalio import DigitalIO
import digitalio
from adafruit_seesaw.pwmout import PWMOut

i2c_bus = busio.I2C(board.SCL, board.SDA)
temp_probe = adafruit_htu31d.HTU31D(i2c_bus)
temp_probe.heater = False
lightSensor = AnalogIn(board.LIGHT)

# set up the switches
leftButtonBoard = Seesaw(i2c_bus, 0x3A)
rightButtonBoard = Seesaw(i2c_bus, 0x3B)
buttonBoards = (leftButtonBoard, rightButtonBoard)
buttonPins = (18, 19, 20, 2)
buttons = []
for buttonBoard in buttonBoards:
    for buttonPin in buttonPins:
        button = DigitalIO(buttonBoard, buttonPin)
        button.direction = digitalio.Direction.INPUT
        button.pull = digitalio.Pull.UP
        buttons.append(button)

lastButtonPush = 0.0

# def checkTouchScreen():
#     global lastButtonPush
#     point = ui.ts.touch_point

#     # touch detected
#     if point and point[-1] > 30000:
#         if ui.screenActivateButton.contains(point):
#             ui.enableScreen()
#             lastButtonPush = time.monotonic()

#     if point and ui.screenEnabled:
#         # check mode buttons
#         i = 0
#         for button in ui.modeButtonTargets:
#             if button.contains(point):
#                 lastButtonPush = time.monotonic()
#                 if i == 0:
#                     ui.updateMode("manual")
#                     ui.toggleFan(1)
#                     feeds.publish(feeds.modeSettingFeedCommand, "off")
#                     feeds.publish(feeds.fanSpeedFeed, ui.fanSpeed)
#                     feeds.publish(feeds.fanToggleFeed, ui.fanToggle)
#                 elif i == 1:
#                     ui.updateMode("heat")
#                     feeds.publish(feeds.modeSettingFeedCommand, "heat")
#                 elif i == 2:
#                     ui.updateMode("cool")
#                     feeds.publish(feeds.modeSettingFeedCommand, "cool")
#             i = i + 1
        
#         i = 0
#         # check fan buttons
#         for i, button in enumerate(ui.fanButtonTargets):
#             if button.contains(point):
#                 lastButtonPush = time.monotonic()
#                 if ui.modeSetting == "manual":
#                     ui.toggleFan(1)
#                     feeds.publish(feeds.fanToggleFeed, 1)

#                 if i == 0:
#                     feeds.publish(feeds.fanSpeedCommand, "0")
#                     ui.updateFanSpeed(0)
#                     ui.set_backlight(1)
#                 else:
#                     newFanSpeed = 4 - i
#                     feeds.publish(feeds.fanSpeedCommand, str(newFanSpeed))
#                     ui.updateFanSpeed(newFanSpeed)
#                     ui.set_backlight(1)
#             i = i + 1

#         time.sleep(.075)

def checkButtons():
    global lastButtonPush
    i = 0
    for button in buttons:
        if not button.value:
            ui.enableScreen()
            lastButtonPush = time.monotonic()
            if i == 0:
                ui.updateTemperatureSetting(ui.temperatureSetting - 1)
                feeds.publish(feeds.temperatureSettingFeedCommand, ui.temperatureSetting)
                checkTemperature()
            elif i == 1:
                ui.updateTemperatureSetting(ui.temperatureSetting + 1)
                feeds.publish(feeds.temperatureSettingFeedCommand, ui.temperatureSetting)
                checkTemperature()
            else:
                feeds.publish(feeds.commanderFeed, i - 1)
        i = i + 1
            

def checkTemperature():
    print("Check readings")
    currTemp = round(temp_probe.temperature * (9 / 5) + 32 - 4, 1)
    currHumidity = round(temp_probe.relative_humidity, 1)
    # ui.currTempLabel.text = str(floor(currTemp)) + "F\n" + str(floor(currHumidity)) + "%"
    ui.updateTemperature(currTemp)
    ui.updateHumidity(currHumidity)
    feeds.publish(feeds.temperatureSensorFeed, currTemp)
    feeds.publish(feeds.humidityFeed, currHumidity)

    if ui.modeSetting == "heat":
        if (currTemp <= ui.temperatureSetting):
            ui.toggleFan(1)
            feeds.publish(feeds.fanToggleFeed, ui.fanToggle)
        else:
            ui.toggleFan(0)
            feeds.publish(feeds.fanToggleFeed, ui.fanToggle)
    elif ui.modeSetting == "cool":
        if (currTemp >= ui.temperatureSetting):
            ui.toggleFan(1)
            feeds.publish(feeds.fanToggleFeed, ui.fanToggle)
        else:
            ui.toggleFan(0)
            feeds.publish(feeds.fanToggleFeed, ui.fanToggle)
    ui.refresh_status_light()

def mqtt_message(client, feed_id, payload):
    print('Got {0} from {1}'.format(payload, feed_id))

    if feed_id == feeds.temperatureSettingFeed:
        print("got new temperature setting")
        ui.updateTemperatureSetting(floor(float(payload)))
        ui.updateTemperatureSetting()
        checkTemperature()
    if feed_id == feeds.fanSpeedCommand:
        print("got new fan speed setting")
        ui.updateFanSpeedSetting(int(payload))
        feeds.publish(feeds.fanSpeedFeed, ui.fanSpeed)
    if feed_id == feeds.modeSettingFeed:
        print("got new mode setting")
        if payload == "heat" or payload == "cool" or payload == "manual":
            ui.updateMode(payload)
        if payload == "manual":
            ui.toggleFan(1)
            feeds.publish(feeds.fanToggleFeed, ui.fanToggle)
        elif payload == "off":
            ui.updateMode("manual")
            ui.toggleFan(0)
            feeds.publish(feeds.fanToggleFeed, ui.fanToggle)
        checkTemperature()
            

mqtt_client.on_message = mqtt_message

checkTemperature()
# ui.updateMode("heat")
prev_refresh_time = 0.0
while True:
    # print("Main loop")
    # checkTouchScreen()
    checkButtons()
    if (time.monotonic() - lastButtonPush) > 15 :
        ui.disableScreen()
    if (time.monotonic() - prev_refresh_time) > 40:
        checkTemperature()
        prev_refresh_time = time.monotonic()
    feeds.loop()