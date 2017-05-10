#!/usr/bin/python

#imports
import RPi.GPIO as GPIO
import time
import datetime
import adc
import LCD
from defines import *

# LCD contexts:
# 1 : Time & Temp Display
# 2 : Alarm set Display
# 3 : Alarm set Message Display
CONTEXT = 1

# ADC channel for temperature sensor
T_CHANNEL = 0

# Threaded callback definition for push button 1
def button_22_pressed(channel):
    global CONTEXT
    
    print "Context was ", CONTEXT
    if(CONTEXT == 1):
        CONTEXT = 2
        print " Change to ", CONTEXT

        # display alarm input screen
        show_display_2()

    elif(CONTEXT == 2):
        CONTEXT = 1
        print " changed to ", CONTEXT
        show_display_1()


# Threaded callback definition for push button 2
def button_17_pressed(channel):
    global CONTEXT, Hour_Count,Min_Count
    global Alarm_Set, Alarm_Hour, Alarm_Min
    global Buzzer_Activated

    print "17 - Context = ", CONTEXT

    if(CONTEXT == 1):    # reset alarm if CONTEXT 1.
        Alarm_Set = False
        Alarm_Hour = -1
        Alarm_Min = -1
        if(Buzzer_Activated):
            Buzzer_Activated = False
            GPIO.output(BUZZER, GPIO.LOW)

    elif(CONTEXT == 2):   # set the alarm in CONTEXT 2
        if(Hour_Count == -1):
            c_time = get_time()
            str_Hour_Count,str_Min_Count = c_time.split(':')
            Hour_Count = int(str_Hour_Count)
            Min_Count = int(str_Min_Count)

        if(Alarm_Hour == -1):
            Alarm_Hour = Hour_Count
            # keep cursor blinking at alarm hour input
            # to indicate use is not done with setting
            # up the Alarm hour. User will confirm 
            # Alarm hour with button 17 press. 
            LCD.lcd_byte(LCD_LINE_2 + 4, LCD_CMD)
            LCD.lcd_byte(0x0F, LCD_CMD)

        elif(Alarm_Min == -1):
            Alarm_Min = Min_Count
            Alarm_Set = True
            CONTEXT = 3
            print "changed to ", CONTEXT
            show_alarm_msg()

            # wait for 3 seconds
            time.sleep(3)
            CONTEXT = 1


def button_27_pressed(channel):
    global CONTEXT, Hour_Count,Min_Count
    global Alarm_Set, Alarm_Hour, Alarm_Min
    global Buzzer_Activated

    if(CONTEXT == 2):
        # This is a counter button.
        # when this button is pressed make sure 
        # you still blink the cursor at the same
        # position where hour/minutes is enteredi.

        # current time (Hour:min) is being displayed 
        # when this button pressed. So fetch that hour 
        # and min value and start incrementing from that
        # value and display the incremented value on
        # the LCD each time this button 27 is pressed.
        #done = False
        if (Hour_Count == -1):
            c_time = get_time()
            str_Hour_Count,str_Min_Count = c_time.split(':')
            Hour_Count = int(str_Hour_Count)
            Min_Count = int(str_Min_Count)

        if(Alarm_Hour == -1):
            Hour_Count += 1
            if(Hour_Count == 24):
                Hour_Count = 0
            if(Hour_Count < 10):
                LCD.lcd_string("0", LCD_LINE_2 + 1)
                LCD.lcd_string(str(Hour_Count), LCD_LINE_2 + 2)
                LCD.lcd_string(":", LCD_LINE_2 + 3)
                if(Min_Count < 10):
                    LCD.lcd_string("0",LCD_LINE_2 + 4)
                    LCD.lcd_string(str(Min_Count), LCD_LINE_2 + 5)
                else:
                    LCD.lcd_string(str(Min_Count), LCD_LINE_2 + 4)

                LCD.lcd_string("set", LCD_LINE_2 + 11)
            else:
                LCD.lcd_string(str(Hour_Count), LCD_LINE_2 +1)
                LCD.lcd_string(":", LCD_LINE_2 + 3)
                if(Min_Count < 10):
                    LCD.lcd_string("0",LCD_LINE_2 + 4)
                    LCD.lcd_string(str(Min_Count), LCD_LINE_2 + 5)
                else:
                    LCD.lcd_string(str(Min_Count), LCD_LINE_2 + 4)

                LCD.lcd_string("set", LCD_LINE_2 + 11)

            # keep cursor blinking at alarm hour input
            # to indicate use is not done with setting
            # up the Alarm hour. User will confirm 
            # Alarm hour with button 17 press. 
            LCD.lcd_byte(LCD_LINE_2 + 1, LCD_CMD)
            LCD.lcd_byte(0x0F, LCD_CMD)
            
        elif(Alarm_Min == -1):
            Min_Count += 1
            if(Min_Count == 59):
                Min_Count = 0
            #first show locked in value of alarm hour on the LCD
            if(Alarm_Hour < 10):
                LCD.lcd_string("0", LCD_LINE_2 + 1)
                LCD.lcd_string(str(Alarm_Hour), LCD_LINE_2 + 2)
                LCD.lcd_string(":", LCD_LINE_2 + 3)
                if(Min_Count < 10):
                    LCD.lcd_string("0", LCD_LINE_2 + 4)
                    LCD.lcd_string(str(Min_Count), LCD_LINE_2 + 5)
                else:
                    LCD.lcd_string(str(Min_Count), LCD_LINE_2 + 4)
            else:
                LCD.lcd_string(str(Alarm_Hour), LCD_LINE_2 + 1)
                LCD.lcd_string(":", LCD_LINE_2 + 3)

                if(Min_Count < 10):
                    LCD.lcd_string("0", LCD_LINE_2 + 4)
                    LCD.lcd_string(str(Min_Count), LCD_LINE_2 + 5)
                else:
                    LCD.lcd_string(str(Min_Count), LCD_LINE_2 + 4)
            LCD.lcd_string("set", LCD_LINE_2 + 11)

            # keep cursor blinking at alarm minute input
            # to indicate use is not done with setting
            # up the Alarm minutes. User will confirm 
            # Alarm minutes with button 17 press. 
            LCD.lcd_byte(LCD_LINE_2 + 4, LCD_CMD)
            LCD.lcd_byte(0x0F, LCD_CMD)


def show_display_1(): 
    global Cur_Hour, Cur_Min
    global Alarm_Set, Alarm_Hour, Alarm_Min
    global Buzzer_Activated

    ttime = get_time()
    temp  = get_temp()

    # clear display
    LCD.lcd_byte(0x01, LCD_CMD)
    LCD.lcd_byte(0x01, LCD_CMD)
    time.sleep(E_DELAY)
    
    # display time & temperature on the screen
    LCD.lcd_string(str(ttime), LCD_LINE_1 + 1)
    LCD.lcd_string(str(temp), LCD_LINE_1 + 9)
    LCD.lcd_string("F", LCD_LINE_1 + 12)
    LCD.lcd_string("Set Alarm >", LCD_LINE_2 + 5)
    
    #time.sleep(3)

    # activate buzzer if alarm
    # is set for current time
    print "---------------------"
    print "Alarm set = ", Alarm_Set
    print "Alarm Hour = ", Alarm_Hour
    print "Alarm Min = ", Alarm_Min
    print "Cur_Hour = ", Cur_Hour
    print "Cur_Min = ", Cur_Min
    print "---------------------"

    if(Alarm_Set == True):
        
        if(Cur_Hour == Alarm_Hour):
            if(Cur_Min == Alarm_Min):
                Buzzer_Activated = True
                GPIO.output(BUZZER, GPIO.HIGH)


def show_display_2():
    # clear display
    LCD.lcd_byte(0x01, LCD_CMD)
    LCD.lcd_byte(0x01, LCD_CMD)
    time.sleep(E_DELAY)

    LCD.lcd_string("HR:MIN", LCD_LINE_1 + 1)
    ltime = get_time()
    LCD.lcd_string(str(ltime), LCD_LINE_2 + 1)

    LCD.lcd_string("set" , LCD_LINE_2 + 11)
    LCD.lcd_byte(LCD_LINE_2 + 1, LCD_CMD)
    LCD.lcd_byte(0x0F, LCD_CMD)

def show_alarm_msg():
    LCD.lcd_byte(0x01, LCD_CMD)
    LCD.lcd_byte(0x01, LCD_CMD)
    time.sleep(E_DELAY)

    LCD.lcd_string("Alarm set at:", LCD_LINE_1 + 2)
    LCD.lcd_string(str(Alarm_Hour), LCD_LINE_2 + 1)
    LCD.lcd_string(":", LCD_LINE_2 + 3)
    LCD.lcd_string(str(Alarm_Min), LCD_LINE_2 + 4)

def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers

    # LCD setup
    LCD.setupLcdPins()

    # SPI setup
    adc.setupSpiPins()

    # push buttons setup
    # GPIO 22, 17 & 27 are set up as inputs.  All pulled up.  
    GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)  
    GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP) 

    # Buzzer setup 
    GPIO.setup(BUZZER, GPIO.OUT)

    # ISR Declaration for Push Buttons
    GPIO.add_event_detect(17, GPIO.FALLING, callback = button_17_pressed, bouncetime = 500)
    GPIO.add_event_detect(22, GPIO.FALLING, callback = button_22_pressed, bouncetime = 500)
    GPIO.add_event_detect(27, GPIO.FALLING, callback = button_27_pressed, bouncetime = 500)

# main
def main():
    
    # component setup
    setup()

    # Initialise LCD
    LCD.lcd_init()

    while True:
        if(CONTEXT == 1):
            show_display_1()
            time.sleep(2)
        time.sleep(2)
                    

def get_time():
    global Cur_Hour, Cur_Min
    now = datetime.datetime.now()
    Cur_Hour = now.hour
    Cur_Min = now.minute
    return now.strftime('%H:%M')

def get_temp():
        
        val = adc.readAdc(T_CHANNEL)
        print "value from ADC: ", val

        #print "ADC Result: ", str(val)
        millivolts = val * (3300.0 / 1024.0)
        #print str(millivolts)
        # 10 mv per degree
        temp_C = ((millivolts - 100.0) / 10.0) - 40.0
        print "degree celcius = ", temp_C

        # convert celcius to Fahrenheit
        temp_F = (temp_C * (9.0 /5.0)) + 32
        print "degree Fahrenheit = ", temp_F

        # remove decimal point from millivolts
        #millivolts = "%d" % millivolts
        #print str(millivolts)

        # save only decimal place for temperature and vltage readings
        temp_C = "%.1f" % temp_C
        temp_F = "%.1f" % temp_F

        #print Temp in celcius and Fahrenheit
        #print "Temp = ", str(temp_C), " Celcius" 
        #print "Temp = ", str(temp_F), " Fahrenheit"
        
        return temp_C
 

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        LCD.lcd_byte(0x01, LCD_CMD)
        LCD.lcd_byte(0x01, LCD_CMD)
        LCD.lcd_string("Goodbye", LCD_LINE_1)
        GPIO.cleanup()
