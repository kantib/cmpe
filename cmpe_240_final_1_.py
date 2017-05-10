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

LINE1 = ""
LINE2 = ""
CURSOR = -1
DISPLAY_3_TIMEOUT = 0


def get_time():
    global Cur_Hour, Cur_Min
    now = datetime.datetime.now()
    Cur_Hour = now.hour
    Cur_Min = now.minute
    return now.strftime('%H:%M')

def get_temp():
    val = adc.readAdc(T_CHANNEL)
    #print "value from ADC: ", val

    #print "ADC Result: ", str(val)
    millivolts = val * (3300.0 / 1024.0)
    #print str(millivolts)
    # 10 mv per degree
    temp_C = ((millivolts - 100.0) / 10.0) - 40.0
    #print "degree celcius = ", temp_C

    # convert celcius to Fahrenheit
    temp_F = (temp_C * (9.0 /5.0)) + 32
    #print "degree Fahrenheit = ", temp_F

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


def clear_counters():
    global Alarm_Set, Alarm_Hour, Alarm_Min
    global Hour_Count, Min_Count
    global Buzzer_Activated

    Alarm_Set = False
    Alarm_Hour = -1
    Alarm_Min = -1
    Hour_Count = -1
    Min_Count = -1

    if(Buzzer_Activated):
        Buzzer_Activated = False
        GPIO.output(BUZZER, GPIO.LOW)


def get_display_1_lines():

    cur_time = get_time()
    cur_temp = get_temp()

    line1=" %-7s%-3sF" % (str(cur_time), str(cur_temp))
    line2="    Set Alarm"
    
    return (line1, line2)

def get_display_2_lines(hr, mn):
    line1="HR:MIN"
    line2=" %02d:%02d    Set" % (hr, mn)
    return (line1, line2)

def get_display_3_lines():
    global Alarm_Hour, Alarm_Min
    line1=" Alarm Set At:"
    line2=" %02d:%02d" % (Alarm_Hour, Alarm_Min)
    return (line1, line2)

def update_display(line1, line2, cur_pos=-1):
    # clear display
    LCD.lcd_byte(0x01, LCD_CMD)
    LCD.lcd_byte(0x01, LCD_CMD)
    time.sleep(E_DELAY)

    LCD.lcd_string(line1, LCD_LINE_1 + 1)
    
    LCD.lcd_string(line2, LCD_LINE_2 + 1)

    if cur_pos >= 0:
        LCD.lcd_byte(cur_pos, LCD_CMD)
        LCD.lcd_byte(0x0F, LCD_CMD)

# Threaded callback definition for push button 1
def button_22_pressed(channel):
    global CONTEXT, LINE1, LINE2, CURSOR
    global Hour_Count, Min_Count
    
    print "Context was ", CONTEXT
    if(CONTEXT == 1):
        CONTEXT = 2
        print " Change to ", CONTEXT

        clear_counters()

        cur_time = get_time()
        str_Hour_Count,str_Min_Count = cur_time.split(':')
        Hour_Count = int(str_Hour_Count)
        Min_Count = int(str_Min_Count)

        CURSOR=LCD_LINE_2+2
        LINE1, LINE2 = get_display_2_lines(Hour_Count, Min_Count)

    elif(CONTEXT == 2):
        CONTEXT = 1
        # clear all counters
        clear_counters()

        CURSOR=-1
        LINE1, LINE2 = get_display_1_lines()


# Threaded callback definition for push button 2
def button_17_pressed(channel):
    global CONTEXT, Hour_Count,Min_Count
    global Alarm_Set, Alarm_Hour, Alarm_Min
    global Buzzer_Activated
    global LINE1, LINE2, CURSOR, DISPLAY_3_TIMEOUT

    print "17 - Context = ", CONTEXT

    if(CONTEXT == 1):    # reset alarm if CONTEXT 1.
        clear_counters()

    elif(CONTEXT == 2):   # set the alarm in CONTEXT 2
        if Alarm_Hour == -1:
            Alarm_Hour = Hour_Count
            CURSOR = LCD_LINE_2 + 5
            LINE1, LINE2 = get_display_2_lines(Hour_Count, Min_Count)
        else:
            Alarm_Min = Min_Count
            CURSOR=-1
            CONTEXT=3
            DISPLAY_3_TIMEOUT = 5
            Alarm_Set = True
            LINE1, LINE2 = get_display_3_lines()


def button_27_pressed(channel):
    global CONTEXT, Hour_Count,Min_Count
    global Alarm_Set, Alarm_Hour, Alarm_Min
    global Buzzer_Activated, LINE1, LINE2

    if(CONTEXT == 2):
        if Alarm_Hour == -1:
            Hour_Count += 1
            if Hour_Count == 24:
                Hour_Count = 0
            LINE1, LINE2 = get_display_2_lines(Hour_Count, Min_Count)
        else:
            Min_Count += 1
            if Min_Count == 60:
                Min_Count = 0
            LINE1, LINE2 = get_display_2_lines(Hour_Count, Min_Count)


def check_and_fire_alarm():
    global Alarm_Hour, Alarm_Min, Alarm_Set, Buzzer_Activated
    if Alarm_Set:
        cur_time = get_time()
        str_Hour_Count,str_Min_Count = cur_time.split(':')
        hr = int(str_Hour_Count)
        mn = int(str_Min_Count)

        if hr == Alarm_Hour and mn == Alarm_Min:
            Buzzer_Activated = True
            GPIO.output(BUZZER, GPIO.HIGH)
        

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

def print_values():
    global LINE1, LINE2, CURSOR, CONTEXT, DISPLAY_3_TIMEOUT
    global Alarm_Hour, Alarm_Min, Alarm_Set, Cur_Hour, Cur_Min
    print "CONTEXT: {c}".format(c=CONTEXT)
    print "Alarm_Hour: {h}, Alarm_Min: {m}, Alarm_Set: {s}".format(
            h=Alarm_Hour, m=Alarm_Min, s=Alarm_Set)
    print "Cur_Hour: {h}, Cur_Min: {m}".format(h=Cur_Hour, m=Cur_Min)

# main
def main():
    
    global LINE1, LINE2, CURSOR, CONTEXT, DISPLAY_3_TIMEOUT
    # component setup
    setup()

    # Initialise LCD
    LCD.lcd_init()

    LINE1, LINE2 = get_display_1_lines()

    while True:
        print_values()
        check_and_fire_alarm()
        update_display(LINE1, LINE2, CURSOR)
        time.sleep(1)
        if CONTEXT == 1:
            LINE1, LINE2 = get_display_1_lines()
            
        elif CONTEXT == 3:
            DISPLAY_3_TIMEOUT -= 2
            if DISPLAY_3_TIMEOUT <= 0:
                CONTEXT = 1
                LINE1, LINE2 = get_display_1_lines()


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
