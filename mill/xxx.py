import pololu.pololu as pololu
import wiringpi2 as wp
import time
import RPi.GPIO as GPIO
import gcoder

pinbase = 65
i2c_addr = 0x20

"""
 +-----+-----+---------+------+---+--B Plus--+---+------+---------+-----+-----+
 | BCM | wPi |   Name  | Mode | V | Physical | V | Mode | Name    | wPi | BCM |
 +-----+-----+---------+------+---+----++----+---+------+---------+-----+-----+
 |     |     |    3.3v |      |   |  1 || 2  |   |      | 5v      |     |     |
 |   2 |   8 |   SDA.1 | ALT0 | 1 |  3 || 4  |   |      | 5V      |     |     |
 |   3 |   9 |   SCL.1 | ALT0 | 1 |  5 || 6  |   |      | 0v      |     |     |
 |   4 |   7 | GPIO. 7 |   IN | 1 |  7 || 8  | 1 | ALT0 | TxD     | 15  | 14  |
 |     |     |      0v |      |   |  9 || 10 | 0 | OUT  | RxD     | 16  | 15  |
 |  17 |   0 | GPIO. 0 |   IN | 0 | 11 || 12 | 0 | OUT  | GPIO. 1 | 1   | 18  |
 |  27 |   2 | GPIO. 2 |   IN | 0 | 13 || 14 |   |      | 0v      |     |     |
 |  22 |   3 | GPIO. 3 |  OUT | 0 | 15 || 16 | 0 | IN   | GPIO. 4 | 4   | 23  |
 |     |     |    3.3v |      |   | 17 || 18 | 0 | IN   | GPIO. 5 | 5   | 24  |
 |  10 |  12 |    MOSI |   IN | 0 | 19 || 20 |   |      | 0v      |     |     |
 |   9 |  13 |    MISO |   IN | 0 | 21 || 22 | 0 | IN   | GPIO. 6 | 6   | 25  |
 |  11 |  14 |    SCLK |  OUT | 0 | 23 || 24 | 1 | IN   | CE0     | 10  | 8   |
 |     |     |      0v |      |   | 25 || 26 | 1 | IN   | CE1     | 11  | 7   |
 |   0 |  30 |   SDA.0 |   IN | 1 | 27 || 28 | 1 | IN   | SCL.0   | 31  | 1   |
 |   5 |  21 | GPIO.21 |   IN | 1 | 29 || 30 |   |      | 0v      |     |     |
 |   6 |  22 | GPIO.22 |   IN | 1 | 31 || 32 | 0 | IN   | GPIO.26 | 26  | 12  |
 |  13 |  23 | GPIO.23 |  OUT | 0 | 33 || 34 |   |      | 0v      |     |     |
 |  19 |  24 | GPIO.24 |   IN | 1 | 35 || 36 | 0 | OUT  | GPIO.27 | 27  | 16  |
 |  26 |  25 | GPIO.25 |   IN | 0 | 37 || 38 | 0 | IN   | GPIO.28 | 28  | 20  |
 |     |     |      0v |      |   | 39 || 40 | 0 | IN   | GPIO.29 | 29  | 21  |
 +-----+-----+---------+------+---+----++----+---+------+---------+-----+-----+
 | BCM | wPi |   Name  | Mode | V | Physical | V | Mode | Name    | wPi | BCM |
 +-----+-----+---------+------+---+--B Plus--+---+------+---------+-----+-----+

"""

class Movements(object):

    UP    = 1
    RIGHT = 2
    DOWN  = 3
    LEFT  = 4
    NONE  = 0
    
    names = ['none','up','right','down','left']

class Controll(object):

    def __init__(self):
        # $U3 = X
        # $U4 = Y

        #dir connected to pin 11(BCM17), step to pin 13(BCM27), enable to pin 15(BCM22)
        self.y = pololu.Pololu(pololu.Pins(enable=22, direction=17,step=27))

        #dir connected to pin 16(BCM23), step to pin 18(BCM24), enable to pin 22(BCM25)
        self.x = pololu.Pololu(pololu.Pins(enable=25, direction=23,step=24))    
        self.x.speed = 120
        self.y.speed = 120

        self.xcoord = 0
        self.ycoord = 0

        self.Movement = Movements

        self.movement = Movements.NONE

        GPIO.setmode(GPIO.BCM)
        #GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        #GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        #GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        #GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        #interrupt
        GPIO.setup(19,GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(19, GPIO.FALLING, callback=self.callback) 
        
        self.i2c = wp.I2C()
        self.dev = self.i2c.setup(i2c_addr)
         
        wp.wiringPiSetup()
        wp.mcp23016Setup(pinbase, i2c_addr)

        self.state =0

        #wp.pinMode(19,0)
        #wp.pullUpDnControl(19,2)

        for i in range(65,73):
            wp.pinMode(i,1)
            wp.pullUpDnControl(i,2)

        for i in range(73,81):
            wp.pinMode(i,0)

        #wp.pinMode(65, 1)#pin 65 output
        #wp.digitalWrite(65, 1)#pin 65 high

    def callback(self, channel):
        state = self.i2c.readReg8(self.dev, 0x09)
        if (state == 0b11111110): 
            self.movement = Movements.RIGHT

        if (state == 0b11111101):
            self.movement = Movements.DOWN
        
        if (state == 0b11111011):
            self.movement = Movements.LEFT

        if (state == 0b11110111):
            self.movement = Movements.UP

        if (state == 0b11111111):
            self.movement = Movements.NONE

    def up(self):
        #print "moving up"
        self.x.stepsleft(1)

    def down(self):
        #print "moving down"
        self.x.stepsright(1)

    def left(self):
        self.y.stepsleft(1)

    def right(self):
        self.y.stepsright(1)
   
    def handler(self):
        if (self.movement == Movements.UP):
            self.ycoord+=1
            self.down()
        if (self.movement == Movements.DOWN):
            self.ycoord-=1
        if (self.movement == Movements.RIGHT):
            self.xcoord+=1
            self.right()
        if (self.movement == Movements.LEFT):
            self.xcoord-=1
            self.left()
   
    def load(self, filename):
        
        try:
            lines = open(filename,'r')
            for line in lines:
                if (line==[]):
                    pass
                elif (line[0:3]=="G21"):
                    print "working in mm"
                elif (line[0:3]=="G1"):
                    pass

        except:
            pass
            

if __name__ == '__main__':

    instance = Controll()


