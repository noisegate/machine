import xml.dom.minidom
from xml.dom.minidom import Node

doc = xml.dom.minidom.parse("parameters.xml")

class Calibrate(object):

    def __init__(self):
        self.stepspermmx=0
        self.stepspermmy=0
        self.hysteresisx=0
        self.hysteresisy=0
        self.speedx=0
        self.speedy=0

    def gettext(self, nodelist):
        rc=[]
        for node in nodelist:
            if (node.nodeType==node.TEXT_NODE):
                rc.append(node.data)
        return ''.join(rc)

    def getdata(self):
        rc=[]
        for machine in doc.getElementsByTagName("machine"):
            for element in machine.getElementsByTagName("stepspermmx"):
                self.stepspermmx = int(self.gettext(element.childNodes))
            for element in machine.getElementsByTagName("stepspermmy"):
                self.stepspermmy = int(self.gettext(element.childNodes))
            for element in machine.getElementsByTagName("hysteresisx"):
                self.hysteresisx = int(self.gettext(element.childNodes))
            for element in machine.getElementsByTagName("hysteresisy"):
                self.hysteresisy = int(self.gettext(element.childNodes))
            for element in machine.getElementsByTagName("speedx"):
                self.speedx = float(self.gettext(element.childNodes))
            for element in machine.getElementsByTagName("speedy"):
                self.speedy = float(self.gettext(element.childNodes))
            for element in machine.getElementsByTagName("scale"):
                self.scale = float(self.gettext(element.childNodes))

if __name__ == "__main__":
    print Calibrate.getdata()
