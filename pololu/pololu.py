"""
    ==================================
    Pololu 4988 GPIO raspberry module
    ==================================

    by Noisegate (c) 2015
    aka Marcell Marosvolgyi

    Do What the Fuck You Want to Public License, WTFPL
    no, just kiddin' it is GPLv2
    
    I Think this test program has potential 4 becoming a
    simple library. Maybe one day...

    Use @ own risk. If you blow stuff, I didn't do it.

        If my code suxx and kills your hardware, I feel bad for ya,
        but I dont take responsibily. Please let me know though what
        happened, I might improve my code.


"""

import RPi.GPIO as gpio
import time

class Poshandler(object):

    """
        behavior depending on float or int pos parameter
    """

    def __init__(self, function):
        self.function = function

    def __call__(self, *args, **kwargs):
        if (isinstance(args[1], float)):
            args = tuple([args[0], int(args[1]/360.0 * 200)])
        else:
            args = tuple([args[0], int(args[1])])

        return self.function(*args, **kwargs)

    def __get__(self, instance, owner):
        def wrapper(*args, **kwargs):
            return self(instance, *args, **kwargs)
        return wrapper

class Timeunits(object):
    ms = 0.001
    us = 0.000001

class Pins(object):
    
    def __init__(self, *args, **kwargs):
        self.enable = kwargs['enable']
        self.direction = kwargs['direction']
        self.step = kwargs['step']

class Pololu(object):

    """
        instance = Pololu(Pins(enable=<pinnr>, direction=<pinnr>, step=<pinnr>))

        instance.speed = 60# RPM

        instance.stepsleft(400)#400 left &c
    """

    def __init__(self, pins):
        gpio.setmode(gpio.BCM)
    	gpio.setup(pins.enable,gpio.OUT)
        gpio.setup(pins.direction,gpio.OUT)
        gpio.setup(pins.step,gpio.OUT)
        gpio.output(pins.direction,gpio.LOW)

        self.currentangle = 0.0
        self.rpm=60
        self.stepdelay = 60.0/self.rpm/200.0
        self.pins = pins

    @property
    def speed(self):
        return self.rpm

    @speed.setter
    def speed(self, val):
        self.rpm = val
        self.stepdelay = 60.0/self.rpm/200.0
    
    def enable(self):
        gpio.output(self.pins.enable, gpio.LOW)	

    def disable(self):
        gpio.output(self.pins.enable, gpio.HIGH)

    def step(self):
        gpio.output(self.pins.step, gpio.HIGH)
        time.sleep(Timeunits.us*25)
        gpio.output(self.pins.step, gpio.LOW)

    def steps(self,n):
        for i in range(n):
            self.step()
            time.sleep(self.stepdelay)

    def stepsleft(self, n):
        self.enable()
        gpio.output(self.pins.direction, gpio.LOW)
        self.steps(n)
        self.disable()

    def stepsright(self,n):
        self.enable()
        gpio.output(self.pins.direction, gpio.HIGH)
        self.steps(n)
        self.disable()

    @Poshandler
    def goto(self, pos):

        diff = pos-self.currentangle
        
        if (diff<0):
            gpio.output(self.pins.direction, gpio.LOW)
            diff = -diff
        else:
            gpio.output(self.pins.direction, gpio.HIGH)

        self.steps(int(diff))

        self.currentangle = pos

    def resetposition(self):
        self.currentangle = 0

if __name__ == "__main__":
   
    #use your own pin defs here!
    #these are th t.l.i. shield TM settings
    instance = Pololu(Pins(enable = 25, direction=23, step=24))
    instance.speed = 60*1

    instance.stepsleft(400)
    instance.stepsright(400)

    instance.goto(200)
    instance.goto(100)
    instance.goto(0)
    
    print "I hope stepper is where it started..."
