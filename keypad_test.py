from machine import Pin
from time import sleep

matrix_keys = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']
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
    
print("Please enter a key from the keypad")
    
def scankeys():  
    for row in range(4):
        for col in range(4):
            row_pins[row].high()
            key = None
            if col_pins[col].value() == 1:
                print("You have pressed:", matrix_keys[row][col])
                key_press = matrix_keys[row][col]
                sleep(0.3)
                if key_press != None:
                    return key_press
        row_pins[row].low()

while True:
    key = scankeys()
    if key != None:
        print("KEY: " + str(key))
