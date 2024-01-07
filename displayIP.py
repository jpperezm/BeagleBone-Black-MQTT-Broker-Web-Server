#!/usr/bin/python3

import smbus
import time
import subprocess

# device parameters
I2C_ADDR  = 0x27 # I2C device address
LCD_WIDTH = 16   # Maximum characters per line

# device constants
LCD_CHR = 1 # Mode - Will Send Data
LCD_CMD = 0 # Mode - Will Send Commands

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line

LCD_BACKLIGHT  = 0x08  # On
#LCD_BACKLIGHT = 0x00  # Off

ENABLE = 0b00000100 # Enable bit

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.005

#Open I2C interface
bus = smbus.SMBus(2) # Rev C Beaglebone Black uses 2

def lcd_init():
  try:
    # Initialise display
    lcd_byte(0x33,LCD_CMD) # 110011 Initialise
    lcd_byte(0x32,LCD_CMD) # 110010 Initialise
    lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
    lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off 
    lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
    lcd_byte(0x01,LCD_CMD) # 000001 Clear display
    time.sleep(E_DELAY)
  except IOError:
      print("Error: LCD no encontrado o error de comunicación")
      return False
  return True  

def lcd_byte(bits, mode):
  try:
    # Send byte to data pins
    # bits = the data
    # mode = 1 for data
    #        0 for command

    bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
    bits_low = mode | ((bits<<4) & 0xF0) | LCD_BACKLIGHT

    # High bits
    bus.write_byte(I2C_ADDR, bits_high)
    lcd_toggle_enable(bits_high)

    # Low bits
    bus.write_byte(I2C_ADDR, bits_low)
    lcd_toggle_enable(bits_low)
  except IOError:
      print("Error: LCD no encontrado o error de comunicación")
      return False
  return True

def lcd_toggle_enable(bits):
  try:
    # Toggle enable
    time.sleep(E_DELAY)
    bus.write_byte(I2C_ADDR, (bits | ENABLE))
    time.sleep(E_PULSE)
    bus.write_byte(I2C_ADDR,(bits & ~ENABLE))
    time.sleep(E_DELAY)
  except IOError:
      print("Error: LCD no encontrado o error de comunicación")
      return False
  return True

def lcd_string(message,line):
  # Send string to display
  message = message.ljust(LCD_WIDTH," ")
  lcd_byte(line, LCD_CMD)
  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)



def get_ip_address():
  try:
    ip_output = subprocess.check_output(['hostname', '-I'])
    ip_list = ip_output.decode('utf-8').strip().split()
    return ip_list[0] if ip_list else "No IP Found"
  except Exception as e:
    return "No IP Found"


def main():
  while True:
    if not lcd_init():
      time.sleep(30)
      continue

    ip = get_ip_address()
    lcd_byte(0x80, LCD_CMD)
    lcd_string("IP Address:", LCD_LINE_1)
    lcd_byte(0xC0, LCD_CMD)
    lcd_string(ip, LCD_LINE_2)
    time.sleep(10)


if __name__ == '__main__':

  try:
    main()
  except KeyboardInterrupt:
    pass
  finally:
    lcd_byte(0x01, LCD_CMD)