#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  3 13:06:55 2025

@author: M. S. C. Gravett
"""

#from EMAN2 import *
import glob
import subprocess
import argparse
import pathlib
import numpy as np

def convert_to_hdf(tomo_name):
    Path('tiltseries').mkdir(parents=True, exist_ok=True) #make directory in eman style structure
    tomo = EMData(tomo_name) #open mrc
    name_core = tomo_name.split('/')[-1][:-4] #get name
    new_name = f"{name_core}.hdf" #hdf name
    path = tomo_name.replace(f'{name_core}.mrc','') #path to file
    tomo.write_image(f'tiltseries/{path}{new_name}') #write image, need to edit this so puts in tiltseries folder

def readxf(xf_file, tlt_file):
    # EMAN translates then rotates, IMOD rotates then translates
    # R(x+dx, y+dy) = R(x, y) + R(dx, dy)
    # IMOD (dx, dy) is the rotated EMAN (dx, dy)
    #logic from tomoguide for aretomo to relion and alistair burt's emanjson2imodxf
    xf_array = np.loadtxt(xf_file) #load imod xf file
    tlt_array = np.loadtxt(tlt_file) #load imod tlt file
    A11 = xf_array[:,0] #column 1 in xf 0,0 of 2D rot matrix
    A12 = xf_array[:,1] #column 2 in xf 0,1 of 2D rot matrix
    A21 = xf_array[:,2] #column 3 in xf 1,0 of 2D rot matrix
    A22 = xf_array[:,3] #column 4 in xf 1,1 of 2D rot matrix
    dx_imod = xf_array[:,4] #column 5 in xf, shift in x
    dy_imod = xf_array[:,5] #column 6 in xf shift in y
    rotation_matrices = np.zeros([len(A11),3,3]) #make empty array to put xf file data into 3x3 transformation matrices
    rotation_matrices[:, 0, 0] = A11
    rotation_matrices[:, 0, 1] = A12
    rotation_matrices[:, 1, 0] = A21
    rotation_matrices[:, 1, 1] = A22
    rotation_matrices[:, 0, 2] = dx_imod
    rotation_matrices[:, 1, 2] = dy_imod
    rotation_matrices[:, 2, 2] = [1.0]*len(A11)
    T_inv = np.linalg.inv(rotation_matrices) #invert matrices to find shift in eman
    dx_eman = T_inv[:,0,2]
    dy_eman = T_inv[:,1,2]
    z_rot = -1*np.degrees(np.arctan2(A12,A11))#find refined tilt axis in degrees
    y_tilt = -1*tlt_array #list of tilt angles from tlt
    x_tilt = [0.0]*len(A11) #xtilt is 0 for aretomo3 imod output
    return dx_eman, dy_eman, z_rot, y_tilt, x_tilt

def get_defocus(defocus_file):
    df_array = np.loadtxt(defocus_file)
    df1 = df_array[:,1]
    df2 = df_array[:,2]
    av_df = (df1+df2)/2
    return av_df*10**-4

def imodxf2emanjson(xf_file, tlt_file, defocus_file=''): 
    Path('info').mkdir(parents=True, exist_ok=True) #make directory in eman style structure
    json_name = f'info/{tomo_name}_info.json' #name of json
    tomo_json = js_open_dict(json_name) #open empty json
    dx, dy, z_rot, y_tilt, x_tilt = readxf(xf_file, tlt_file) #get data from xf file
    json = np.stack((dx, dy, z_rot, y_tilt, x_tilt), axis=-1) #xf data in corect format
    tomo_json['apix_unbin'] = '2.21' #pixel size angstroms
    tomo_json['tlt_file']="tiltseries/disco_tomo01.mrc.hdf" #tilt series path
    tomo_json['tlt_params'] = json #write xf data to json tlt_params
    tomo_json['ali_loss'] = [1]*len(dx) #just set to arbitrary value
    tomo_json['phase'] = [10.0]*len(dx) #not sure if this is correct just copied values in tutorials
    if len(defocus_file)>0: 
        defocus = get_defocus(defocus_file) #gets defocus from
    tomo_json['defocus'] = defocus


tomo_name = '../tiltseries_mrc/disco_tomo01.mrc.mrc'
convert_to_hdf(tomo_name) #convert tilt teries from mrc to hdf
imodxf2emanjson('test.xf', 'test.tlt', 'test_CTF.txt') #xf file and tilt file from imod, ctf file from aretomo not required


