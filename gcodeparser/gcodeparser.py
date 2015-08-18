"""
gpl2 by Noisegate aka Marcell Marosvolgyi
2015
borrowed a lot from pycodeviewer/ googlecode
development 0.1
"""

from string import *
from math import *
import os
import sys
import re
import fbpy.fb as fb
import time
import numpy

HUGE = 100000

class Point(object):
    scale = .718166     
    def __init__(self,x ,y ,z):
        self.x_ = x
        self.y_ = y
        self.z_ = z

    @property
    def x(self):
        return self.x_ * self.scale

    @x.setter
    def x(self, x_):
        self.x_ = x_

    @property
    def y(self):
        return self.y_ * self.scale

    @y.setter
    def y(self, y_):
        self.y_ = y_

    @property
    def z(self):
        return self.z_ * self.scale

    @z.setter
    def z(self, z_):
        self.z_ = z_

class Geom(object):
    pass

class Line(object):

    def __init__(self, point1, point2, speed, no, gcode):
        self.point1 = point1
        self.point2 = point2
        self.speed = speed
        self.no = no
        self.type = "line"
        self.gcode = gcode
        
class Arc(object):
    
    def __init__(self, point1, point2, center, speed, no):
        self.point1 = point1
        self.point2 = point2
        self.center = point3
        self.speed = speed
        self.no = no
        self.type = "arc"

class Geometries(object):

    def __init__(self):
        self.geometries = []
        self.maxx = 0
        self.maxy = 0
        self.minx = HUGE
        self.miny = HUGE
        self.lines = 0
        self.arcs = 0
        self.xtent = 0
        self.ytent = 0
        
    def add(self, geometry):
        self.geometries.append(geometry)

    def statistics(self):
        for i in self.geometries:
            x1=i.point1.x
            y1=i.point1.y
            x2=i.point2.x  
            y2=i.point2.y
            if (x1 > self.maxx):
                self.maxx = x1
            if (x2 > self.maxx):
                self.maxx = x2
            if (y1 > self.maxy):
                self.maxy = y1
            if (y2 > self.maxy):
                self.maxy = y2

            if (x1 < self.minx):
                self.minx = x1
            if (x2 < self.minx):
                self.minx = x2
            if (y1 < self.miny):
                self.miny = y1
            if (y2 < self.miny):
                self.miny = y2
            
            if isinstance(i, Line):
                self.lines +=1
            if isinstance(i, Arc):
                self.arcs +=1

            self.xtent = self.maxx - self.minx
            self.ytent = self.maxy - self.miny
            #print self.xtent
            #print self.ytent

class Simulator(object):
     
    def __init__(self, surf):
        self.geometries = None#geometries 
        self.surf = surf

        self.color1 = fb.Color(0,0,200,0)
        self.color2 = fb.Color(200,200,200,0)

        self.liftcallback = self.dummycallback
        self.lowercallback = self.dummycallback 

        self.zoom = 1.0
        self.offsetx = 0.5
        self.offsety = 0.5

        self.linecounter = 0
        self.SCALE = 100.0
        self.forward = True

        self.currentx0=0
        self.currentx1=0
        self.currenty0=0
        self.currenty1=0
        self.tictoc = 0
        self.state = "POLL"

    def redraw(self):
        self.surf.clear()
        self.surf.pixelstyle.color = fb.Color(250,250,250,0)
        self.surf.pixelstyle.style = fb.Styles.solid

        self.surf.pixelstyle.blur=1
        self.surf.pixelstyle.blurradius=2
        self.surf.pixelstyle.sigma=2
 
        self.surf.rect((0.0, 0.0),(1.0,1.0))

    def dummycallback(self):
        pass

    def trafox(self, x):
        return self.zoom*x/self.geometries.xtent/2+self.offsetx

    def trafoy(self, x):
        return self.zoom*x/self.geometries.xtent/2+self.offsety

    def draw(self):
        self.redraw()
        self.surf.pixelstyle.color = fb.Color(140,0,0,0)
        self.surf.pixelstyle.style = fb.Styles.dashed
        self.surf.pixelstyle.blur=0
        self.surf.pixelstyle.blurradius=2
        self.surf.pixelstyle.sigma=2
          
        for geometry in self.geometries.geometries :
            if isinstance(geometry, Line):
                self.surf.pixelstyle.color = fb.Color(140,0,0,0)

                self.surf.pixelstyle.style = fb.Styles.dashed
                self.surf.line( (self.trafox(geometry.point1.x), -self.trafoy(geometry.point1.y)), 
                                (self.trafox(geometry.point2.x), -self.trafoy(geometry.point2.y)))
                self.surf.pixelstyle.style = fb.Styles.solid
                self.surf.pixelstyle.color = fb.Color(140,140,140,0)

                self.surf.arc(  (self.trafox(geometry.point1.x), -self.trafoy(geometry.point1.y)),2,2,0,10,10)

        self.surf.update()     

    def raisedrill(self):
        pass

    def lowerdrill(self):
        pass

    def simfinished(self):
        pass

    def pause(self):
        return 1

    def talkback(self, gcstring):
        pass

    def movex(self, dx, x, mode):
        pass

    def movey(self, dy, y, mode):
        pass

    def movexyz(self, dx, dy, x, y, mode, rampup):
        #moves simultaneously (45 degs and 90)
        pass

    def interviolate(self, x0, x1, y0, y1, mode):
        #self.state = "Interviolating "
        #Bressenhemzzz
        dx = abs(x1-x0)
        if (x0<x1): 
            sx = 1
        else: 
            sx = -1
        dy = abs(y1-y0)
        if (y0<y1): 
            sy = 1
        else:
            sy=-1
        if (dx>dy): 
            err = int(dx/2.0)
        else: 
            err = int(-dy/2.0)

        go=1
    

        xi = x0
        yi = y0

        while(go):
            if (x0==x1 and y1==y0):
                self.tictoc = t1-t0
                return gosim#go=0
            t0 = time.time()
            #self.surf.point(
            #                (self.trafox(x0/self.SCALE), 
            #                -self.trafoy(y0/self.SCALE))
            #               )
            #go=0
            deltax = 0
            deltay = 0

            r1 = sqrt((xi-x0)**2 + (yi-y0)**2)
            r2 = sqrt((x1-x0)**2 + (y1-y0)**2)

            curve = (1.0 - exp(-r1/25)) * (1.0 - exp(-r2/25))

            e2 = err
            if (e2 > -dx):
                err -= dy
                x0 += sx
                deltax = sx
            if (e2 < dy):
                err += dx
                y0 += sy
                deltay=sy

            self.movexyz(deltax, deltay, x0/self.SCALE, y0/self.SCALE, mode, curve)
            #time.sleep(0.011)
            #self.surf.update()
            self.currentx0 = x0
            self.currenty0 = y0
            self.currentx1 = x1
            self.currenty1 = y1

            #gosim = self.pause()
            gosim=1
            if (gosim==0):
                go=0
            if (gosim==-1):
                go=0
                gosim=1
            t1 = time.time()

        gosim = self.pause()
        self.tictoc = t1-t0
        return gosim

    def sim(self, mode):
        oldz=0
        gosim=1
        #self.linecounter = 0
        maxlines = len(self.geometries.geometries)

        self.state = "Executing gcode"

        while((gosim==1) and (self.linecounter<maxlines)):
        #for geometry in self.geometries.geometries :
            
            geometry = self.geometries.geometries[self.linecounter]
            if isinstance(geometry, Line):
                #self.surf.line(self.trafo(geometry.point1), self.trafo(geometry.point2))
                
                if self.forward:
                    X0 = geometry.point1
                    X1 = geometry.point2
                else:
                    X1 = geometry.point1
                    X0 = geometry.point2

                x0 = int(X0.x*self.SCALE)
                x1 = int(X1.x*self.SCALE)
                y0 = int(X0.y*self.SCALE)
                y1 = int(X1.y*self.SCALE)
                if (X1.z > oldz):
                    self.raisedrill()
                    oldz = X1.z
                if (X1.z < oldz):
                    self.lowerdrill()
                    oldz = X1.z

                startline = self.linecounter-15
                endline = self.linecounter+15
                if startline<0: startline = 0
                if endline>len(self.geometries.geometries): endline = len(self.geometries.geometries)
                 
                self.talkback("".join(["{0} {1:>4}: {2}".format(
                                        ('>' if i==self.linecounter else '.'), 
                                        i, 
                                        self.geometries.geometries[i].gcode) for i in range(startline,endline)
                                       ]
                                     )
                             )            
    
                #bressenham's
                if ((x0 == x1) and (y0==y1)):
                    pass
                else:
                    gosim = self.interviolate(x0, x1, y0, y1, mode)

            gosim = self.pause()   
            self.surf.line(
                           (self.trafox(x0/self.SCALE),-self.trafoy(y0/self.SCALE)),
                           (self.trafox(x1/self.SCALE),-self.trafoy(y1/self.SCALE))
                           )
            self.surf.update()
            self.linecounter += 1
        self.simfinished()

class Parse(object):

     def __init__(self):
          self.filename = None
          self.geometries = None#Geometries()
          self.no_points = 0

     def parse(self):

          try:
               f = open(self.filename,'r')
          except IOError, (errno, strerror):
               error_dialog("Unable to open the file" + gcodes.name + "\n",1)
          else:

               self.geometries = Geometries()
               pre_x = 0.0
               pre_y = 0.0
               pre_z = 0.0
               x = pre_x
               y = pre_y
               z = pre_z
               s = 0
               l = 1
               style = 0

               while 1:
                    gcode = f.readline()
                    if not gcode:
                         break
                    flag = 0
                    #remove shit between parentheses (comments)
                    #http://stackoverflow.com/questions/640001/how-can-i-remove-text-within-parentheses-with-a-regex
                    gcode = re.sub(r'\([^)]*\)', '', gcode)
                    #parse g code
                    if (gcode[0]==';'):
                         gg=None
                         xx=None
                         yy=None
                         zz=None
                         ss=None
                    else:
                         gg = re.search("[gG]([\d]+)\D",gcode)
                         xx = re.search("[xX]([\d\.\-]+)\D",gcode)
                         yy = re.search("[yY]([\d\.\-]+)\D",gcode)
                         zz = re.search("[zZ]([\d\.\-]+)\D",gcode)
                         ss = re.search("[fF]([\d\.\-]+)\D",gcode)
                    if (gg):
                         style = int(gg.group(1))
                    if (xx):
                         x = float(xx.group(1))
                         flag = 1
                    if (yy):
                         y = float(yy.group(1))
                         flag = 1
                    if (zz):
                         z = float(zz.group(1))
                         flag = 1
                    if (ss):
                         s = float(ss.group(1))
                         #print "s: {0}".format(s)
                    if(style == 1 or style == 0 or style == 4):
                         #lines
                         if(flag):
                              point1 = Point(pre_x,pre_y,pre_z)
                              point2 = Point(x,y,z)
                              self.geometries.add(Line(point1, point2, s, l, gcode))
                              self.no_points+=1
                              #print "{0:<6} {1:<6}".format(x,y)
                    elif(style == 2 or style == 3):
                         #arcs
                              i=0
                              j=0
                              k=0
                              ii = re.search("[iI]([\d\.\-]+)\D",gcode)
                              jj = re.search("[jJ]([\d\.\-]+)\D",gcode)
                              kk = re.search("[kK]([\d\.\-]+)\D",gcode)
                              rr = re.search("[rR]([\d\.\-]+)\D",gcode)
                              if(ii):
                                   i = float(rr.group(1))
                              if(jj):
                                   j = float(rr.group(1))
                              if(kk):
                                   k = float(rr.group(1))
                              center = Point(i,j,k)
                              point1 = Point(pre_x,pre_y,pre_z)
                              point2 = Point(x,y,z)
                              if(style == 3):
                                   #swap
                                   tmp_point = point2
                                   point2 = point1
                                   point1 = point2
                              if(rr):
                                   r = float(rr.group(1))
                                   #c1,c2 = calc_center(point1,point2,r,plain)
                                   #center = c1
                                   #if(r < 0):
                                   #     center = c2
                                   pass
                              #patterns.append(ARC(style,l,s,plain,point1,point2,center))
                              self.no_points+=1
                              print "arc"
                    elif(style == 17):
                              plain = 0
                    elif(style == 18):
                              plain = 1
                    elif(style == 19):
                              plain = 2

                    pre_x = x
                    pre_y = y
                    pre_z = z					
                    l += 1
               f.close()
               self.geometries.statistics()

if __name__ == "__main__":
    main = fb.Surface()
    surf = fb.Surface((800,400),(400,400))

    parser = Parse()
    parser.filename = '/dev/shm/cnc/small-gear-1off.ngc'
    parser.parse()
    
    class Mysim(Simulator):

        def raisedrill(self):
            print "Please raise mill. Press enter to continue"
            self.surf.pixelstyle.color = self.color1
            s=raw_input()

        def lowerdrill(self):
            print "Please lower mill. Press enter to continue"
            self.surf.pixelstyle.color = self.color2
            s=raw_input()
    
        def movex(self, dx):
            pass

        def movey(self, dy):
            pass

    #sim = Mysim(parser.geometries, surf)
    
    #sim.draw()
    #sim.sim()

