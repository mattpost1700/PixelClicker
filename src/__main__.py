import time
from datetime import datetime

import pyautogui
import pygetwindow as gw
import requests
from PIL import ImageGrab
from plyer import notification

from . import *

LAST_GLOBAL_MSG = datetime(year=1970, month=1, day=1)

def _rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def log(msg: str, discord=False, notify=False):
    print(f"log: ({datetime.now()}) {msg}")

    global LAST_GLOBAL_MSG

    now = datetime.now()
    diff = now - LAST_GLOBAL_MSG
    if diff > TIME_BETWEEN_GLOBAL_MESSAGE:
        if PIXEL_CLICKER_DISCORD_WEBHOOK and discord:
            try:
                resp_code = requests.post(PIXEL_CLICKER_DISCORD_WEBHOOK, json={"content": msg}).status_code
                if resp_code // 100 != 2:
                    print(f"log: Unable to publish message to discord!! {resp_code} code")
            except:
                print("log: Unable to publish message to discord!! No internet!")
            LAST_GLOBAL_MSG = now

        if notify:
            notification.notify(
                title="Matt Post's MPS day / night switcher", message=msg, timeout=5
            )
            LAST_GLOBAL_MSG = now
    else:
        print(f"({datetime.now()}) log: Did not push global message because it has only been {diff}")


def get_pixel_colors(region):
    """Capture a region of the screen and return the pixel colors."""
    screenshot = ImageGrab.grab(bbox=region)  # Left, Top, Right, Bottom
    # screenshot.save("tmp.png")
    return [_rgb_to_hex(rgb) for rgb in screenshot.getdata()][0]


def is_in_dark_mode():
    background = get_pixel_colors(MPS_DAY_NIGHT_BACKGROUND_BB)
    log(f"is_in_dark_mode: {background=} {MPS_DAY_NIGHT_BUTTON_NIGHT_HEX=}")

    return get_pixel_colors(MPS_DAY_NIGHT_BACKGROUND_BB) == MPS_DAY_NIGHT_BUTTON_NIGHT_HEX


def is_night_time():
    hour = datetime.now().hour
    log(f"is_night_time: {hour=} {(hour < 8 or hour > 20)=}")
    return hour < 8 or hour > 20


def mps_is_open():
    active_window = gw.getActiveWindow()

    if active_window:
        if is_mps := "mps" in active_window.title.lower():
            log("mps_is_open: MPS is running!")
 
        else:
            log(f"mps_is_open: MPS not detected! {active_window.title} is running", discord=True, notify=True)
        return is_mps

    # No window open
    log(f"mps_is_open: No window is open!!", discord=True, notify=True)
    return False


def should_toggle():
    if not mps_is_open():
        return False

    is_night = is_night_time()
    is_dark_mode = is_in_dark_mode()
    ret_val = (is_night and not is_dark_mode) or (not is_night and is_dark_mode)

    log(f"should_toggle: {is_night=} {is_dark_mode=} {ret_val=}")

    return ret_val


def toggle_day_night():
    # TODO: Check buton is there
    pyautogui.click(*MPS_DAY_NIGHT_BUTTON_COORD)


def main(refresh_seconds: int = 5):
    while True:
        if should_toggle():
            toggle_day_night()
            time.sleep(5)  # in case there is GUI lag
            log(f"GUI toggled! GUI dark mode is now {is_in_dark_mode()}", discord=True)

        time.sleep(refresh_seconds)


if __name__ == "__main__":
    main()
