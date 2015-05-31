# machine
raspberry pi cnc machine controller

Started this project to convert my Sieg micro milling machine 
to a cnc machine. The idea was to use a raspberry pi as 
the controller, using its GPIO, so no (8bits) microcontroller involved.

A full pc interface was one of the goals, with graphical monitoring 
of the gcode execution as to make debugging easy ;) and a keyboard
for editing parameters (hysteresis, steps per mm and so forth)

work in progress...
## dependencies
download and install the following packages:

> git clone https://github.com/noisegate/machine.git

> git clone https://github.com/noisegate/fbpy.git

> git clone https://github.com/noisegate/gcodeparser.git

> git clone https://github.com/noisegate/pololu.git

> git clone https://github.com/noisegate/mill.git

