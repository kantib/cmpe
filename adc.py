#!/usr/bin/env python
#
# Bitbang'd RPi- 3(40 pin) SPI interface with an MCP3008 ADC device
# MCP3008 is 8-channel 10-bit analog to digital converter
#  Connections are:
#     CLK => 11 (RPi's SCLK, GPIO11, pin 23)  
#     DOUT => 9 (chip's data out, RPi's MISO, GPIO 9, pin 21)
#     DIN => 10  (chip's data in, RPi's MOSI, GPIO 10, pin19) 
#     CS => 8 (chip's cs/SHDN, RPi's CE 0, GPIO 8, pin 24)

import RPi.GPIO as GPIO
import time
import sys
from defines import *

#CLK = 11
#MISO = 9
#MOSI = 10
#CS = 8

def setupSpiPins():
    ''' Set all pins as an output except MISO (Master Input, Slave Output)'''
    GPIO.setup(CLK, GPIO.OUT)
    GPIO.setup(MISO, GPIO.IN)
    GPIO.setup(MOSI, GPIO.OUT)
    GPIO.setup(CS, GPIO.OUT)
     

#def readAdc(channel, clkPin, misoPin, mosiPin, csPin):
def readAdc(channel):
    if (channel < 0) or (channel > 7):
        print "Invalid ADC Channel number, must be between [0,7]"
        return -1
        
    # Datasheet says chip select must be pulled high between conversions
    GPIO.output(CS, GPIO.HIGH)
    
    # Start the read with both clock and chip select low
    GPIO.output(CS, GPIO.LOW)
    GPIO.output(CLK, GPIO.HIGH)
    
    # read command is:
    # start bit = 1
    # single-ended comparison = 1 (vs. pseudo-differential)
    # channel num bit 2
    # channel num bit 1
    # channel num bit 0 (LSB)
    read_command = 0x18
    read_command |= channel
    
    sendBits(read_command, 5)
    
    adcValue = recvBits(12)
    
    # Set chip select high to end the read
    GPIO.output(CS, GPIO.HIGH)
  
    return adcValue
    
def sendBits(data, numBits):
    ''' Sends 1 Byte or less of data'''
    
    data <<= (8 - numBits)
    
    for bit in range(numBits):
        # Set RPi's output bit high or low depending on highest bit of data field
        if data & 0x80:
            GPIO.output(MOSI, GPIO.HIGH)
        else:
            GPIO.output(MOSI, GPIO.LOW)
        
        # Advance data to the next bit
        data <<= 1
        
        # Pulse the clock pin HIGH then immediately low
        GPIO.output(CLK, GPIO.HIGH)
        GPIO.output(CLK, GPIO.LOW)

def recvBits(numBits):
    '''Receives arbitrary number of bits'''
    retVal = 0
    
    for bit in range(numBits):
        # Pulse clock pin 
        GPIO.output(CLK, GPIO.HIGH)
        GPIO.output(CLK, GPIO.LOW)
        
        # Read 1 data bit in
        if GPIO.input(MISO):
            retVal |= 0x1
        
        # Advance input to next bit
        retVal <<= 1
    
    # Divide by two to drop the NULL bit
    return (retVal/2)
    

