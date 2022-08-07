from machine import Pin, UART
uart = UART(0, 9600)

led = Pin(25, Pin.OUT)

command = ""

uart.write("ATD9538271867\r\n")

while True:
    if uart.any():
        resp = uart.read().decode().strip()
        print(resp)
        if resp == "RING":
            led.high()
            print('THE PHONE IS RINGING!')
        else:
            led.low()
            continue
