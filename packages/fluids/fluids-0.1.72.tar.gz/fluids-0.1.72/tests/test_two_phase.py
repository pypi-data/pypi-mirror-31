# -*- coding: utf-8 -*-
'''Chemical Engineering Design Library (ChEDL). Utilities for process modeling.
Copyright (C) 2016, 2017 Caleb Bell <Caleb.Andrew.Bell@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.'''

from __future__ import division
from fluids import *
import numpy as np
from numpy.testing import assert_allclose
import pytest


def test_Friedel():
    dP = Friedel(m=10, x=0.9, rhol=950., rhog=1.4, mul=1E-3, mug=1E-5, sigma=0.02, D=0.3, roughness=0, L=1)
    assert_allclose(dP, 274.21322116878406)

    # Example 4 in [6]_:
    dP = Friedel(m=0.6, x=0.1, rhol=915., rhog=2.67, mul=180E-6, mug=14E-6, sigma=0.0487, D=0.05, roughness=0, L=1)
    assert_allclose(dP, 738.6500525002241)
    # 730 is the result in [1]_; they use the Blassius equation instead for friction
    # the multiplier was calculated to be 38.871 vs 38.64 in [6]_


def test_Gronnerud():
    dP = Gronnerud(m=0.6, x=0.1, rhol=915., rhog=2.67, mul=180E-6, mug=14E-6, D=0.05, roughness=0, L=1)
    assert_allclose(dP, 384.125411444741)

    dP = Gronnerud(m=5, x=0.1, rhol=915., rhog=2.67, mul=180E-6, mug=14E-6, D=0.05, roughness=0, L=1)
    assert_allclose(dP, 26650.676132410194)

def test_Chisholm():
    # Gamma < 28, G< 600
    dP = Chisholm(m=0.6, x=0.1, rhol=915., rhog=2.67, mul=180E-6, mug=14E-6, D=0.05, roughness=0, L=1)
    assert_allclose(dP, 1084.1489922923736)

    # Gamma < 28, G > 600
    dP = Chisholm(m=2, x=0.1, rhol=915., rhog=2.67, mul=180E-6, mug=14E-6, D=0.05, roughness=0, L=1)
    assert_allclose(dP, 7081.89630764668)

    # Gamma <= 9.5, G_tp <= 500
    dP = Chisholm(m=.6, x=0.1, rhol=915., rhog=30, mul=180E-6, mug=14E-6, D=0.05, roughness=0, L=1)
    assert_allclose(dP, 222.36274920522493)

    # Gamma <= 9.5, G_tp < 1900:
    dP = Chisholm(m=2, x=0.1, rhol=915., rhog=30, mul=180E-6, mug=14E-6, D=0.05, roughness=0, L=1)
    assert_allclose(dP, 1107.9944943816388)

    # Gamma <= 9.5, G_tp > 1900:
    dP = Chisholm(m=5, x=0.1, rhol=915., rhog=30, mul=180E-6, mug=14E-6, D=0.05, roughness=0, L=1)
    assert_allclose(dP, 3414.1123536958203)

    dP = Chisholm(m=1, x=0.1, rhol=915., rhog=0.1, mul=180E-6, mug=14E-6, D=0.05, roughness=0, L=1)
    assert_allclose(dP, 8743.742915625126)

    # Roughness correction
    dP = Chisholm(m=0.6, x=0.1, rhol=915., rhog=2.67, mul=180E-6, mug=14E-6, D=0.05, roughness=1E-4, L=1, rough_correction=True)
    assert_allclose(dP, 846.6778299960783)


def test_Baroczy_Chisholm():
    # Gamma < 28, G< 600
    dP = Baroczy_Chisholm(m=0.6, x=0.1, rhol=915., rhog=2.67, mul=180E-6, mug=14E-6, D=0.05, roughness=0, L=1)
    assert_allclose(dP, 1084.1489922923736)

    # Gamma <= 9.5, G_tp > 1900:
    dP = Baroczy_Chisholm(m=5, x=0.1, rhol=915., rhog=30, mul=180E-6, mug=14E-6, D=0.05, roughness=0, L=1)
    assert_allclose(dP, 3414.1123536958203)

    dP = Baroczy_Chisholm(m=1, x=0.1, rhol=915., rhog=0.1, mul=180E-6, mug=14E-6, D=0.05, roughness=0, L=1)
    assert_allclose(dP, 8743.742915625126)


def test_Muller_Steinhagen_Heck():
    dP = Muller_Steinhagen_Heck(m=0.6, x=0.1, rhol=915., rhog=2.67, mul=180E-6, mug=14E-6, D=0.05, roughness=0, L=1)
    assert_allclose(dP, 793.4465457435081)


def test_Lombardi_Pedrocchi():
    dP = Lombardi_Pedrocchi(m=0.6, x=0.1, rhol=915., rhog=2.67, sigma=0.045, D=0.05, L=1)
    assert_allclose(dP, 1567.328374498781)


def test_Theissing():
    dP = Theissing(m=0.6, x=.1, rhol=915., rhog=2.67, mul=180E-6, mug=14E-6, D=0.05, roughness=0, L=1)
    assert_allclose(dP, 497.6156370699528)

    # Test x=1, x=0
    dP = Theissing(m=0.6, x=1, rhol=915., rhog=2.67, mul=180E-6, mug=14E-6, D=0.05, roughness=0, L=1)
    assert_allclose(dP, 4012.248776469056)

    dP = Theissing(m=0.6, x=0, rhol=915., rhog=2.67, mul=180E-6, mug=14E-6, D=0.05, roughness=0, L=1)
    assert_allclose(dP, 19.00276790390895)


def test_Jung_Radermacher():
    dP = Jung_Radermacher(m=0.6, x=0.1, rhol=915., rhog=2.67, mul=180E-6, mug=14E-6, D=0.05, roughness=0, L=1)
    assert_allclose(dP, 552.068612372557)


def test_Tran():
    dP = Tran(m=0.6, x=0.1, rhol=915., rhog=2.67, mul=180E-6, mug=14E-6, sigma=0.0487, D=0.05, roughness=0, L=1)
    assert_allclose(dP, 423.2563312951231)


def test_Chen_Friedel():
    dP = Chen_Friedel(m=.0005, x=0.9, rhol=950., rhog=1.4, mul=1E-3, mug=1E-5, sigma=0.02, D=0.003, roughness=0, L=1)
    assert_allclose(dP, 6249.247540588871)

    dP = Chen_Friedel(m=.1, x=0.9, rhol=950., rhog=1.4, mul=1E-3, mug=1E-5, sigma=0.02, D=0.03, roughness=0, L=1)
    assert_allclose(dP, 3541.7714973093725)


def test_Zhang_Webb():
    dP = Zhang_Webb(m=0.6, x=0.1, rhol=915., mul=180E-6, P=2E5, Pc=4055000, D=0.05, roughness=0, L=1)
    assert_allclose(dP, 712.0999804205619)


def test_Bankoff():
    dP = Bankoff(m=0.6, x=0.1, rhol=915., rhog=2.67, mul=180E-6, mug=14E-6, D=0.05, roughness=0, L=1)
    assert_allclose(dP, 4746.059442453398)


def test_Xu_Fang():
    dP = Xu_Fang(m=0.6, x=0.1, rhol=915., rhog=2.67, mul=180E-6, mug=14E-6, sigma=0.0487, D=0.05, roughness=0, L=1)
    assert_allclose(dP, 604.0595632116267)

def test_Yu_France():
    dP = Yu_France(m=0.6, x=.1, rhol=915., rhog=2.67, mul=180E-6, mug=14E-6, D=0.05, roughness=0, L=1)
    assert_allclose(dP, 1146.983322553957)


def test_Wang_Chiang_Lu():
    dP = Wang_Chiang_Lu(m=0.6, x=0.1, rhol=915., rhog=2.67, mul=180E-6, mug=14E-6, D=0.05, roughness=0, L=1)
    assert_allclose(dP, 448.29981978639154)

    dP = Wang_Chiang_Lu(m=0.1, x=0.1, rhol=915., rhog=2.67, mul=180E-6, mug=14E-6, D=0.05, roughness=0, L=1)
    assert_allclose(dP, 3.3087255464765417)


def test_Hwang_Kim():
    dP = Hwang_Kim(m=0.0005, x=0.1, rhol=915., rhog=2.67, mul=180E-6, mug=14E-6, sigma=0.0487, D=0.003, roughness=0, L=1)
    assert_allclose(dP, 798.302774184557)


def test_Zhang_Hibiki_Mishima():
    dP = Zhang_Hibiki_Mishima(m=0.0005, x=0.1, rhol=915., rhog=2.67, mul=180E-6, mug=14E-6, sigma=0.0487, D=0.003, roughness=0, L=1)
    assert_allclose(dP, 444.9718476894804)

    dP = Zhang_Hibiki_Mishima(m=0.0005, x=0.1, rhol=915., rhog=2.67, mul=180E-6, mug=14E-6, sigma=0.0487, D=0.003, roughness=0, L=1, flowtype='adiabatic gas')
    assert_allclose(dP, 1109.1976111277042)

    dP = Zhang_Hibiki_Mishima(m=0.0005, x=0.1, rhol=915., rhog=2.67, mul=180E-6, mug=14E-6, sigma=0.0487, D=0.003, roughness=0, L=1, flowtype='flow boiling')
    assert_allclose(dP, 770.0975665928916)

    with pytest.raises(Exception):
        Zhang_Hibiki_Mishima(m=0.0005, x=0.1, rhol=915., rhog=2.67, mul=180E-6, mug=14E-6, sigma=0.0487, D=0.003, roughness=0, L=1, flowtype='BADMETHOD')


def test_Kim_Mudawar():
    # turbulent-turbulent
    dP = Kim_Mudawar(m=0.6, x=0.1, rhol=915., rhog=2.67, mul=180E-6, mug=14E-6, sigma=0.0487, D=0.05, L=1)
    assert_allclose(dP, 840.4137796786074)

    # Re_l >= Re_c and Re_g < Re_c
    dP = Kim_Mudawar(m=0.6, x=0.001, rhol=915., rhog=2.67, mul=180E-6, mug=14E-6, sigma=0.0487, D=0.05, L=1)
    assert_allclose(dP, 68.61594310455612)

    # Re_l < Re_c and Re_g >= Re_c:
    dP = Kim_Mudawar(m=0.6, x=0.99, rhol=915., rhog=2.67, mul=180E-6, mug=14E-6, sigma=0.0487, D=0.05, L=1)
    assert_allclose(dP, 5381.335846128011)

    # laminar-laminar
    dP = Kim_Mudawar(m=0.1, x=0.1, rhol=915., rhog=2.67, mul=180E-6, mug=14E-6, sigma=0.0487, D=0.5, L=1)
    assert_allclose(dP, 0.005121833671658875)

    # Test friction Re < 20000
    dP = Kim_Mudawar(m=0.1, x=0.1, rhol=915., rhog=2.67, mul=180E-6, mug=14E-6, sigma=0.0487, D=0.05, L=1)

    assert_allclose(dP, 33.74875494223592)


def test_Lockhart_Martinelli():
    dP = Lockhart_Martinelli(m=0.6, x=0.1, rhol=915., rhog=2.67, mul=180E-6, mug=14E-6, D=0.05, L=1)
    assert_allclose(dP, 716.4695654888484)

    # laminar-laminar
    dP = Lockhart_Martinelli(m=0.1, x=0.1, rhol=915., rhog=2.67, mul=180E-6, mug=14E-6, D=1, L=1)
    assert_allclose(dP, 9.06478815533121e-06)

    # Liquid laminar, gas turbulent
    dP = Lockhart_Martinelli(m=0.6, x=0.1, rhol=915., rhog=2.67, mul=180E-6, mug=14E-6, D=2, L=1)
    assert_allclose(dP, 8.654579552636214e-06)

    # Gas laminar, liquid turbulent
    dP = Lockhart_Martinelli(m=0.6, x=0.05, rhol=915., rhog=2.67, mul=180E-6, mug=14E-6, D=2, L=1)
    assert_allclose(dP, 4.56627076018814e-06)


def test_Mishima_Hibiki():
    dP = Mishima_Hibiki(m=0.6, x=0.1, rhol=915., rhog=2.67, mul=180E-6, mug=14E-6, sigma=0.0487, D=0.05, roughness=0, L=1)
    assert_allclose(dP, 732.4268200606265)



def test_two_phase_dP():
    # Case 0
    assert ['Lombardi_Pedrocchi'] == two_phase_dP(10, 0.7, 1000, 0.1, rhog=1.2, sigma=0.02, AvailableMethods=True)
    # Case 5
    assert ['Zhang_Webb'] == two_phase_dP(10, 0.7, 1000, 0.1, mul=1E-3, P=1E5, Pc=1E6, AvailableMethods=True)
    # Case 1,2
    expect = ['Jung_Radermacher', 'Muller_Steinhagen_Heck', 'Baroczy_Chisholm', 'Yu_France', 'Wang_Chiang_Lu', 'Theissing', 'Chisholm rough', 'Chisholm', 'Gronnerud', 'Lockhart_Martinelli', 'Bankoff']
    actual = two_phase_dP(10, 0.7, 1000, 0.1, rhog=1.2, mul=1E-3, mug=1E-6, AvailableMethods=True)
    assert sorted(expect) == sorted(actual)
    # Case 3, 4; drags in 5, 1, 2
    expect = ['Zhang_Hibiki_Mishima adiabatic gas', 'Kim_Mudawar', 'Friedel', 'Jung_Radermacher', 'Hwang_Kim', 'Muller_Steinhagen_Heck', 'Baroczy_Chisholm', 'Tran', 'Yu_France', 'Zhang_Hibiki_Mishima flow boiling', 'Xu_Fang', 'Wang_Chiang_Lu', 'Theissing', 'Chisholm rough', 'Chisholm', 'Mishima_Hibiki', 'Gronnerud', 'Chen_Friedel', 'Lombardi_Pedrocchi', 'Zhang_Hibiki_Mishima', 'Lockhart_Martinelli', 'Bankoff']
    actual = two_phase_dP(10, 0.7, 1000, 0.1, rhog=1.2, mul=1E-3, mug=1E-6, sigma=0.014, AvailableMethods=True)
    assert sorted(expect) == sorted(actual)

    # Final method attempt Lombardi_Pedrocchi
    dP = two_phase_dP(m=0.6, x=0.1, rhol=915., rhog=2.67, sigma=0.045, D=0.05, L=1)
    assert_allclose(dP, 1567.328374498781)

    # Second method attempt Zhang_Webb
    dP = two_phase_dP(m=0.6, x=0.1, rhol=915., mul=180E-6, P=2E5, Pc=4055000, D=0.05, roughness=0, L=1)
    assert_allclose(dP, 712.0999804205619)

    # Second choice, for no sigma; Chisholm
    dP = two_phase_dP(m=0.6, x=0.1, rhol=915., rhog=2.67, mul=180E-6, mug=14E-6, D=0.05, roughness=0, L=1)
    assert_allclose(dP, 1084.1489922923736)

    # Prefered choice, Kim_Mudawar
    dP = two_phase_dP(m=0.6, x=0.1, rhol=915., rhog=2.67, mul=180E-6, mug=14E-6, sigma=0.0487, D=0.05, L=1)
    assert_allclose(dP, 840.4137796786074)

    # Case where i = 4
    dP = two_phase_dP(Method='Friedel', m=0.6, x=0.1, rhol=915., rhog=2.67, mul=180E-6, mug=14E-6, sigma=0.0487, D=0.05, roughness=0, L=1)
    assert_allclose(dP, 738.6500525002243)

    # Case where i = 1
    dP = two_phase_dP(Method='Lockhart_Martinelli', m=0.6, x=0.1, rhol=915., rhog=2.67, mul=180E-6, mug=14E-6, D=0.05, L=1)
    assert_allclose(dP, 716.4695654888484)

    # Case where i = 101, 'Chisholm rough'
    dP = two_phase_dP(Method='Chisholm rough', m=0.6, x=0.1, rhol=915., rhog=2.67, mul=180E-6, mug=14E-6, D=0.05, roughness=1E-4, L=1)
    assert_allclose(dP, 846.6778299960783)

    # Case where i = 102:
    dP = two_phase_dP(Method='Zhang_Hibiki_Mishima adiabatic gas', m=0.0005, x=0.1, rhol=915., rhog=2.67, mul=180E-6, mug=14E-6, sigma=0.0487, D=0.003, roughness=0, L=1)
    assert_allclose(dP, 1109.1976111277042)

    # Case where i = 103:
    dP = two_phase_dP(Method='Zhang_Hibiki_Mishima flow boiling', m=0.0005, x=0.1, rhol=915., rhog=2.67, mul=180E-6, mug=14E-6, sigma=0.0487, D=0.003, roughness=0, L=1)
    assert_allclose(dP, 770.0975665928916)

    # Don't give enough information:
    with pytest.raises(Exception):
        two_phase_dP(m=0.6, x=0.1, rhol=915., D=0.05, L=1)

    with pytest.raises(Exception):
        two_phase_dP(m=0.6, x=0.1, rhol=915., rhog=2.67, sigma=0.045, D=0.05, L=1, Method='BADMETHOD')


def test_two_phase_dP_acceleration():
    m = 1
    D = 0.1
    xi = 0.37263067757947943
    xo = 0.5570214522041096
    rho_li = 827.1015716377739
    rho_lo = 827.05
    rho_gi = 3.9190921750559062
    rho_go = 3.811717994431281
    alpha_i = homogeneous(x=xi, rhol=rho_li, rhog=rho_gi)
    alpha_o = homogeneous(x=xo, rhol=rho_lo, rhog=rho_go)
    dP = two_phase_dP_acceleration(m=m, D=D, xi=xi, xo=xo, alpha_i=alpha_i, 
                                   alpha_o=alpha_o, rho_li=rho_li, rho_gi=rho_gi,
                                   rho_go=rho_go, rho_lo=rho_lo)
    assert_allclose(dP, 824.0280564053887)


def test_two_phase_dP_dz_acceleration():
    dP_dz = two_phase_dP_dz_acceleration(m=1, D=0.1, x=0.372, rhol=827.1, rhog=3.919, alpha=0.992)
    assert_allclose(dP_dz, 1543.3120935618122)
    
    
def test_two_phase_dP_gravitational():
    dP = two_phase_dP_gravitational(angle=90, z=2, alpha_i=0.9685, rho_li=1518., rho_gi=2.6)
    assert_allclose(dP, 987.237416829999)
    
    dP = two_phase_dP_gravitational(angle=90, z=2, alpha_i=0.9685, rho_li=1518., rho_gi=2.6,  alpha_o=0.968, rho_lo=1517.9, rho_go=2.59)
    assert_allclose(dP, 994.5416058829999)
    
    
def test_two_phase_dP_dz_gravitational():
    dP_dz = two_phase_dP_dz_gravitational(angle=90, alpha=0.9685, rhol=1518., rhog=2.6)
    assert_allclose(dP_dz, 493.6187084149995)