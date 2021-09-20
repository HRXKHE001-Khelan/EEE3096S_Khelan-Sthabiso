# Import libraries
import RPi.GPIO as GPIO
import random
import ES2EEPROMUtils
import os
import time
# some global variables that need to change as we run the program
end_of_game = None  # set if the user wins or ends the game
global TScore, Tname
global actual_value
global guess_value
# DEFINE THE PINS USED HERE
LED_value = [11, 13, 15]
LED_accuracy = 32
btn_submit = 16
btn_increase = 18
buzzer = 33
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

    global actual_value
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
        actual_value = generate_number()
        #Menu = False
        while not end_of_game:
            pass
    elif option == "Q":
        print("Come back soon!")
        exit()
    else:
        print("Invalid option. Please select a valid one!")

def display_scores(count, raw_data):

    l = len(raw_data)
    print("There are {} scores. Here are the top 3!".format(count))
    if l >= 3:
       print("1st place: " + raw_data[0][0]+" score: "+str(raw_data[0][1]))
       print("2nd place: " + raw_data[1][0]+" score: "+str(raw_data[1][1]))
       print("3rd place: " + raw_data[2][0]+" score: "+str(raw_data[2][1]))
    elif l == 2:
       print("1st place: " + raw_data[0][0]+" score: "+str(raw_data[0][1]))
       print("2nd place: " + raw_data[1][0]+" score: "+str(raw_data[1][1]))
    elif l ==1:
       print("1st place: " + raw_data[0][0]+" score: "+str(raw_data[0][1]))
    else:
       print("There are no scores to display :(")
    pass

# Setup Pins
def setup():
    global guess_value
    guess_value =0
 
    # Setup board mode
    GPIO.setmode(GPIO.BOARD)

    #setp regular GPIO
    GPIO.setup(LED_value[0], GPIO.OUT)
    GPIO.setup(LED_value[1], GPIO.OUT)
    GPIO.setup(LED_value[2], GPIO.OUT)
    GPIO.setup(LED_accuracy, GPIO.OUT)
    GPIO.setup(buzzer, GPIO.OUT)
    GPIO.setup(btn_submit, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(btn_increase, GPIO.IN,pull_up_down = GPIO.PUD_UP)

    # Setup PWM channels
    global LED_red
    LED_red = GPIO.PWM(LED_accuracy, 1000)
    #LED_red.start(50)

    #Buzzer_pwm.start(50)
    GPIO.output(LED_value[0],GPIO.LOW)
    GPIO.output(LED_value[1],GPIO.LOW)
    GPIO.output(LED_value[2],GPIO.LOW)


    global Buzzer_pwm
    Buzzer_pwm = GPIO.PWM(buzzer,1)
    Buzzer_pwm.stop()
    GPIO.output(buzzer,GPIO.LOW)
    # Setup debouncing and callbacks
    GPIO.add_event_detect(btn_submit, GPIO.FALLING, callback = btn_guess_pressed, bouncetime = 200)
    GPIO.add_event_detect(btn_increase, GPIO.FALLING, callback = btn_increase_pressed, bouncetime = 200)
    pass


# Load high scores
def fetch_scores():

    track_score = 7
    scores = [] #initialize array scores
    score_count = eeprom.read_byte(0)
    #get however many scores there are

    for i in range(0,score_count):
        name = ""
        for k in range((i+1)*4,(i+1)*4+3):
            name = name + chr(eeprom.read_byte(k))
        scores.append([name,eeprom.read_byte(track_score)])
    # convert the codes back to ascii
    # return back the results
    track_score+=4

    return score_count, scores


# Save high scores
def save_scores():
    global guesses
    #fetch scores
    score_count, scores = fetch_scores()
    #so then we need to add a 1 to score count
    score_count +=1

    print("Congratulation, your guess is correct: "+str(actual_value)+"\n")
    user_name = input("Enter your name using 3 Letters:\n")

    i = 0
    while i != 1:
          if len(user_name) != 3:
             user_name = input("Error! Enter your name using 3 Letters:\n")
          else:
             guesses+=1

             scores.append([user_name,guesses])
             scores.sort(key=lambda x: x[1])

             eeprom.write_byte(0, score_count)

             score_reg = 7
             for i in range(0, score_count):
                 a = scores[i]
                 b = a[0]
                 c = 0
                 for j in range((i+1)*4,(i+1)*4+3):
                     eeprom.write_byte(j, ord(b[c]))
                     c+=1
                     eeprom.write_byte(score_reg,a[1])
                     score_reg += 4

             guess_value = 0
             Buzzer_pwm.stop()
             LED_red.stop()
             GPIO.output(LED_value[0], GPIO.LOW)
             GPIO.output(LED_value[1], GPIO.LOW)
             GPIO.output(LED_value[2], GPIO.LOW)
             GPIO.cleanup()
             setup()
             menu()
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
    global guess_value

    if guess_value<8:
       guess_value = guess_value+1

    else:
       guess_value = 0
       GPIO.output(LED_value[0], GPIO.LOW)
       GPIO.output(LED_value[1], GPIO.LOW)
       GPIO.output(LED_value[2], GPIO.LOW)

    # Increase the value shown on the LEDs
    if guess_value == 1:
       GPIO.output(LED_value[0], GPIO.LOW)
       GPIO.output(LED_value[1], GPIO.LOW)
       GPIO.output(LED_value[2], GPIO.HIGH)
    elif guess_value == 2:
       GPIO.output(LED_value[0], GPIO.LOW)
       GPIO.output(LED_value[1], GPIO.HIGH)
       GPIO.output(LED_value[2], GPIO.LOW)
    elif guess_value == 3:
       GPIO.output(LED_value[0], GPIO.LOW)
       GPIO.output(LED_value[1], GPIO.HIGH)
       GPIO.output(LED_value[2], GPIO.HIGH)
    elif guess_value == 4:
       GPIO.output(LED_value[0], GPIO.HIGH)
       GPIO.output(LED_value[1], GPIO.LOW)
       GPIO.output(LED_value[2], GPIO.LOW)
    elif guess_value == 5:
       GPIO.output(LED_value[0], GPIO.HIGH)
       GPIO.output(LED_value[1], GPIO.LOW)
       GPIO.output(LED_value[2], GPIO.HIGH)
    elif guess_value == 6:
       GPIO.output(LED_value[0], GPIO.HIGH)
       GPIO.output(LED_value[1], GPIO.HIGH)
       GPIO.output(LED_value[2], GPIO.LOW)
    elif guess_value == 7:
       GPIO.output(LED_value[0], GPIO.HIGH)
       GPIO.output(LED_value[1], GPIO.HIGH)
       GPIO.output(LED_value[2], GPIO.HIGH)


    pass


# Guess button
def btn_guess_pressed(channel):
    global guesses
    guesses = 0
    global guess_value
    global actual_value
    start_time = time.time()
    while GPIO.input(btn_submit) == 0:
          pass #stalling bitch

    pressedTime = time.time()-start_time
    if pressedTime > 0.5 :
       Buzzer_pwm.stop()
       LED_red.stop
       GPIO.cleanup()
       setup()
       menu()
    else:
       if guess_value == actual_value:
          guess_value=0
          guesses+=1
          Buzzer_pwm.stop()
          save_scores()

       else:

          guesses+=1
          accuracy_leds()
          trigger_buzzer()

# LED Brightness
def accuracy_leds():
    # Set the brightness of the LED based on how close the guess is to the answer
    brightness = 0
    if guess_value>actual_value:
    # - If they guessed 7, the brightness would be at ((8-7)/(8-6)*100 = 50%
       brightness =(((8-guess_value)/(8-actual_value))*100)
       LED_red.start(brightness)
    elif guess_value<actual_value:
     # - For example if the answer is 6 and a user guesses 4, the brightness should be at 4/6*100 = 66%
       brightness=((guess_value/actual_value)*100)
       LED_red.start(brightness)
    # - The % brightness should be directly proportional to the % "closeness"
    elif guess_value == actual_value:
       LED_red.start(100)
    else:
       LED_red.start(brightness)
    pass

# Sound Buzzer
def trigger_buzzer():
    # The buzzer operates differently from the LED
    # While we want the brightness of the LED to change(duty cycle), we want the frequency of the buzzer to change
    # The buzzer duty cycle should be left at 50%
    #buzzz = 0
    # If the user is off by an absolute value of 3, the buzzer should sound once every second
    if abs(guess_value-actual_value) == 3:
       Buzzer_pwm.start(50)
       Buzzer_pwm.ChangeFrequency(1)
    # If the user is off by an absolute value of 2, the buzzer should sound twice every second
    elif abs(guess_value-actual_value) == 2:
       Buzzer_pwm.start(50)
       Buzzer_pwm.ChangeFrequency(2)
    # If the user is off by an absolute value of 1, the buzzer should sound 4 times a second
    elif abs(guess_value-actual_value) == 1:
       Buzzer_pwm.start(50)
       Buzzer_pwm.ChangeFrequency(4)
    else:
       pass


if __name__ == "__main__":
   #eeprom.populate_mock_scores()
    try:
        # Call setup function
        setup()
       # eeprom.clear(16)
        welcome()
        while True:
            menu()
            pass
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()
