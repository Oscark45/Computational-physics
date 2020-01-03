# -*- coding: utf-8 -*-
# file_name.py
# Python 3.6

"""
Author:     Oscar Kaatranen
Created:    %28/12/2019$
Modified:   %(date)$ 

Description

In this physics problem two masses are connected by a string and are pulled upwards 
by 2 strings so that their velocities are constant. All the strings remain at constant
length.

The program calculates the tensions in the strings and makes an animation of the scenario.

"""

from vpython import *

posy = 250; Lcord = 250
W1 = 9.81 # N
W2 = 9.81 # N
s = 100
v = 2.0 # velocity

Lbox = 60; Wbox = 60; Hbox = 60 # mass box dimensions

scene = display(height = 700, width = 700, range = 380)
alt = curve(pos = [(-300, posy, 0), (300, posy, 0)])

string1 = cylinder(pos = vector(-s/2, 0, 0), axis = vector(s, 0, 0), \
                  color = color.yellow, radius = 2) # String connecting the masses

mass1 = box(pos = vector(-s/2, -Hbox/2, 0), length = Lbox, width = Wbox, height = Hbox, color = color.red)
mass2 = box(pos = vector(s/2, -Hbox/2, 0), length = Lbox, width = Wbox, height = Hbox, color = color.red)

arrow1 = arrow(pos = vector(-s/2, 0, 0), color = color.orange) # Tension cord 1
arrow2 = arrow(pos = vector(s/2, 0, 0), color = color.orange) # Tension cord 2

arrow1.axis = vector(0, Lcord, 0)
arrow2.axis = vector(0, Lcord, 0)

# Labels

Flabel1 = label(pos = vector(200, Lcord + 100, 0), text = 'Force', box = 0)
Ftext1 = label(pos = vector(200, Lcord + 50, 0), box = 0)
Flabel2 = label(pos = vector(-200, Lcord + 100, 0), text = 'Force', box = 0)
Ftext2 = label(pos = vector(-200, Lcord + 50, 0), box = 0)

angleLabel = label(pos = vector(0, Lcord + 100, 0), text = 'Angle (deg)', box = 0)
angleText = label(pos = vector(0, Lcord + 50, 0), box = 0)

for t in arange(0., 125.0 , 0.2):
    rate(50) # slow motion
    
    # Positions and angle
    x1 = 50 + v*t
    x2 = -50 - v*t
    theta = asin((x1 - 50)/Lcord)
    posMass = Lcord - Lcord*cos(theta)
    
    # Mass and string positions
    mass1.pos = vector(-s/2, -Hbox/2 + posMass, 0)
    mass2.pos = vector(s/2, -Hbox/2 + posMass, 0)
    string1.pos = vector(-s/2, posMass, 0)
    
    # Cord positions updates
    arrow1.pos = vector(-s/2, posMass, 0)
    arrow2.pos = vector(s/2, posMass, 0)

    # Cord direction updates
    arrow1.axis = vector(Lcord*sin(-theta), Lcord*cos(-theta), 0)
    arrow2.axis = vector(Lcord*sin(theta), Lcord*cos(theta), 0)
    
    # Label text updates
    force = W1/cos(theta)
    Ftext1.text = '%8.2f'%force
    Ftext2.text = '%8.2f'%force
    angleText.text = '%8.2f'%degrees(theta)
    
    
    
    
    
    




