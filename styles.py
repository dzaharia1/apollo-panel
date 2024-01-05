import displayio

cwd = ("/"+__file__).rsplit('/', 1)[0]

def createIcon(iconPath):
    image_file = open(iconPath, "rb")
    icon = displayio.OnDiskBitmap(image_file)
    return displayio.TileGrid(icon, pixel_shader=getattr(icon, 'pixel_shader', displayio.ColorConverter()))

iconPaths = {
    "power": cwd + "icons/power.bmp",
    "cool": cwd + "icons/cool.bmp",
    "heat": cwd + "icons/warm.bmp",
    "manual": cwd + "icons/manual.bmp",
    "chevron_up": cwd + "icons/chevron_up.bmp",
    "chevron_down": cwd + "icons/chevron_down.bmp",
    "fan_0": cwd + "icons/fan_0.bmp",
    "fan_1": cwd + "icons/fan_1.bmp",
    "fan_2": cwd + "icons/fan_2.bmp",
    "fan_3": cwd + "icons/fan_3.bmp",
}

icons = {
    "power": createIcon(iconPaths["power"]),
    "cool": createIcon(iconPaths["cool"]),
    "heat": createIcon(iconPaths["heat"]),
    "manual": createIcon(iconPaths["manual"]),
    "chevron_up": createIcon(iconPaths["chevron_up"]),
    "chevron_down": createIcon(iconPaths["chevron_down"]),
    "fan_0": createIcon(iconPaths["fan_0"]),
    "fan_1": createIcon(iconPaths["fan_1"]),
    "fan_2": createIcon(iconPaths["fan_2"]),
    "fan_3": createIcon(iconPaths["fan_3"]),
}

colors = {
    "heat": 0xFF6928,
    "cool": 0x2898FF,
    "manual": 0xFFFFFF,
    "white": 0xFFFFFF,
    "black": 0x000000
}