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
        self.enablex = kwargs['enablex']
        self.directionx = kwargs['directionx']
        self.stepx = kwargs['stepx']
        self.enabley = kwargs['enabley']
        self.directiony = kwargs['directiony']
        self.stepy = kwargs['stepy']

class Pololu(object):

    """
        instance = Pololu(Pins(enable=<pinnr>, direction=<pinnr>, step=<pinnr>))

        instance.speed = 60# RPM

        instance.stepsleft(400)#400 left &c
    """

    def __init__(self, pins):
        gpio.setmode(gpio.BCM)

        self.hasx = False
        self.hasy = False

        if (pins.enablex and pins.directionx and pins.stepx):
    	    gpio.setup(pins.enablex, gpio.OUT)
            gpio.setup(pins.directionx,gpio.OUT)
            gpio.setup(pins.stepx,gpio.OUT)
            gpio.output(pins.directionx,gpio.LOW)
            self.hasx = True

        if (pins.enabley and pins.directiony and pins.stepy):
    	    gpio.setup(pins.enabley, gpio.OUT)
            gpio.setup(pins.directiony,gpio.OUT)
            gpio.setup(pins.stepy,gpio.OUT)
            gpio.output(pins.directiony,gpio.LOW)
            self.hasy = True

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
        if (self.hasx):
            gpio.output(self.pins.enablex, gpio.LOW)	
        if (self.hasy):
            gpio.output(self.pins.enabley, gpio.LOW)	

    def disable(self):
        if (self.hasx):
            gpio.output(self.pins.enablex, gpio.HIGH)
        if (self.hasy):
            gpio.output(self.pins.enabley, gpio.HIGH)

    def step(self, pins):
        gpio.output(pins, gpio.HIGH)
        time.sleep(Timeunits.us*25)
        gpio.output(pins, gpio.LOW)
        time.sleep(self.stepdelay)

    def steps(self, directions):
        if (directions[0]<0):
            gpio.output(self.pins.directionx, gpio.LOW)
        if (directions[0]>0): 
            gpio.output(self.pins.directionx, gpio.HIGH)        
        if (directions[1]<0): 
            gpio.output(self.pins.directiony, gpio.LOW)
        if (directions[1]>0): 
            gpio.output(self.pins.directiony, gpio.HIGH)        
       
        directions = [abs(directions[0]),abs(directions[1])]

        #greatest common
        #cases:
        #dx, dy nonzero
        if (directions[0]==0 and directions[1]!=0):
            for i in range(directions[1]):
                self.step([self.pins.stepy])
        elif (directions[0]!=0 and directions[1]==0):
            for i in range(directions[0]):
                self.step([self.pins.stepx])
        else:
           #eg dx = 3 and dy = 2 then there will be 2 simultaneous
           #steps. we want to exploit that, so first we do those.
           #min(dx,dy) = dy = 2
           #max(dx,dy) = dx = 3, 3-2 = 1 left to do on its own.
 
           gcd = min(directions)

           for i in range(gcd):
               self.step([self.pins.stepx, self.pins.stepy])

           leftover = directions[0]-directions[1]

           if (leftover>0):
               #dx
               whichisit=self.pins.stepx
           if (leftover<0):
               leftover *= -1
               whichisit=self.pins.stepy
           
           if (leftover>0):
               for i in range(leftover):
                   self.step([whichisit])

    def stepsleft(self, n):
        pass

    def stepsright(self,n):
        pass

if __name__ == "__main__":
   
    #use your own pin defs here!
    #these are th t.l.i. shield TM settings

    instance = Pololu(Pins(enablex = 25, directionx=23, stepx=24, enabley=22, directiony=17,stepy=27))
    instance.speed = 40*1

    instance.enable()

    instance.steps([-200,0])#
    instance.steps([+200,0])
    instance.steps([0,-200])
    instance.steps([0,200])
    
    instance.steps([-200,-200])
    instance.steps([200,200])
    instance.steps([200,-200])
    instance.steps([-200,200])

    instance.disable()
