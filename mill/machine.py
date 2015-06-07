import fbpy.fb as fb
import gcodeparser.gcodeparser as gcode
import mill.interface as interface

class Mysim(gcode.Simulator):

    def __init__(self, surf, interfaceself):
        self.interfaceself = interfaceself
        self.X=0
        self.Y=0
        gcode.Simulator.__init__(self, surf)

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

    def movey(self, dy):
        #self.interfaceself.drillmovemessage("move y")
        self.Y+=dy
        self.interfaceself.updatedata("none", self.X, self.Y)

class Myinterface(interface.Interface):

    def __init__(self):
        self.surface = fb.Surface()
        self.surf = fb.Surface((800,200),(300,300))
        self.parser = gcode.Parse()
        self.sim = Mysim(self.surf, self)
        Interface.__init__(self)

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
            print "OOPS"
            return
        #self.sim.draw()
        #self.sim.sim(mode)

    def generichandler(self, arg):

        if (arg=='+'):
            self.sim.zoom +=0.1
            self.sim.draw()
        if (arg=='-'):
            self.sim.zoom -=0.1
            self.sim.draw()
        if (arg=='w'):
            self.sim.offset =0.0
            self.sim.draw()
        if (arg=='z'):
            self.sim.offset =0.5
            self.sim.draw()
 

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
        self.parser.filename = "spacer.ngc"
        self.parser.parse()
        self.sim.geometries = self.parser.geometries
        self.sim.draw()

if __name__ == '__main__':

    machineinterface =Myinterface()
    
    machineinterface.main()
    machineinterface.loop()
    machineinterface.quit()

