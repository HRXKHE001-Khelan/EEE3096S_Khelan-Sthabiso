# Import libraries
import RPi.GPIO as GPIO
import random
import ES2EEPROMUtils
import os

# some global variables that need to change as we run the program
end_of_game = None  # set if the user wins or ends the game

# DEFINE THE PINS USED HERE
LED_value = [11, 13, 15]
LED_accuracy = 32
btn_submit = 16
btn_increase = 18
buzzer = 33 #None
eeprom = ES2EEPROMUtils.ES2EEPROM()


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

    global end_of_game
    option = input("Select an option:   H - View High Scores     P - Play Game       Q - Quit\n")
    option = option.upper()
    if option == "H":
        os.system('clear')
        print("HIGH SCORES!!")
        s_count, ss = fetch_scores()
        display_scores(s_count, ss)
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
    print("There are {} scores. Here are the top 3!".format(count))
    # print out the scores in the required format
    pass


# Setup Pins
def setup():
    # Setup board mode
    GPIO.setmode(GPIO.BOARD)

    #setup regular GPIO
    GPIO.setup(LED_value[0], GPIO.OUT)
    GPIO.setup(LED_value[1], GPIO.OUT)
    GPIO.setup(LED_value[2], GPIO.OUT)
    GPIO.setup(LED_accuracy, GPIO.OUT)
    
    GPIO.output(LED_value[0], GPIO.LOW)
    GPIO.output(LED_value[1], GPIO.LOW)
    GPIO.output(LED_value[2], GPIO.LOW)
    GPIO.output(LED_accuracy, GPIO.LOW)
	
    GPIO.setup(buzzer, GPIO.OUT)
    
    GPIO.setup(btn_submit, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(btn_increase, GPIO.IN,pull_up_down = GPIO.PUD_UP)

    # Setup PWM channels
    LED_red = GPIO.PWM(LED_accuracy, 1000)
    LED_red.start(50)

    Buzzer_pwm = GPIO.PWM(33, 2)
    Buzzer_pwm.start(50)

    # Setup debouncing and callbacks
    GPIO.add_event_detect(btn_submit, GPIO.FALLING, callback = btn_guess_pressed, bouncetime = 200)
    GPIO.add_event_detect(btn_increase, GPIO.FALLING, callback = btn_increase_pressed, bouncetime = 200)
    pass


# Load high scores
def fetch_scores():
    # get however many scores there are
    score_count = char(len(eeprom.read_byte(0))

    # Get the scores
    for i in range(1,3,1):
	scores = char(eeprom.readblock(i,4))
    # convert the codes back to ascii
    
    # return back the results
    return score_count, scores


# Save high scores
def save_scores():
    # fetch scores
    x = fetch_scores();
    
    # include new score
    # sort
    # update total amount of scores
    # write new scores
    pass


# Generate guess number
def generate_number():
    return random.randint(0, pow(2, 3)-1)


# Increase button pressed
def btn_increase_pressed(channel):
                       
# You can choose to have a global variable store the user's current guess,                       
    global guess_number
    
    if GPIO.input(btn_increase) == 0:
    	if guess_number == 7:
		guess_number =0
	else:
		guess_number+ = 1
        	
                       
    # Increase the value shown on the LEDs
    if guess_number == 0:
        GPIO.output(LED_value[0], GPIO.LOW)
        GPIO.output(LED_value[1], GPIO.LOW)
        GPIO.output(LED_value[2], GPIO.LOW)
    elif guess_number == 1:
        GPIO.output(LED_value[0], GPIO.LOW)
        GPIO.output(LED_value[1], GPIO.LOW)
        GPIO.output(LED_value[2], GPIO.HIGH)
    elif guess_number == 2:
        GPIO.output(LED_value[0], GPIO.LOW)
        GPIO.output(LED_value[1], GPIO.HIGH)
        GPIO.output(LED_value[2], GPIO.LOW)
    elif guess_number == 3:
        GPIO.output(LED_value[0], GPIO.LOW)
        GPIO.output(LED_value[1], GPIO.HIGH)
        GPIO.output(LED_value[2], GPIO.HIGH)
    elif counter == 4:
        GPIO.output(LED_value[0], GPIO.HIGH)
        GPIO.output(LED_value[1], GPIO.LOW)
        GPIO.output(LED_value[2], GPIO.LOW)
    elif counter == 5:
        GPIO.output(LED_value[0], GPIO.HIGH)
        GPIO.output(LED_value[1], GPIO.LOW)
        GPIO.output(LED_value[2], GPIO.HIGH)
    elif counter == 6:
        GPIO.output(LED_value[0], GPIO.HIGH)
        GPIO.output(LED_value[1], GPIO.HIGH)
        GPIO.output(LED_value[2], GPIO.LOW)
    elif counter == 7:
        GPIO.output(LED_value[0], GPIO.HIGH)
        GPIO.output(LED_value[1], GPIO.HIGH)
        GPIO.output(LED_value[2], GPIO.HIGH)
    pass
    # or just pull the value off the LEDs when a user makes a guess
    pass


# Guess button
def btn_guess_pressed(channel):
    # If they've pressed and held the button, clear up the GPIO and take them back to the menu screen.
    ####################       
    	GPIO.cleanup()
   	menu()
		       
    # Compare the actual value with the user value displayed on the LEDs		       
    while(1):
    	if GPIO.input(btn_submit) === 0:
		if count!= generate_number():
			accuracy_leds()       
    			sleep(0.1)
		        trigger_buzzer()
		        sleep(0.1)
		else:
		        # - Disable LEDs and Buzzer
			GPIO.output(LED_accuracy, 0)       
		        sleep(0.1)
		        GPIO.output(buzzer, 0)
		        slepp(0.1)
    
		       
    #LED_red.start(50)
		       
    # Change the PWM LED
    # if it's close enough, adjust the buzzer
		       
    # if it's an exact guess:
    # - Disable LEDs and Buzzer
    # - tell the user and prompt them for a name
    # - fetch all the scores
    # - add the new score
    # - sort the scores
    # - Store the scores back to the EEPROM, being sure to update the score count
    pass


# LED Brightness
def accuracy_leds():
    # Set the brightness of the LED based on how close the guess is to the answer
    brightness = 0
    if count>generate_number():
    # - If they guessed 7, the brightness would be at ((8-7)/(8-6)*100 = 50%			       
    	brightness =((8-count)/(8-generate_number()))*100
	LED_red.start(50)	       
	LED_red.ChangeDutyCycle(brightness)
		       
    if count<generate_number():
     # - For example if the answer is 6 and a user guesses 4, the brightness should be at 4/6*100 = 66%		       
	brightness=(count/generate_number())*100
	LED_red.start(50)	       
	LED_red.ChangeDutyCycle(brightness)	       
    # - The % brightness should be directly proportional to the % "closeness" 
    pass

# Sound Buzzer
def trigger_buzzer():
    # The buzzer operates differently from the LED
    # While we want the brightness of the LED to change(duty cycle), we want the frequency of the buzzer to change
    # The buzzer duty cycle should be left at 50%
    #buzzz = 0	       
    # If the user is off by an absolute value of 3, the buzzer should sound once every second	       
    if abs(count-generate_number) == 3
    	Buzzer_pwm.start(50)
	Buzzer_pwm.ChangeFrequency(1)
		       	       
    # If the user is off by an absolute value of 2, the buzzer should sound twice every second
    if abs(count-generate_number) == 2
	Buzzer_pwm.start(50)
	Buzzer_pwm.ChangeFrequency(2)	       
    # If the user is off by an absolute value of 1, the buzzer should sound 4 times a second
    if abs(count-generate_number) == 1
	Buzzer_pwm.start(50)
	Buzzer_pwm.ChangeFrequency(4)		       
    pass


if __name__ == "__main__":
   #eeprom.populate_mock_scores()
    try:
        # Call setup function
        setup()
        welcome()
        while True:
            menu()
            pass
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()
