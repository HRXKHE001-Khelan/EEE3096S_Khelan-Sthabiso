import datetime
import threading
import time
import RPi.GPIO as GPIO
import adafruit_mcp3xxx.mcp3008 as MCP
import board
import busio
import digitalio
from adafruit_mcp3xxx.analog_in import AnalogIn

global start_time
start_time=datetime.datetime.now()
global interval
interval = 5

def setup():

    # create the spi bus
    spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
    # create the cs (chip select)
    cs = digitalio.DigitalInOut(board.D5)
    # create the mcp object
    mcp = MCP.MCP3008(spi, cs)
    #set up the button using digitalio
    button = digitalio.DigitalInOut(board.D24)
    button.switch_to_input(pull=digitalio.Pull.UP)

def change_interval():
    global interval
    
    if interval ==5:
        interval =10
        print("button pressed interval = 10")
        time.sleep(10)

    elif interval ==10:
        interval = 1
        print("button pressed interval = 1")
        time.sleep(5)

    elif interval == 1:
        interval = 5
        print("button pressed interval = 5")
        time.sleep(10)    


def getLDR():
    # create the spi bus
    spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
    # create the cs (chip select)
    cs = digitalio.DigitalInOut(board.D5)
    # create the mcp object
    mcp = MCP.MCP3008(spi, cs)
    # create an analog input channel on pin 2
    chan = AnalogIn(mcp, MCP.P2)
    return chan.value
    #print("Raw ADC Value: ", chan.value)
    #print("ADC Voltage: " + str(chan.voltage) + "V")

def getTemp_voltage():
    # create the spi bus
    spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
    # create the cs (chip select)
    cs = digitalio.DigitalInOut(board.D5)
    # create the mcp object
    mcp = MCP.MCP3008(spi, cs)
    # create an analog input channel on pin 1
    chan_Temp = AnalogIn(mcp, MCP.P1)
    temp_voltage = chan_Temp.voltage
    temp = (temp_voltage - 0.5)
    temp = temp/0.01
    return temp_voltage
    #print("Value Temp Sensor", temp)
    #print("ADC Voltage Temp Sensor: ", str(chan_Temp.voltage) + "V")

def convertDegrees(temp_voltage):
    temp = (temp_voltage - 0.5)
    temp = temp / 0.01
    return temp

def format_output():
    temp_voltage = getTemp_voltage()
    temp_deg = round(convertDegrees(temp_voltage), 1)
    temp_deg = str(temp_deg)
    temp_voltage = round(temp_voltage, 3)
    temp_voltage = str(temp_voltage)
    light = round(getLDR(),5)
    light = str(light)
    runTime = round((datetime.datetime.now()-start_time).total_seconds())
    runTime = str(runTime)
    print(runTime +"s \t\t " + temp_voltage +" \t\t " + temp_deg +" C\t\t " + light)


def print_time_thread():
    """
    This function prints the time to the screen every five seconds
    """
    thread = threading.Timer(interval, print_time_thread)
    thread.daemon = True  # Daemon threads exit when the program does
    thread.start()
    format_output()
    #getTemp()
    #getLDR()
    #print(round((datetime.datetime.now()-start_time).total_seconds()))
    #print("")


if __name__ == "__main__":
    print("Runtime \t Temp Reading \t Temp \t\t Light Reading")
    print_time_thread()  # call it once to start the thread
    # Tell our program to run indefinitely
    setup()
    button = digitalio.DigitalInOut(board.D24)
    button.switch_to_input(pull=digitalio.Pull.UP)

    while True:
        if not button.value:
            x = threading.Thread(target=change_interval) 
            x.start()
            x.join()
        pass
        

