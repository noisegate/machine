import glob
import fbpy.fb as fb
import gcodeparser.gcodeparser as gcode
import mill.interface as interface
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

    def stepsleft(self,x):
        pass

    def stepsright(self,y):
        pass

class Mysim(gcode.Simulator):

    def __init__(self, surf, interfaceself):
        self.interfaceself = interfaceself
        self.X=0
        self.Y=0
        gcode.Simulator.__init__(self, surf)
        if (POLOLU_AVAILABLE):
            self.ydriver = pololu.Pololu(pololu.Pins(enable=22, direction=17, step=27))
            self.xdriver = pololu.Pololu(pololu.Pins(enable=25, direction=23, step=24))
            self.ydriver.speed=60
            self.xdriver.speed=60
        else:
            self.ydriver = Dummypololu()
            self.xdriver = Dummypololu()

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

    def movex(self, dx):
        #self.interfaceself.drillmovemessage("move x")
        self.X+=dx
        self.interfaceself.updatedata("none", self.X, self.Y)
        if (dx>0):
            self.xdriver.stepsright(1)
        if (dx<0):
            self.xdriver.stepsleft(1)

    def movey(self, dy):
        #self.interfaceself.drillmovemessage("move y")
        self.Y+=dy
        self.interfaceself.updatedata("none", self.X, self.Y)
        if (dy>0):
            self.ydriver.stepsright(1)
        if (dy<0):
            self.ydriver.stepsleft(1)

class Myinterface(interface.Interface):
    LEFTCOLUMN = 10

    menudata =  [
                    [10, LEFTCOLUMN, "MENU"],
                    [11, LEFTCOLUMN, "===="],
                    [12, LEFTCOLUMN, "q)      quit"],
                    [13, LEFTCOLUMN, "c)      start milling"],
                    [14, LEFTCOLUMN, "s)      simulate"],
                    [15, LEFTCOLUMN, "o)      set origin"],
                    [16, LEFTCOLUMN, "l)      load file"],
                    [17, LEFTCOLUMN, "<space> pause/play"],
                    [18, LEFTCOLUMN, "i,j,k,m up/dn/lt/rt"],
                    [19, LEFTCOLUMN, "more stuff..."]
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

    def ifpause(self):
        c=self.screen.getch()
        if (c==ord(' ')): 
            self.drillmessage("paused, space to continue")

    def resetorigin(self):
        pass

    def decrementx(self):
        pass

    def decrementy(self):
        pass

    def incrementx(self):
        #print "move x"
        self.sim.movex(1)

    def incrementy(self):
        pass

    def dowhateverSis(self, mode):
        if (self.sim.geometries is None):
            return
        self.sim.draw()
        self.sim.sim(mode)

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

if __name__ == '__main__':

    machineinterface = Myinterface()
    
    machineinterface.main()
    machineinterface.loop()
    machineinterface.quit()

