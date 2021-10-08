#Import all relevant libraries
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import threading
import datetime
import time
#Declare global variables
global now
global button
global Timeint
#Instantiate some global variables
Timeint = 5
now = datetime.datetime.now()

#setup function for IO pins
def setup():
    #button setup with digitalIO
    button = digitalio.DigitalInOut(board.D26)
    button.switch_to_input(pull=digitalio.Pull.UP)
    #create the spi bus
    spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
    #create the cs (chip select)
    cs = digitalio.DigitalInOut(board.D5)
    #create the mcp object
    mcp = MCP.MCP3008(spi, cs)
    pass

#Get ADC value for LDR
def LDR():
    #spi bus
    spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
    #cs (chip select)
    cs = digitalio.DigitalInOut(board.D5)
    #mcp object
    mcp = MCP.MCP3008(spi, cs)
    #create an analog input channel on pin 2
    chan2 = AnalogIn(mcp,MCP.P2)
    #return the ADC value
    return chan2.value

#Get ADC voltage for Temperature sensor
def Temp():
    #spi bus
    spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
    #cs (chip select)
    cs = digitalio.DigitalInOut(board.D5)
    #mcp object
    mcp = MCP.MCP3008(spi, cs)
    #create an analog input channel on pin 1
    chan1 = AnalogIn(mcp,MCP.P1)
    #Get ADC voltage
    temp = chan1.voltage
    #return ADC voltage
    return temp

#Convert tmeperature sensor ADC voltage to temperature in degrees
def Temp_Degrees(temp):
    #Using transfer function from MCP9700 datasheet to convert ADC voltage to degrees celcius
    temp_degrees = (temp-0.5)
    temp_degrees = temp_degrees*100
    
    return temp_degrees

#Change sample time from push button
def sample_time():
    global Timeint
    #Checks if current time is 5s and then changes it to 10s
    if Timeint ==5:
       Timeint =10
       time.sleep(10)
    #Checks if current time is 10s and then changes it to 1s
    elif Timeint ==10:
       Timeint = 1
       time.sleep(5)
    #Checks if current time is 1s and then changes it to 5s
    elif Timeint == 1:
       Timeint = 5
       time.sleep(10)

#display Temperature, light and ADC readings in correct format
def Display():
    #Calculating Runtime according to current real clock time between prevoius and current print sequence
    Runtime = round((datetime.datetime.now()-now).total_seconds())
    ldr = str(LDR())
    temp = Temp()
    #format values to two decimal places
    temp = round(temp,2)
    temp_degrees = Temp_Degrees(temp)
    temp_degrees = round(temp_degrees, 2)
    #Print the corresponding values
    print(str(Runtime) +"s \t\t " +str(temp) +" \t\t " + str(temp_degrees) +" C\t\t " + ldr)

    
#This function prints the values to the screen at the specified time interval
#Source: EEE Wiki page
def print_time_thread():
    #Change interval value (Timeint) for function to operate with
    thread = threading.Timer(Timeint, print_time_thread)
    thread.daemon = True  # Daemon threads exit when the program does
    thread.start()
    Display()
 

#Source: EEE Wiki page
if __name__ == "__main__":
    print("Runtime \t Temp Reading \t Temp \t\t Light Reading")
    setup()
    print_time_thread() # call the thread once to start the thread 
    button = digitalio.DigitalInOut(board.D26)
    button.switch_to_input(pull=digitalio.Pull.UP)
    
    # Tell our program to run indefinitely
    while True:
        #Check if button has been pressed
        if not button.value:
            #"callback function"
            i = threading.Thread(target=sample_time) 
            i.start()
            i.join()
        pass

