# pico-phone
A simple mobile phone built with the Raspberry Pi Pico.

**This project has been discontinued and will be continued as PAY-PHONE**

Features:
1. Incoming and Outgoing calls
2. Accept UPI payments directly to your bank account by generating a QR code of your UPI ID.

Components used:
1. Raspberry Pi Pico
2. SSD1306 128x64 OLED Display
3. 4X4 Matrix Keypad
4. GSM Module (Here: SIM800L)
5. RGB Led (Common Cathode)

Credits:
uQR Library: https://github.com/JASchilz/uQR

SSD1306 Library: https://github.com/micropython/micropython-lib/tree/master/micropython/drivers/display/ssd1306

New features added:
 1. Incoming call answer and decline capabilities.

Features to be added:
1. Enabling multi-core functionality on the Pi Pico to recognize incoming calls.
2. Wifi & Bluetooth connectivity to verify UPI payments is real time.
