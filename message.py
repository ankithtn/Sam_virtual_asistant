import pywhatkit
import time
import pyautogui
pywhatkit.sendwhatmsg(phone_no='+919353982609', message='hey, this is automated message do not respond.', time_hour=20,
                      time_min=3,
                      wait_time=40)
time.sleep(40)  # waiting for the WhatsApp Web tab to open
pyautogui.press('enter')









