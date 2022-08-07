from machine import Pin
import utime

uart1 = machine.UART(1, baudrate = 9600)

#2 sec timeout is arbitrarily chosen
def sendCMD_waitResp(cmd, uart = uart1, timeout = 2000):
    # print("CMD: " + cmd)
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
                # print(resp.decode())
                return resp

# sendCMD_waitResp("AT+CGATT?\r\n")
# utime.sleep(2)
resp = sendCMD_waitResp("ATD9538271867;\r\n")
print(resp)
utime.sleep(8)
resp = sendCMD_waitResp("ATH\r\n")
print(resp)