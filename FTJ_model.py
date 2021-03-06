# -*- coding: utf-8 -*-
"""
Created on Thu Jun 24 09:12:21 2021

@author: okoscar

//Title: WKB Ferroelectric Tunneling Junction device simulation
//Version: 1.0
//Date: July 2020
//Language: VerilogA (translated to Python)


The following modules are intergrated

1.WKB approximation calculation of transmission and current 
2.Static coercive voltage calculation based on modified JKD semi-empirical scaling law.
3.Dynamic switching time calculation involving KAI model, Merz's law and creep process model.

-----------------------------------------------------------------------------------------------*/
`resetall
`include "constants.vams"
`include "disciplines.vams"

//self-defined Constants

/*----------Elementary charge---------------*/
`define qe 1.6e-19	
/*----------Boltzmann constant------------- */
`define kT  0.0259
/*----------Planck's constant------------- */
`define hbas 1.055e-34	
/*----------Electron mass------------- */
`define m 9.11e-31
/*----------Vacuum dielectric constant------------- */
`define epsi0 8.854e-12
/*----------Normalized screening length of the two terminals in meter------------- */
`define a12 0.165e-9
/*----------Characteristic field in V/m------------- */
`define E0 1.0e9


"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
plt.close('all')

#from decimal import *
#getcontext().prec = 50

# Self-defined constants
qe = 1.6e-19 # Elementary charge
kT = 0.0259 # Boltzmann constant
hbas = 1.055e-34 # Planck's constant (reduced)
m = 9.11e-31 # Electron mass
epsi0 = 8.854e-12 # Vacuum dielectric constant
a12 = 0.165e-9 # Normalized screening length of the two terminals in meter
E0 = 1.0e9 # Characteristic field in V/m


#----------T1,T2=real pins of the FTJ------------- */
#----------X=store the state of the FTJ, non-volatile way------------- */
#----------Ttrans=store the state of the FTJ with time delay, non-volatile way------------- */

# Input: T1, T2
# Output: x, Ttrans
    
#----------Initial state of the FTJ---------
Pol = -1 # from[-1:1]  exclude 0;  //-1+ = high resistance, 1 = low resistance
resistance = 1 # from[-1:1]  exclude 0;  //-1 = high resistance, 1 = low resistance
Dev_type = 0 # 0 for metal-FE-metal structure, 1 for GR-FE-metal structure

# ----------Parameter for calculating the static coercive voltage---------------*/
C_JKD = 1650 # Factor from JKD semi-empirical scaling law
Pr = 0.07 # Spontaneous polarization of BTO in F/m2
 
# ----------Attempt time of nucleation and growth in second---------------*/
tau_nuc0 = 2.8e-15
tau_grow0 = 2.25e-13
    
# ----------Creep energy barrier for nucleation and growth in electron-volt---------------*/
eps_n = 6.18e9
eps_g = 4.64e9
    
alpha = 0.26 # in F/m^2/V, graphene Cq constant in Gr-FE-M structure
Cm0 = 0.45 # in F/m^2, left metal contact capacitance in M-FE-M structure
Cm = 0.35 # in F/m^2, right metal contact capacitance
epsr = 10 # unitless, relative dielectric constant of the FE layer
    
mt = 0.5 # effective mass in transverse direction
ml = 0.95 # effective mass in vertical direction
Eb_1 = 1.4 # in eV, barrier height at grahene side(Ec_FE-Em_graphene)
Eb_2 = 1.0 # in eV, barrier height at metal-FE interface.
    
# ----------Surface radius in meter---------------
r = 250e-9
# ----------FE barrier thickness in meter---------------
t_fe = 4e-9
    
# Temperature 
T = 300
T0 = 300 # temperature constant
    

def F2D(x):
    return np.log(1+np.exp(-x/kT))

def FTJ(T1, T2, Pool):
    
    # Simulation
    Polstate=Pool
    Area = np.pi*r**2
    V = dict()
    I = dict()
    V[(T1, T2)] = T2-T1
    Vb = V[(T1,T2)]
    Cf = epsr*epsi0/t_fe # FE capacitance 
    beta = Cm/(Cm+Cf) # unitless, capacitance ratio  
    N2D = 2*mt*m*kT*qe/(2*np.pi*hbas**2) # in /m^2, 2D density
    Va = Vb
    Pp = Polstate*Pr-Cf*Va

    # Modified JKD semi-empirical scaling law
    Vc_lh = C_JKD*t_fe**(1/3)-a12*Pr/epsi0
    print("C_JKD:", C_JKD)
    print("a12:", a12)
    print("Pr:", Pr)
    print("epsi0:", epsi0)
    print()
    Vc_hl = - Vc_lh
    
    print("Area: ", Area)
    print("Cf:", Cf)
    print("beta:", beta)
    print("N2D:", N2D)
    print("Va:", Va)
    
    if Dev_type == 1: # If we are modeling the GR-FE-metal structure
        if Pp > 0:
            V1 = 1/alpha*(-Cf*beta*np.sqrt((Cf*beta)**2 + 2*alpha*beta*Pp))+Va
        else:
            V1 = -1/alpha*(-Cf*beta*np.sqrt((Cf*beta)**2 - 2*alpha*beta*Pp))+Va	
        Qg = 1/2*alpha*abs(Va-V1)*(Va-V1)
        V2 = -Polstate*Pr/(Cf+Cm)+(1-beta)*V1
        
    else: # Metal-FE-metal structure    
        V1 = (Cm0*Va + Polstate*Pr + Cf*Cm0/Cm*Va)/(Cm0 + Cf + Cf*Cm0/Cm)
        V2 = (Cf*Va - Polstate*Pr)/(Cm+Cf+Cf*Cm/Cm0)

    print("V1:", V1)
    print("V2:", V2)

    Ef1 = -Va
    Ef2 = 0
    
    Eb1 = -V1+Eb_1
    Eb2 = -V2+Eb_2
    
    print("Eb1:", Eb1)
    print("Eb2:", Eb2)
    
    ef=(Eb1-Eb2)/t_fe # electric field cross FE layer
    
    #print("V1:", V1)
    #print("V2:", V2)
    print("ef:", ef)
    
    Emin = min(min(0,Ef1),Ef2)-5*kT
    Emax = max(Eb1,Eb2)
    Tr = 0
    Tr2 = 0
    Ispec = 0
    G0=qe**2/2/np.pi/hbas
    print("G0:", G0)
    
    for i in range(1001):
        E = Emin +(Emax-Emin)/1000*i
        Tr = np.exp(-4*np.sqrt(2*ml*m*qe)/(3*hbas*abs(ef))*abs(np.maximum(Eb1-E,0)**1.5 - np.maximum(Eb2-E,0)**1.5))
        Tr2 = Tr2+Tr
        Ispec = Ispec - G0 * Tr*(F2D(E-Ef1)-F2D(E-Ef2))
        #print("Tr:", Tr)
        #print("Ispec:", Ispec)
        #break
    
    print("Ispec:", Ispec)
    # for loop "for (i = 0; i < 1001; i = i+1) begin"
    #int_array = np.arange(1001)
    #E = Emin+(Emax-Emin)/1000.0*int_array
    #Tr = np.exp(-4*np.sqrt(2*ml*m*qe))/(3*hbas*abs(ef))*abs(np.maximum(Eb1-E,0)**1.5 - np.maximum(Eb2-E,0)**1.5)
    #Tr2 = np.sum(Tr)
    #Ispec = -np.sum(G0 * Tr*(F2D(E-Ef1)-F2D(E-Ef2)))

    Id = Area*N2D * Ispec/1001.0*1000.0*(Emax-Emin)/1000.0
    Id2 = abs(Id)
    
    # Case 1: high resistance state
    if Polstate == -1:
        print("Pol -1, Comparison: Vb = {:.5f} and Vc_lh = {:.5f}".format(Vb, Vc_hl))
        if Vb <= Vc_hl: # case 1.1: switch toward LRS
            efa = abs(Vb)/t_fe
            # Merz's Law and creep process model
            taun = tau_nuc0*np.exp(eps_n*T0/(T*efa))
            taug = tau_grow0*np.exp(eps_g*T0/(T*efa))
            # Calculation delay from KAI model
            duration = taun+taug
            # Current used to store the state of the FTJ
            ix = 1 
            print("Change from low to high")
        else: # case 1.2: remain HRS
            ix = 0
            print("Stay in low state")
            
    # Case 2: low resistance state    
    if Polstate == 1:
        print("Pol 1, Comparison: Vb = {:.5f} and Vc_lh = {:.5f}".format(Vb, Vc_hl))
        if Vb >= Vc_lh:
            efa = abs(Vb)/t_fe
            # Merz's Law and creep process model
            taun = tau_nuc0*np.exp(eps_n*T0/(T*efa))
            taug = tau_grow0*np.exp(eps_g*T0/(T*efa))
            # Caculation delay from KAI model
            duration = taun+taug
            ix = 0
            print("Change from high to low")
        else:
            ix = 1
            print("Stay in high state")
       
    # Actualisation of the state of x
    #V[x] = ix

    Ttrans = 0
    # Ttrans has the same function as x but it includes the time delay
    V[Ttrans] = 1
    Polstate = (ix-0.5)*2;
    I[(T1, T2)] = 0
    
    print("Polarisation: ",Polstate)
    return Id2, Polstate
    
#a = FTJ(1,4)

N = 21
V1s = np.linspace(0.1,1.9,N-2)
V2s = np.flip(np.linspace(0.1,1.8,N-3))
V3s = -V1s
V4s = -V2s
drainI1, drainI2, drainI3, drainI4 = np.zeros(N-2), np.zeros(N-3), np.zeros(N-2), np.zeros(N-3)

polStates = np.zeros(4*N)

n = 0
for i in range(N-2):
    print()
    #drainI[i] = FTJ(twos[i], i)
    print("i:", i)
    if i==0:
        drainI1[i], pols = FTJ(V1s[i], 0, Pol)
    else:    
        drainI1[i], pols = FTJ(V1s[i], 0, pols)
    polStates[n] = pols
    n+=1

Pol = pols
for j in range(N-3):
    print()
    print("j:", j)
    if j==0:
        drainI2[j], pols = FTJ(V2s[j], 0, Pol)
    else:    
        drainI2[j], pols = FTJ(V2s[j], 0, pols)
    polStates[n] = pols
    n+=1

Pol = pols
for j in range(N-2):
    print()
    print("k:", j)
    if j==0:
        drainI3[j], pols = FTJ(V3s[j], 0, Pol)
    else:    
        drainI3[j], pols = FTJ(V3s[j], 0, pols)
    polStates[n] = pols
    n+=1

Pol = pols
for j in range(N-3):
    print()
    print("l:", j)
    if j==0:
        drainI4[j], pols = FTJ(V4s[j], 0, Pol)
    else:    
        drainI4[j], pols = FTJ(V4s[j], 0, pols)
    polStates[n] = pols
    n+=1


fig = plt.figure()
plt.plot(V1s, np.log10(drainI1))
plt.xlabel("Voltage")
plt.ylabel("Drain current")
plt.plot(V2s, np.log10(drainI2))
plt.plot(V3s, np.log10(drainI3))
plt.plot(V4s, np.log10(drainI4))

fig2 = plt.figure()
plt.title("Polarisation")
plt.plot(V1s, polStates[0:19], label = "V1s")
plt.plot(V2s, polStates[19:37], label = "V2s")
plt.plot(V3s, polStates[37:56], label = "V3s")
plt.plot(V4s, polStates[56:74], label = "V4s")
plt.legend()


