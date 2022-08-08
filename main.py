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

uart1 = UART(1, 9600)

LED_INBUILT = Pin(25, Pin.OUT)
LED_RGB_R = Pin(22, Pin.OUT)
LED_RGB_G = Pin(21, Pin.OUT)
LED_RGB_B = Pin(20, Pin.OUT)

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

# sleep(1)
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
    resp = sendCMD_waitResp("AT+CSPN?\r\n", uart1)
    sleep(4)
    if uart1.any():
        resp = [resp, uart1.read()]
    try:
        opr = resp[1].decode().replace('\r', '').split('\n')
        opr = opr[1].split('"')
        opr = opr[1]
        if opr != "ERROR" or "":
            return opr
        else:
            return "Unknown"
    except IndexError:
        blink_rgb_led('R', 1, 0.2)
        blink_rgb_led('B', 1, 0.2)
        blink_rgb_led('R', 1, 0.2)
        blink_rgb_led('B', 1, 0.2)
        print("Get operator index error.")
        return get_gsm_operator()

def get_gsm_netStrength():
    ntsr = sendCMD_waitResp("AT+CSQ\r\n", uart1)
    try:
        ntsr = ntsr[1]
        ntsr = ntsr[6:]
        ntsr = ntsr.split(",")
        ntsr = ntsr[0]
        if int(ntsr) > 0 and int(ntsr) < 10:
            net_condition = "Marginal"
        elif int(ntsr) >= 10 and int(ntsr) < 15:
            net_condition = "OK"
        elif int(ntsr) >= 15 and int(ntsr) < 20:
            net_condition = "Good"
        elif int(ntsr) >= 20 and int(ntsr) < 30:
            net_condition = "Excellent"
        else:
            net_condition = "Unknown"
        s_percentage = (int(ntsr)/30) * 100
        s_data = [str(ntsr), str(net_condition), str(s_percentage)]
        return s_data
    except Exception:
        s_data = [0, 0, 0]
        return s_data

def draw_qr(qr_data):
    qr.clear()
    qr.add_data(qr_data)
    matrix = qr.get_matrix()
    print("QR version:", qr.version)
    print("Matrix length", len(matrix))

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
    elif color == 'Y':
        for i in range(0, times):
            LED_RGB_G.high()
            LED_RGB_B.high()
            sleep(delay)
            LED_RGB_B.low()
            LED_RGB_G.low()
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
    oled.text(f"Amt: {upi_amt}", 0, 0)
    draw_qr(upi_url + upi_amt)
    while True:
        key = get_keypress()
        if key == '*':
            oled.fill(0)
            oled.text("Cancelled", 0, 0)
            oled.show()
            sleep(2)
            oled.fill(0)
            oled.show()
            main_menu()
        elif key == '#':
            oled.fill(0)
            draw_qr(upi_url + upi_amt)
            oled.text(f"Amt: {upi_amt}", 0, 0)
            oled.show()
        elif key != None:
            if len(upi_amt) >= 8:
                upi_amt = upi_amt
            else:
                upi_amt = upi_amt + str(key)
            oled.fill(0)
            oled.text(f"Amt: {upi_amt}", 0, 0)
            oled.show()

def incoming_call():
    oled.text("Incoming call..", 0, 0)
    oled.text("UNKNOWN", 0, 16)
    oled.text("* to decline", 0, 26)
    oled.text("# to answer", 0, 36)
    oled.show()
    while True:
        key = get_keypress()
        if key == "*":
            print("Call declined..")
            resp = sendCMD_waitResp("ATH;\r\n")
            print(resp)
            try:
                if resp[1] == "OK":
                    print("Call declined..")
                    oled.fill(0)
                    oled.text("Call declined", 0, 0)
                    oled.show()
                    sleep(2)
                    return "pre-ans-decline"
                else:
                    print("Call decline error")
                    oled.fill(0)
                    oled.text("Call decline error", 0, 0)
                    oled.show()
                    return "ans-err"
            except IndexError:
                print("Index Error")
                oled.fill(0)
                oled.text("Index error", 0, 0)
                oled.show()
                sleep(2)
                return "index-error"
        elif key == "#":
            print("Answering call..")
            resp = sendCMD_waitResp("ATA\r\n")
            sleep(2)
            print(resp)
            try:
                if resp[1] == "OK":
                    print("Call answered")
                    oled.fill(0)
                    oled.text("Ongoing call..", 0, 0)
                    oled.text("* to end", 0, 26)
                    oled.show()
                    call_time = 0
                    while True:
                        key = get_keypress()
                        if key == "*":
                            return "call-ended"
                        else:
                            call_time = call_time + 1
                            oled.fill(0)
                            oled.text("Ongoing call..", 0, 0)
                            oled.text("Time: " + str(call_time), 0, 16)
                            oled.text("* to end", 0, 26)
                            oled.show()
                else:
                    print("Call answer error")
                    oled.fill(0)
                    oled.text("Call answer error", 0, 0)
                    oled.show()
                    return "call-ans-err"
            except IndexError:
                print("Index Error")
                oled.fill(0)
                oled.text("Index error", 0, 0)
                oled.show()
                sleep(2)
                return "index-error"

def main_menu():
    oled.fill(0)
    oled.text("Getting opr..", 0, 0)
    oled.show()
    gsm_operator = get_gsm_operator()
    print(f"Operator: {str(gsm_operator)}")
    gsm_netStrength = get_gsm_netStrength()
    print(f"Network Strength: {str(gsm_netStrength[0])} {str(gsm_netStrength[1])} {str(gsm_netStrength[2])}%")
    oled.fill(0)
    gsm_net_strength_display = str(round(float(gsm_netStrength[2]), 0))
    title_str = f"{str(gsm_operator)} {gsm_net_strength_display}%"
    oled.text(title_str, 0, 0)
    oled.text("1. Make Call", 2, 16)
    oled.text("2. UPI Payment", 2, 26)
    oled.text("3. Option 3", 2, 36)
    oled.text("4. Option 4", 2, 46)
    oled.show()
    while True:
        key = str(get_keypress())
        if uart1.any():
            resp = uart1.read().decode().strip()
            print(resp)
            if resp == "RING":
                oled.fill(0)
                print(incoming_call())
        if key != None:
            if key == "1":
                print("Option: Make call.")
                call_ret = make_call()
                sleep(2)
                oled.fill(0)
                main_menu()
            elif key == "2":
                upi_payment()
            elif key == "3":
                print("3")
            elif key == "4":
                print("4")

if __name__ == "__main__":
    blink_rgb_led('R', 1, 0.1)
    blink_rgb_led('G', 1, 0.1)
    blink_rgb_led('B', 1, 0.1)
    while True:
        try:
            main_menu()
        except OSError:
            print("OS Error!")
            blink_rgb_led('R', 2, 0.5)
            blink_rgb_led('B', 2, 0.5)
