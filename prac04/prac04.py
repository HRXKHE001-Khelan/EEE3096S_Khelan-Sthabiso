import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import threading
import datetime

global now
global button
global T
T = 5

now = datetime.datetime.now()

def setup():
    button = digitalio.DigitalInOut(board.D21)
    button.switch_to_input(pull=digitalio.Pull.UP)

    spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
    cs = digitalio.DigitalInOut(board.D5)
    mcp = MCP.MCP3008(spi, cs)
    pass

def Temp():
    spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
    cs = digitalio.DigitalInOut(board.D5)
    mcp = MCP.MCP3008(spi, cs)

    chan1 = AnalogIn(mcp,MCP.P1)
    temp = chan1.voltage
    return temp


def Temp_Degrees(temp):
    temp_degrees = (temp-0.5)*100
    return temp_degrees

def sample_time():

    global T
    if T ==5:
       T =10
       time.sleep(10)

    elif T ==10:
       T = 1
       time.sleep(5)

    elif T == 1:
       T = 5
       time.sleep(10)


def LDR():
    spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
    cs = digitalio.DigitalInOut(board.D5)
    mcp = MCP.MCP3008(spi, cs)

    chan2 = AnalogIn(mcp,MCP.P2)
    return chan2.value

def Display():
    ldr = str(LDR())
    temp = Temp()
    temp = round(temp,2)

    temp_degrees = Temp_Degrees(temp)
    temp_degrees = round(temp_degrees, 2)

    Runtime = round((datetime.datetime.now()-now).total_seconds())
    print(str(Runtime) +"s \t\t " +str(temp) +" \t\t " + str(temp_degrees) +" C\t\t " + ldr)

def print_time_thread():
    """
    This function prints the time to the screen every five seconds
    """
    thread = threading.Timer(T, print_time_thread)
    thread.daemon = True  # Daemon threads exit when the program does
    thread.start()
    Display()

if __name__ == "__main__":
    print("Runtime \t Temp Reading \t Temp \t\t Light Reading")
    print_time_thread() # call it once to start the thread
    setup()

    # Tell our program to run indefinitely
    button = digitalio.DigitalInOut(board.D21)
    button.switch_to_input(pull=digitalio.Pull.UP)

    while True:
        if not button.value:
            x = threading.Thread(target=sample_time) 
            x.start()
            x.join()
        pass

