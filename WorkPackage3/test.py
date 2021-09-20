# Import libraries
#!/usr/bin/env python3

import RPi.GPIO as GPIO
import random
import ES2EEPROMUtils
import os
import time
eeprom = ES2EEPROMUtils.ES2EEPROM()
# some global variables that need to change as we run the program
end_of_game = None  # set if the user wins or ends the game
current_guess = 0
#variables to check if the botton is being held or pressed
holdorpress = 0
start_time = 0
pwm_accuracy = None
value = None
no_guess = 0
name = None
safety = 0

# DEFINE THE PINS USED HERE
LED_Value = [11, 13, 15]
LED_accuracy = 32
btn_submit = 16
btn_increase = 18
buzzer = None


# Print the game banner
def welcome():
    os.system('clear')
    print("  _   _                 _                  _____ _            __  __ _")
    print("| \ | |               | |                / ____| |          / _|/ _| |")
    print("|  \| |_   _ _ __ ___ | |__   ___ _ __  | (___ | |__  _   _| |_| |_| | ___ ")
    print("| . ` | | | | '_ ` _ \| '_ \ / _ \ '__|  \___ \| '_ \| | | |  _|  _| |/ _ \\")
    print("| |\  | |_| | | | | | | |_) |  __/ |     ____) | | | | |_| | | | | | |  __/")
    print("|_| \_|\__,_|_| |_| |_|_.__/ \___|_|    |_____/|_| |_|\__,_|_| |_| |_|\___|")
    print("")
    print("Guess the number and immortalise your name in the High Score Hall of Fame!")

# Print the game menu
def menu():
    global holdorpress 
    global start_time
    global end_of_game
    global current_guess
    global pwm_accuracy
    global pwm_buzzer
    global value
    global no_guess
    global name
    global safety 
    option = input("Select an option:   H - View High Scores     P - Play Game       Q - Quit\n")
    option = option.upper()
    if option == "H":
        os.system('clear')
        print("HIGH SCORES!!")
        s_count, ss = fetch_scores()
        display_scores(s_count, ss)
        menu()
    elif option == "P":
        os.system('clear')
        print("Starting a new round!")
        print("Use the buttons on the Pi to make and submit your guess!")
        print("Press and hold the guess button to cancel your game")
        value = generate_number()
        while not end_of_game:
            pass
    elif option == "Q":
        print("Come back soon!")
        exit()
    else:
        print("Invalid option. Please select a valid one!")


def display_scores(count, raw_data):
    # print the scores to the screen in the expected format
    length = len(raw_data) #get total number scores stored in eeprom
    print("There are {} scores. Here are the top 3!".format(count))
    #if statetements prevent errors if number of scores stored in eeprom <3
    if length>=3:
        # print name first then score of the already ordered array
        print("1st:" + raw_data[0][0] +" "+ str(raw_data[0][1]))
        print("2nd:" + raw_data[1][0] +" "+ str(raw_data[1][1]))
        print("3rd:" + raw_data[2][0] +" "+ str(raw_data[2][1]))
    elif length == 2:
        print("1st:" + raw_data[0][0] +" "+ str(raw_data[0][1]))
        print("2nd:" + raw_data[1][0] +" "+ str(raw_data[1][1]))
    elif length == 1:
        print("1st:" + raw_data[0][0] +" "+ str(raw_data[0][1]))
    elif length == 0:
        #catch case if no scores present in eeprom
        print("No scores to display")

    # print out the scores in the required format
    pass


# Setup Pins
def setup():
    global pwm_accuracy
    global pwm_buzzer
    # Setup board mode
    GPIO.setmode(GPIO.BOARD)
    
    # Setup regular GPIO
    GPIO.setup(LED_Value[0],GPIO.OUT); #set GPIO pin to LED Value 1 as output
    GPIO.setup(LED_Value[1],GPIO.OUT); #set GPIO pin to LED Value 2 as output
    GPIO.setup(LED_Value[2],GPIO.OUT); #set GPIO pin to LED Value 3 as output

    # ensure LED pins set to low on startup
    GPIO.output(LED_Value[0], GPIO.LOW)
    GPIO.output(LED_Value[1], GPIO.LOW)
    GPIO.output(LED_Value[2], GPIO.LOW)

    GPIO.setup(btn_submit,GPIO.IN, pull_up_down=GPIO.PUD_UP); #set GPIO pin to btn_submit as input
    GPIO.setup(btn_increase,GPIO.IN, pull_up_down=GPIO.PUD_UP); #set GPIO pin to btn_increase as input

    
    # Setup PWM channels
    GPIO.setup(LED_accuracy, GPIO.OUT); #set GPIO pin as output
    pwm_accuracy = GPIO.PWM(LED_accuracy,4000)#set up PWM to LED with f=1000
    pwm_accuracy.start(0) #initialise pwm with duty cyle of 0
    GPIO.setup(33, GPIO.OUT);
    pwm_buzzer = GPIO.PWM(33, 1)#set up PWM to buzzer with f=2300
    pwm_buzzer.stop()#prevent buzzer from sounding during setup

    # Setup debouncing and callbacks
    #button debouncing of 50ms, set to RISING & FALLING edge btn_submit linked to btn_guess_pressed function
    GPIO.add_event_detect(btn_submit, GPIO.BOTH, callback=btn_guess_pressed, bouncetime=50)
    # button debouncing of 50ms, set to RISING & FALLING edge btn_submit linked to btn_increase_pressed function
    GPIO.add_event_detect(btn_increase, GPIO.RISING, callback=btn_increase_pressed, bouncetime=200)
    current_guess = 0
    pass


# Load high scores
def fetch_scores():
    # get however many scores there are
    #eeprom.clear(10)
    score_count = eeprom.read_byte(0);#read total number of scores from first register
    scores = []#setup empty array to store related scores and names
    for i in range (1,score_count+1):
        names = eeprom.read_block(i, 3, bs=16) #read registers related to name
        name_char = chr(names[0])+chr(names[1])+chr(names[2]) #convert ascii to char
        scores1 = eeprom.read_byte(7+((i-1)*4)) #read score related to register
        scores.append([name_char,scores1]) #appended name and score to the array
    sorted_scores = sorted(scores,key=lambda x: x[1]) #sort the array from lowest to highest score
    #scores = None
    # Get the scores
    
    # convert the codes back to ascii
    
    # return back the results
    return score_count, sorted_scores #return total number scoreas and sorted score array


# Save high scores
def save_scores():
    global name
    global no_guess
    # fetch scores
    no_scores = eeprom.read_byte(0); #read first register to get total number of scores
    ascii_name = [] #empty array to hold name's ascii characters
    for character in name:
        ascii_name.append(ord(character)) #convert char to ascii and append to array

    # include new score
    eeprom.write_block(no_scores+1, ascii_name, bs=16, sleep_time=0.01)
    eeprom.write_byte(7+((no_scores)*4), no_guess)
    eeprom.write_byte(0, no_scores+1)
    #print statement to be used for debugging
    #print(eeprom.read_block(no_scores+1, 3, bs=16))
    #print(eeprom.read_byte(7+((no_scores)*4)))
    pass


# Generate guess number
def generate_number():
    return random.randint(0, pow(2, 3)-1) # returns a random number from 0 to seven


# if Increase button pressed, this function controls what happens as a result of the user input
def btn_increase_pressed(channel):
    pwm_buzzer.stop() # stops the buzzer from going off when the gues is changed to one farther away fro the correct one
    global current_guess #bring in the current guess variable, stores value diplayed on LED
    #if and else statements controlling the behavior of the LED's based on the user inputs 
    #displays the bindary values from 0 to seven
    if current_guess < 8:
        current_guess = current_guess + 1
    else:
        current_guess = 0
        GPIO.output(LED_Value[0], GPIO.HIGH)
        GPIO.output(LED_Value[1], GPIO.LOW)
        GPIO.output(LED_Value[2], GPIO.LOW)
    # Increase the value shown on the LEDs
    if current_guess == 1:
        GPIO.output(LED_Value[0], GPIO.HIGH)
        GPIO.output(LED_Value[1], GPIO.LOW)
        GPIO.output(LED_Value[2], GPIO.LOW)
    elif current_guess == 2:
        GPIO.output(LED_Value[0], GPIO.LOW)
        GPIO.output(LED_Value[1], GPIO.HIGH)
        GPIO.output(LED_Value[2], GPIO.LOW)
    elif current_guess == 3:
        GPIO.output(LED_Value[0], GPIO.HIGH)
        GPIO.output(LED_Value[1], GPIO.HIGH)
        GPIO.output(LED_Value[2], GPIO.LOW)
    elif current_guess == 4:
        GPIO.output(LED_Value[0], GPIO.LOW)
        GPIO.output(LED_Value[1], GPIO.LOW)
        GPIO.output(LED_Value[2], GPIO.HIGH)
    elif current_guess == 5:
        GPIO.output(LED_Value[0], GPIO.HIGH)
        GPIO.output(LED_Value[1], GPIO.LOW)
        GPIO.output(LED_Value[2], GPIO.HIGH)
    elif current_guess == 6:
        GPIO.output(LED_Value[0], GPIO.LOW)
        GPIO.output(LED_Value[1], GPIO.HIGH)
        GPIO.output(LED_Value[2], GPIO.HIGH)
    elif current_guess == 7:
        GPIO.output(LED_Value[0], GPIO.HIGH)
        GPIO.output(LED_Value[1], GPIO.HIGH)
        GPIO.output(LED_Value[2], GPIO.HIGH)
    pass

#this funciton is able to restart the program to allow the user to play the game again without manually typing the code
def restart():
    import sys #library needed
    print("argv was", sys.argv)
    print("sys.executable was", sys.executable)
    print("restart now")
    import os
    os.execv(sys.executable, ['python3'] + sys.argv) #executes the program again using python3 executable

# if guess submit button pressed, this function controls what happens as a result of the user input
def btn_guess_pressed(channel):
    pwm_buzzer.stop() #ensure buzzer stops after sumbitted guess
    #making sure global variables are avaliable to the function
    global pwm_accuracy
    global holdorpress
    global start_time
    global current_guess
    global value
    global holdorpress
    global start_time
    global no_guess
    global name
    global safety 
   
    #code to check if the button is being held down for more than two seconds, if the falling edge of the button relese occurs two seconds after the rising edge of the button press, then the program takes the user to the menu screen rather than submitting a guess

    if holdorpress == 0: #this checks that this is a rising edge response 
        start_time = time.time() #starts comparitor timer
        holdorpress += 1 #increments holdorpress so that the next time the button registers an interupt the code knows it is a falling edge and not a rising edge

    else: #if a falling ege is detected then the code checks how long ago the orignal rsing edge occurs
        time_1 = time.time() - start_time #this conprares falling edge time to rising edge time
        if time_1 > 2: #if the time is longer than two then long press has been activated
            #everthing is reset and program is restarted to take user to the home screen
            no_guess = 0 
            GPIO.output(LED_Value[0], GPIO.LOW)
            GPIO.output(LED_Value[1], GPIO.LOW)
            GPIO.output(LED_Value[2], GPIO.LOW)
            pwm_accuracy.stop()
            pwm_buzzer.stop()
            restart()
       
        else: #short press activated
            if safety == 0: #this makes sure that the user is not inputting anything after winning the game already
                no_guess += 1 #increments amount of guesses
            
            #check if the guess differs from the hidden value
            difference = value - current_guess
            difference = abs(difference) #gets the absolute value
            accuracy_leds()
            #if user has guessed the value correctly
            if difference == 0:
                safety = 1 #makes sure that no more inputs can occur
                val = input("You won!!! Insert name: ") #asks user for name

                # variables to use as comparators in the while loops
                i = 0
                z = 0

                #while loop ensures that the name is exactly three characters long
                while i != 1:
                    if len(val)!=3: #if not 3 character then the user must re enter the name
                        print("invalid name!, the name must be three characters long")
                        val = input("You won!!!! Insert name: ")
                    else: #if the name is three character, then the score and name is saved
                        print("name and score saved!!!!")
                        name = val #name is saved to global variable "name"
                        save_scores() #calls the function to save the score to the eeprom

                        #after the user saves their name and score, this while loops asks the user if the want tot reurn to the main menu or exit the program
                        i = 1
                        x = input("Press y to go to main menu and any other button to quit: ")
                        while z !=1:
                            if x=="y": #the program will restart
                                restart()
                            else: #the program will exit
                                exit()
            
            elif difference <=3: #trigger buzzer based on proximity to correct answer
                trigger_buzzer(difference)
        holdorpress = 0 #ensures variable is set to zero so prograrm can execute again seamlessly
    pass


# cotrol LED Brightness
def accuracy_leds():
    global pwm_accuracy #gets accuracy of guess
    duty_cycle = (current_guess/(0.000001+value))*100 #sets duty cucly based of guess proximity, higher duty cycle for a closer guess
    if duty_cycle >100: #if there is an overflow error, duty cycle set to 50
        duty_cycle = 50
    pwm_accuracy.start(duty_cycle)
    # Set the brightness of the LED based on how close the guess is to the answer
    # - The % brightness should be directly proportional to the % "closeness"
    # - For example if the answer is 6 and a user guesses 4, the brightness should be at 4/6*100 = 66%
    # - If they guessed 7, the brightness would be at ((8-7)/(8-6)*100 = 50%
    pass

# Sound Buzzer
def trigger_buzzer(diff):
    #gets global variables
    global pwm_buzzer 
    global current_guess
    global value
    # The buzzer operates differently from the LED
    # While we want the brightness of the LED to change(duty cycle), we want the frequency of the buzzer to change
    # The buzzer duty cycle should be left at 50%
    # If the user is off by an absolute value of 3, the buzzer should sound once every second

#controls frequency of buzzer based on guess proxity to accurate answer, the closer the guess, the higher the frequency
    if diff == 3:
        pwm_buzzer.start(50)
        pwm_buzzer.ChangeFrequency(1)
    elif diff == 2:
        pwm_buzzer.start(50)
        pwm_buzzer.ChangeFrequency(2)
    elif diff == 1:
        pwm_buzzer.start(50)
        pwm_buzzer.ChangeFrequency(4)
    pass


if __name__ == "__main__":
    try:
         #Call setup function
        setup()
        welcome()
        while True:
            menu()
            pass
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()

