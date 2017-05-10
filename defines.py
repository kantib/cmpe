# Define RPi-3 GPIO to LCD mapping
LCD_RS = 25
LCD_E  = 12
LCD_D4 = 5
LCD_D5 = 6
LCD_D6 = 13
LCD_D7 = 26

# Define some device constants
#LCD_WIDTH = 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False

# RPi - MCP3008 ADC pin mappings
# for SPI communication
CLK  = 11
MISO = 9
MOSI = 10
CS   = 8

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line

# Button Mapping
BUTTON_17 = 17
BUTTON_22 = 22
BUTTON_27 = 27

# Buzzer Mapping
BUZZER = 16

# Global variable declaration
Alarm_Set = False
Buzzer_Activated = False

Hour_Count = -1
Min_Count  = -1
Alarm_Hour = -1
Alarm_Min  = -1
Cur_Hour   = -1
Cur_Min    = -1

# Define some device constants
LCD_WIDTH = 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005
