# -*- coding: utf-8 -*-
"""
Created on Sat May 23 08:16:35 2020

@author: KEVIN
"""
#CDE
####### crear el polígono general ##########
import shapefile

w = shapefile.Writer('C://Users//KEVIN//Desktop//satellital//shapefiles//test//polygon')
w.field('name', 'C')
w.poly([
            [[-73.98999,4.863768], [-73.98999,4.966215], [-73.796349,4.966215], [-73.796349,4.863768], [-73.98999,4.863768]] # poly 1
            #[[15,2], [17,6], [22,7]], # hole 1
            #[[122,37], [117,36], [115,32]] # poly 2
            ])
w.record('polygon1')
w.close()


### AOI ###

import geopandas as gpd

aoi = gpd.read_file('C://Users//KEVIN//Desktop//satellital//shapefiles//test//polygon.shp')
aoi.crs = {'init':'epsg:4326', 'no_defs': True} 

aoi


from shapely.geometry import MultiPolygon, Polygon

footprint = None
for i in aoi['geometry']:
    footprint = i
footprint

from rasterio.mask import mask
aoi_proj = aoi.to_crs("epsg:32618") #busccar coincidencia con coordinadas de imagen
aoi_proj


import rasterio as rio
R10 = "C://Users//KEVIN//Desktop//satellital//Sopo_sentinel//"

# Open b4 and b8
b4 = rio.open(R10+'T18NXL_20200109T152631_B04.jp2')
b3 = rio.open(R10+'T18NXL_20200109T152631_B03.jp2')
b2 = rio.open(R10+'T18NXL_20200109T152631_B02.jp2')
b8 = rio.open(R10+'T18NXL_20200109T152631_B08.jp2')
#Reduce size of Sat image in band 4 and 8 to AOI
#import band 8 as NIR
from rasterio.mask import mask

with rio.open(R10+'T18NXL_20200109T152631_B08.jp2') as src:
    out_image, out_transform = rio.mask.mask(src, aoi_proj.geometry,crop=True)
    out_meta = src.meta.copy()
    out_meta.update({"driver": "GTiff",
                 "height": out_image.shape[1],
                 "width": out_image.shape[2],
                 "transform": out_transform})
    src.close()
with rio.open("RGB_big_nir.tif", "w", **out_meta) as dest:
    dest.write(out_image)
    dest.close()


#NDVI
# Open b4 and b8
#Reduce size of Sat image in band 4 and 8 to AOI
#import band 8 as NIR

with  rio.open(R10+'T18NXL_20200109T152631_B08.jp2') as src:
    out_image, out_transform = rio.mask.mask(src, aoi_proj.geometry,crop=True)
    out_meta = src.meta.copy()
    out_meta.update({"driver": "GTiff",
                 "height": out_image.shape[1],
                 "width": out_image.shape[2],
                 "transform": out_transform})
    src.close()
with rio.open("RGB_big_nir.tif", "w", **out_meta) as dest:
    dest.write(out_image)
    dest.close()

with rio.open(R10+'T18NXL_20200109T152631_B04.jp2') as src:
    out_image, out_transform = rio.mask.mask(src, aoi_proj.geometry,crop=True)
    out_meta = src.meta.copy()
    out_meta.update({"driver": "GTiff",
                 "height": out_image.shape[1],
                 "width": out_image.shape[2],
                 "transform": out_transform})
    src.close()
with rio.open("RGB_big_red.tif", "w", **out_meta) as dest:
    dest.write(out_image)
    dest.close()

b4a = rio.open('RGB_big_red.tif')
b8a = rio.open('RGB_big_nir.tif')

# read Red(b4) and NIR(b8) as arrays
red = b4a.read()
nir = b8a.read()
print(b4a.width, b4a.height)

x_width = b4a.width
y_height = b4a.height

import numpy as np
# Allow division by zero
np.seterr(divide='ignore', invalid='ignore')

# Calculate NDVI
ndvi = (nir.astype(float)-red.astype(float))/(nir+red)

# Write the NDVI image
meta = b4a.meta
meta.update(driver='GTiff')
meta.update(dtype=rio.float32)

with rio.open('NDVI_big_sopo.tif', 'w', **meta) as dst:
    dst.write(ndvi.astype(rio.float32))
    dst.close()
    b4a.close()
    b8a.close()

### estadísticas de la zona en general ###
print(np.nanmin(ndvi)) 
print(np.nanmax(ndvi))

########### polígonos específicos dentro de la zona ##########

aoi2 = gpd.read_file('C://Users//KEVIN//Desktop//satellital//EXP2/layers/POLYGON.shp')
aoi2.crs = {'init':'epsg:4326', 'no_defs': True}  #epsg:4326 is standard world coordinates
#aoi2 = aoi2[1:]
aoi2

aoi2_proj = aoi2.to_crs("epsg:32618") #busccar coincidencia con b4.crs
aoi2_proj

import rasterstats as rs
stats = rs.zonal_stats(aoi2_proj, "NDVI_big_sopo.tif",
            stats="count min mean max median std percentile_5.0 percentile_10.0 percentile_15.0  percentile_20.0 percentile_25.0 percentile_30.0 percentile_35.0 percentile_40.0 percentile_45.0 percentile_50.0 percentile_55.0 percentile_60.0 percentile_65.0 percentile_70.0 percentile_75.0 percentile_80.0 percentile_85.0 percentile_90.0 percentile_95.0", layer=1)

# aoi2_proj["stats_1"] = stats

#stats
#sum
#std
#median
#majority
#minority
#unique
#range
#nodata
#percentile (see note below for details)

from __future__ import division
import matplotlib.pyplot as plt
# def mymean(x):
#     # An "interface" to matplotlib.axes.Axes.hist() method
#     n, bins, patches = plt.hist(x, bins=10)#, color='#0504aa',
#                             #alpha=0.7, rwidth=0.85)
#     return n, bins, patches

# stats = rs.zonal_stats(aoi2_proj, "NDVI_big_sopo.tif",
#            stats="count",
#           add_stats={'mymean':mymean})


def hist_i(x):
     n, bins, patches = plt.hist(x, bins=10)#, color='#0504aa',
     return n, bins, patches


#, patches 

def p_i(z):
    return np.ma.sort(z)
    

type(aoi2_proj['geometry'][0])

def print_hist(y):
        for AA in counter:
            plt.hist(n = y[AA].get('hist_i')[0] , bins = y[AA].get('hist_i')[1],patches=  y[AA].get('hist_i')[2]  )
            plt.show()

stats = rs.zonal_stats(aoi2_proj['geometry'][0], "NDVI_big_sopo.tif",
           stats="count" , 
           add_stats={'hist_i':hist_i} )



stats[0].get('hist_i')

len(stats[0].get('hist_i')[0] )     #bins
stats[3].get('hist_i')[1] #bins
stats[3].get('hist_i')[2] #bins
stats[3].get('hist_i')[3] #bins


sum((stats[0].get('hist_i')[0]  ) == 0.0 )
300-43