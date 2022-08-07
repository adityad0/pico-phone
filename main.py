"""
ssd1306 library
https://github.com/micropython/micropython/blob/master/drivers/display/ssd1306.py
JASchilz/uQR:
https://github.com/JASchilz/uQR
"""
from machine import I2C, Pin, UART
from time import sleep
from ssd1306 import SSD1306_I2C
from uQR import QRCode
import utime
import _thread

uart1 = UART(1, 9600)

sLock = _thread.allocate_lock()

LED_INBUILT = Pin(25, Pin.OUT)
LED_RGB_R = Pin(22, Pin.OUT)
LED_RGB_G = Pin(21, Pin.OUT)
LED_RGB_B = Pin(20, Pin.OUT)

command = ""

i2c0 = I2C(0, sda = Pin(0), scl = Pin(1), freq = 40000)
def get_i2c_devices(i2c0 = i2c0):
    print(i2c0)
    print("Available i2c devices: " + str(i2c0.scan()))

WIDTH = 128
HEIGHT = 64

oled = SSD1306_I2C(WIDTH, HEIGHT, i2c0)

oled.fill(0)

# Initializing the keypad
matrix_keys = [
    ['1', '2', '3'],
    ['4', '5', '6'],
    ['7', '8', '9'],
    ['*', '0', '#']
]
keypad_rows = [17, 16, 15, 14]
keypad_columns = [10, 11, 12, 13]
col_pins = []
row_pins = []
for x in range(0,4):
    row_pins.append(Pin(keypad_rows[x], Pin.OUT))
    row_pins[x].value(1)
for x in range(0, 4):
    col_pins.append(Pin(keypad_columns[x], Pin.IN, Pin.PULL_DOWN))
    col_pins[x].value(0)


oled.text("Initialized!", 0, 0)
oled.show()

sleep(1)
qr = QRCode()

# qr.add_data("uQR example")
# matrix = qr.get_matrix()
# print("version:", qr.version)
# print("len of matrix", len(matrix))

# oled.fill(1)
# for y in range(len(matrix)*2):                   # Scaling the bitmap by 2
#     for x in range(len(matrix[0])*2):            # because my screen is tiny.
#         value = not matrix[int(y/2)][int(x/2)]   # Inverting the values because
#         oled.pixel(x, y, value)                  # black is `True` in the matrix.
# oled.show()

upi_pa = "adityadesaig@apl"
upi_pn = "Aditya Desai"
upi_cu = "INR"
upi_url = f"upi://pay?pa={upi_pa}&pn={upi_pn}&cu=INR&am="
upi_amt = ""

command = ""

def sendCMD_waitResp(cmd, uart = uart1, timeout = 2000):
    uart.write(cmd)
    resp = waitResp(uart, timeout)
    resp = resp[-1].decode().replace('\r', '').split('\n')
    return resp
    
def waitResp(uart = uart1, timeout = 2000):
    prvMills = utime.ticks_ms()
    resp = b""
    while(utime.ticks_ms() - prvMills) < timeout:
        if uart.any():
            resp = [resp, uart.read()]
            if resp != '':
                return resp

def get_keypress():
    for row in range(4):
        for col in range(4):
            row_pins[row].high()
            key = None
            if col_pins[col].value() == 1:
                # print("You have pressed:", matrix_keys[row][col])
                key_press = matrix_keys[row][col]
                sleep(0.3)
                if key_press != None:
                    return key_press
        row_pins[row].low()

def get_gsm_operator():
    opr = sendCMD_waitResp("AT+COPS?\r\n", uart1)
    try:
        opr = opr[1]
        opr = opr[12:-1]
        return opr
    except Exception:
        return "Unknown"

def get_gsm_netStrength():
    ntsr = sendCMD_waitResp("AT+CSQ\r\n", uart1)
    try:
        ntsr = ntsr[1]
        ntsr = ntsr[6:]
        return ntsr
    except Exception:
        return "0"

gsm_operator = get_gsm_operator()
gsm_signal_strength = get_gsm_netStrength()

def draw_qr(qr_data):
    qr.clear()
    qr.add_data(qr_data)
    matrix = qr.get_matrix()
    print("QR version:", qr.version)
    print("Matrix length", len(matrix))

    oled.fill(0)
    scale = 1

    offset_x = 45
    offset_y = 19

    for y in range(len(matrix)*scale):
        for x in range(len(matrix[0])*scale):
            value = not matrix[int(y/scale)][int(x/scale)]
            oled.pixel(x + offset_x, y + offset_y, value)
    oled.show()

oled.fill(0)
oled.show()

# draw_qr(upi_url + "")

def rgb_led_off():
    LED_RGB_R.low()
    LED_RGB_G.low()
    LED_RGB_B.low()
    return True

def rbg_led_color(rval, gval, bval):
    if rval == 1:
        LED_RGB_R.high()
    else:
        LED_RGB_R.low()
    if gval == 1:
        LED_RGB_G.high()
    else:
        LED_RGB_G.low()
    if bval == 1:
        LED_RGB_B.high()
    else:
        LED_RGB_B.low()
    return True

def blink_rgb_led(color, times, delay):
    if color == 'R':
        for i in range(0, times):
            LED_RGB_R.high()
            sleep(delay)
            LED_RGB_R.low()
            sleep(delay)
    elif color == 'G':
        for i in range(0, times):
            LED_RGB_G.high()
            sleep(delay)
            LED_RGB_G.low()
            sleep(delay)
    elif color == 'B':
        for i in range(0, times):
            LED_RGB_B.high()
            sleep(delay)
            LED_RGB_B.low()
            sleep(delay)
    LED_RGB_R.low()
    LED_RGB_G.low()
    LED_RGB_B.low()

def make_call():
    dial_num = ""
    oled.fill(0)
    oled.text("Make call", 25, 0)
    oled.text("Enter number:", 2, 16)
    oled.show()
    while True:
        key = get_keypress()
        if key != None:
            if key == "*":
                oled.fill(0)
                oled.text("Cancelled", 0, 0)
                oled.show()
                return "cancelled"
            elif key == "#":
                print(f"Dialing: {str(dial_num)}..")
                resp = sendCMD_waitResp("ATD" + dial_num + ";\r\n")
                if resp[1] == "OK":
                    print(f"Calling: {str(dial_num)}..")
                    oled.fill(0)
                    oled.text("Calling", 0, 0)
                    oled.text(str(dial_num), 2, 16)
                    oled.text('* to end', 2, 26)
                    oled.show()
                    while True:
                        key = get_keypress()
                        if key != None:
                            if key == "*":
                                print("Ending call..")
                                resp = sendCMD_waitResp("ATH;\r\n")
                                print(resp)
                                if len(resp) >= 2:
                                    if resp[1] == "OK" or resp[1] == "NO CARRIER":
                                        print("Call ended")
                                        oled.fill(0)
                                        oled.text("Call ended", 0, 0)
                                        oled.show()
                                        return "call_hangup"
                                    else:
                                        print("Call end error")
                                        oled.fill(0)
                                        oled.text("Call end error", 0, 0)
                                        oled.show()
                                        return "call_hangup_error"
                                else:
                                    print("Call end error")
                                    oled.fill(0)
                                    oled.text("Call end error", 0, 0)
                                    oled.show()
                                    return "call_hangup_error"
                else:
                    print(f"Error: {str(resp)}")
                    oled.fill(0)
                    oled.text("Error", 0, 0)
                    oled.text(str(resp), 0, 16)
                    oled.show()
                    sleep(2)
                    return make_call()
            else:
                if len(str(dial_num)) == 15:
                    dial_num = dial_num
                else:
                    dial_num += key
                oled.text(dial_num, 2, 26)
                oled.show()
                continue

def upi_payment():
    upi_amt = ""
    oled.fill(0)
    oled.text("Amt:", 0, 0)
    oled.show()
    qr.add_data(upi_url)
    matrix = qr.get_matrix()
    print("version:", qr.version)
    print("len of matrix", len(matrix))

    oled.fill(1)
    for y in range(len(matrix)*2):                   # Scaling the bitmap by 2
        for x in range(len(matrix[0])*2):            # because my screen is tiny.
            value = not matrix[int(y/2)][int(x/2)]   # Inverting the values because
            oled.pixel(x, y, value)                  # black is `True` in the matrix.
    oled.show()

def incoming_call():
    oled.text("Incoming call", 0, 0)
    oled.text("No call in..", 0, 16)
    oled.text("* for menu", 0, 26)
    oled.text("# to answer", 0, 36)
    oled.show()
    while True:
        key = get_keypress()
        if key == "*":
            main_menu()
        elif key == "#":
            print("Answering call..")
            resp = sendCMD_waitResp("ATA;\r\n")
            print(resp)
            if resp[1] == "OK":
                print("Call answered")
                oled.fill(0)
                oled.text("Call answered", 0, 0)
                oled.show()
                return "call_answered"
            else:
                print("Call answer error")
                oled.fill(0)
                oled.text("Call answer error", 0, 0)
                oled.show()
                return "call_answer_error"

def main_menu():
    global gsm_signal_strength, gsm_operator
    oled.fill(0)
    oled.text("Main Menu", 25, 0)
    oled.text("1. Call out", 2, 16)
    oled.text("2. Call in", 2, 26)
    oled.text("3. UPI Payment", 2, 36)
    oled.text("4. Option 4", 2, 46)
    oled.show()
    while True:
        key = str(get_keypress())
        # Check for incoming calls
        if uart1.any():
            resp = uart1.read().decode().strip()
            print(resp)
            if resp == "RING":
                print('Incoming call..')
        if key != None:
            if key == "1":
                print("Option: Make call.")
                call_ret = make_call()
                if call_ret != "":
                    sleep(2)
                    oled.fill(0)
                    main_menu()
                else:
                    sleep(2)
                    oled.fill(0)
                    main_menu()
            elif key == "2":
                print("2")
            elif key == "3":
                print("3")
            elif key == "4":
                print("4")

# blink_rgb_led('R', 2, 0.2)
# blink_rgb_led('G', 2, 0.2)
# blink_rgb_led('B', 2, 0.2)

if __name__ == "__main__":
    while True:
        try:
            print("GSM operator:", gsm_operator)
            print("GSM signal strength:", gsm_signal_strength)
            main_menu()
        except OSError:
            print("OS Error!")
            blink_rgb_led('R', 2, 0.5)
            blink_rgb_led('B', 2, 0.5)
