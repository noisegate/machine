import glob
import fbpy.fb as fb
import time
import gcodeparser.gcodeparser as gcode
import mill.interface as interface
import curses
import curses.textpad
import os
import data
try:
    import pololu.pololu as pololu
    POLOLU_AVAILABLE = True
except ImportError:
    print "WARNING, NO HARDWARE SUPPORT, ONLY SIMULATION. press enter to continue"
    s=raw_input()
    POLOLU_AVAILABLE = False

class Dummypololu(object):

    def __init__(self):
        pass

    def enable(self):
        pass

    def disable(self):
        pass

    def stepsleft(self,x):
        pass

    def stepsright(self,y):
        pass

class Simpololu(object):

    def __init__(self):
        self.X = 0.0

    def stepsleft(self, x):
        self.X -=x        

    def stepsright(self,x):
        self.X +=x

class Mysim(gcode.Simulator):

    def __init__(self, surf, interfaceself):
        self.interfaceself = interfaceself
        self.X=0
        self.Y=0
        params = data.Calibrate()
        params.getdata()
        self.stepspermmX = params.stepspermmx
        self.stepspermmY = params.stepspermmy  
        self.sleepx = params.speedx
        self.sleepy = params.speedy
        self.lastx=0
        self.lasty=0
        self.hystx=params.hysteresisx 
        self.hysty=params.hysteresisy 
        gcode.Simulator.__init__(self, surf)
        self.aanslagy=0
        self.aanslagx=0
        
        if (POLOLU_AVAILABLE):
            self.ydriver = pololu.Pololu(pololu.Pins(enable=22, direction=17, step=27))
            self.xdriver = pololu.Pololu(pololu.Pins(enable=25, direction=23, step=24))
            self.xdriver.disable()
            self.ydriver.disable()
            self.ydriver.speed=260
            self.xdriver.speed=260
        else:
            self.ydriver = Dummypololu()
            self.xdriver = Dummypololu()
        self.simxdriver = Simpololu()
        self.simydriver = Simpololu()

    def raisedrill(self):
        self.surf.pixelstyle.color = self.color1
        self.interfaceself.drillmessage("raise mill and press space to continue...")

    def lowerdrill(self):
        self.surf.pixelstyle.color = self.color2
        self.interfaceself.drillmessage("lower mill and press space to continue...") 

    def simfinished(self):
        self.interfaceself.drillmessage("Simulation finished, press space to continue") 

    def pause(self):
        self.interfaceself.ifpause()

    def movex(self, dx, x, mode):
        #self.interfaceself.drillmovemessage("move x")
        self.xdriver.enable() 
        self.X+=dx
        self.interfaceself.updatedata("none", self.X, self.Y)
        if (dx>0):
            if (self.lastx == -1):
                if (mode==1): self.xdriver.stepsright(self.stepspermmX*self.hystx)
                self.simxdriver.stepsleft(self.hystx)
                self.aanslagx = 0
            if (mode==1): self.xdriver.stepsright(self.stepspermmX*dx)
            self.aanslagx-=dx
            if (self.aanslagx<0): self.simxdriver.stepsright(dx)
            self.lastx=1    
        if(dx<0):
            if (self.lastx == 1):
                if (mode==1): self.xdriver.stepsleft(self.stepspermmX*self.hystx)
                self.simxdriver.stepsright(self.hystx)
                self.aanslagx= 0
            if (mode==1): self.xdriver.stepsleft(self.stepspermmX*-dx)
            self.aanslagx+=dx
            if (self.aanslagx<0): self.simxdriver.stepsleft(-dx)
            self.lastx=-1
        if (mode==0): self.surf.point((self.trafox(self.simxdriver.X/30.0), self.trafoy(self.simydriver.X/30.0)))    
        time.sleep(self.sleepx)
        self.xdriver.disable()
        

    def movey(self, dy, y, mode):
        #self.interfaceself.drillmovemessage("move y")
        self.ydriver.enable()
        self.Y+=dy
        self.interfaceself.updatedata("none", self.X, self.Y)
        if (dy>0):
            if (self.lasty == -1):
                if (mode==1): self.ydriver.stepsleft(self.stepspermmY*self.hysty)
                #self.simydriver.stepsright(self.hysty)
                self.aanslagy=0
            if (mode==1): self.ydriver.stepsleft(self.stepspermmY*dy)
            self.aanslagy-=dy
            if (self.aanslagy<0): self.simydriver.stepsleft(dy)
            self.lasty=1
        if (dy<0):
            if (self.lasty == 1):
                if (mode==1): self.ydriver.stepsright(self.stepspermmY*self.hysty)
                #self.simydriver.stepsleft(self.hysty)
                self.aanslagy=50
            if (mode==1): self.ydriver.stepsright(self.stepspermmY*-dy)
            self.aanslagy+=dy
            if (self.aanslagy<0): self.simydriver.stepsright(-dy)
            self.lasty=-1
        if (mode==0): self.surf.point((self.trafox(self.simxdriver.X/30.0), self.trafoy(self.simydriver.X/30.0)))    
        time.sleep(self.sleepy)
        self.ydriver.disable()


class Myinterface(interface.Interface):
    LEFTCOLUMN = 10

    menudata =  [
                    [10, LEFTCOLUMN, "MENU"],
                    [11, LEFTCOLUMN, "===="],
                    [12, LEFTCOLUMN, "q)      quit"],
                    [13, LEFTCOLUMN, "C)      start milling"],
                    [14, LEFTCOLUMN, "S)      simulate"],
                    [15, LEFTCOLUMN, "o)      set origin"],
                    [16, LEFTCOLUMN, "l)      load file"],
                    [17, LEFTCOLUMN, "c)      calibrate"],
                    [18, LEFTCOLUMN, "<space> pause/play"],
                    [19, LEFTCOLUMN, "i,j,k,m up/dn/lt/rt"],
                    [20, LEFTCOLUMN, "a,w,s,z move graph"],
                    [21, LEFTCOLUMN, "+, -, zoom graph"],
                    [22, LEFTCOLUMN, "Q) quit closing machine"],
                    [23, LEFTCOLUMN, "e) enable"],
                    [24, LEFTCOLUMN, "d) disable"]
                ]


    def __init__(self):
        self.surface = fb.Surface()
        self.surf = fb.Surface((800,200),(300,300))
        self.parser = gcode.Parse()
        self.sim = Mysim(self.surf, self)
        interface.Interface.__init__(self)

    def pause(self):
        go = 1
        while (go):
            c=self.screen.getch()
            if (c==ord(' ')): 
                go=0
            if (c==ord('q')):
                return -1
        return 0

    def ifpause(self):
        c=self.screen.getch()
        if (c==ord(' ')): 
            self.drillmessage("paused, space to continue")

    def resetorigin(self):
        pass

    def decrementx(self, n):
        self.sim.movex(-n,0, 1)       

    def decrementy(self,n):
        self.sim.movey(n,0 ,1)

    def incrementx(self,n):
        self.sim.movex(n, 0, 1)

    def incrementy(self,n):
        self.sim.movey(-n,0, 1)

    def dowhateverSis(self, mode):
        if (self.sim.geometries is None):
            return
        self.sim.draw()
        self.sim.sim(mode)

    def generichandler(self, arg):

        if (arg==ord('+')):
            self.sim.zoom +=0.01
            self.sim.draw()
        if (arg==ord('-')):
            self.sim.zoom -=0.01
            self.sim.draw()
        if (arg==ord('w')):
            self.sim.offsety +=0.01
            self.sim.draw()
        if (arg==ord('z')):
            self.sim.offsety -=0.01
            self.sim.draw()
        if (arg==ord('a')):
            self.sim.offsetx -=0.01
            self.sim.draw()
        if (arg==ord('s')):
            self.sim.offsetx +=0.01
            self.sim.draw()
        if (arg==ord('e')):
            self.screen.addstr(3,3,"ena")
            self.screen.refresh()
            self.sim.xdriver.enable()
            self.sim.ydriver.enable()
        if (arg==ord('d')):
            self.sim.xdriver.disable()
            self.sim.ydriver.disable()
        if (arg==ord('i')):
            self.decrementy(10)
        if (arg==ord('m')):
            self.incrementy(10)
        if (arg==ord('j')):
            self.decrementx(10)
        if (arg==ord('k')):
            self.incrementx(10)
        if (arg==ord('I')):
            self.decrementy(100)
        if (arg==ord('M')):
            self.incrementy(100)
        if (arg==ord('J')):
            self.decrementx(100)
        if (arg==ord('K')):
            self.incrementx(100)

        if (arg==ord('Q')):
            os.system('sudo shutdown -h now')

    def resetorigin(self):
        self.sim.X = 0
        self.sim.Y = 0

    def drillmessage(self, message):
        self.screen.addstr(int(0.8*self.height),self.LEFTCOLUMN, "Drill MSG:{0}".format(message))
        self.screen.refresh()
        self.pause()
        self.screen.addstr(int(0.8*self.height),self.LEFTCOLUMN,"                                                       ")
        self.screen.refresh()

    def drillmovemessage(self, message):
        self.screen.addstr(int(0.8*self.height),self.LEFTCOLUMN, "Drill MSG:{0}".format(message))
        self.screen.refresh()
        self.screen.addstr(int(0.8*self.height),self.LEFTCOLUMN,"                                                       ")
        self.screen.refresh()

    def loadfile(self):
        files=glob.glob("/dev/shm/cnc/*.ngc")
        self.parser.filename = files[0]
        self.parser.parse()
        self.sim.geometries = self.parser.geometries
        self.sim.draw()

    def calibrate(self):
        #work in progress...
        self.screen.keypad(1)
        win = curses.newwin(5, 60, 5, 10)
        tb = curses.textpad.Textbox(win)
        text = tb.edit()
        curses.beep()
        #ofzoo....
        self.sim.stepspermmX = int(text.encode('utf_8'))
                
    def handlerestkeypresses(self,c):
        if (c==ord('c')):
            #calibrate
            self.calibrate()
        elif(c==ord('h')):
            #hysteresis settings
            pass

if __name__ == '__main__':

    machineinterface = Myinterface()
    
    machineinterface.main()
    machineinterface.loop()
    machineinterface.quit()
#todo
