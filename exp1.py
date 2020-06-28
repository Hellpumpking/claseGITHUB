# -*- coding: utf-8 -*-
"""
Created on Thu May 21 15:36:41 2020

@author: KEVIN
"""
#ABCDEF
import shapefile
from sentinelsat import SentinelAPI
user = 'hellpumpking'
password = 'caza1e1cazador12'
api = SentinelAPI(user, password, 'https://scihub.copernicus.eu/dhus')

#%cd "C://Users//KEVIN//Desktop//satellital//"

w = shapefile.Writer('C://Users//KEVIN//Desktop//satellital//shapefiles//test//polygon')
w.field('name', 'C')
w.poly([
            [[-73.98999,4.863768], [-73.98999,4.966215], [-73.796349,4.966215], [-73.796349,4.863768], [-73.98999,4.863768]] # poly 1
            #[[15,2], [17,6], [22,7]], # hole 1
            #[[122,37], [117,36], [115,32]] # poly 2
            ])
w.record('polygon1')
w.close()

import geopandas as gpd
import folium 
import matplotlib.pyplot as plt
import geojson

sopo = gpd.read_file('C://Users//KEVIN//Desktop//satellital//shapefiles//test//polygon.shp')
sopo.crs = {'init':'epsg:4326'} 

m = folium.Map([4.85, -73.9], zoom_start=11)
folium.GeoJson(sopo).add_to(m)
from shapely.geometry import MultiPolygon, Polygon

footprint = None
for i in sopo['geometry']:
    footprint = i
footprint

R10 = "C://Users//KEVIN//Desktop//satellital//Sopo_sentinel/"

# Open Bands 8, 4, 3 and 2 with Rasterio #april image
import rasterio as rio
b4 = rio.open(R10+'T18NXL_20200109T152631_B04.jp2')
b3 = rio.open(R10+'T18NXL_20200109T152631_B03.jp2')
b2 = rio.open(R10+'T18NXL_20200109T152631_B02.jp2')
b8 = rio.open(R10+'T18NXL_20200109T152631_B08.jp2')

# Create an RGB image 
with rio.open('RGB_sopo_big.tiff','w',driver='Gtiff', width=b4.width, height=b4.height, 
              count=3,crs=b4.crs,transform=b4.transform, dtype=b4.dtypes[0]) as rgb:
    rgb.write(b2.read(1),1) 
    rgb.write(b3.read(1),2) 
    rgb.write(b4.read(1),3) 
    rgb.close()

from rasterio.mask import mask
sopo_proj = sopo.to_crs("epsg:32618") #busccar coincidencia con coordinadas de imagen
sopo_proj


with rio.open("RGB_sopo_big.tiff") as src:
    out_image, out_transform = rio.mask.mask(src, sopo_proj.geometry,crop=True)
    out_meta = src.meta.copy()
    out_meta.update({"driver": "GTiff",
                 "height": out_image.shape[1],
                 "width": out_image.shape[2],
                 "transform": out_transform})
    
with rio.open("RGB_sopo_big_masked.tif", "w", **out_meta) as dest:
    dest.write(out_image)
    
rgb_plt = rio.open('RGB_sopo_big_masked.tif')
fig = plt.figure(figsize=(16,16))
plt.imshow(rgb_plt.read(1), cmap='pink')    

#subplot histogram and image !!!!!
from rasterio.plot import show_hist

fig, (axrgb, axhist) = plt.subplots(1, 2, figsize=(14,7))
show(rgb_plt, ax=axrgb)
show_hist(rgb_plt, bins=50, histtype='stepfilled',
     lw=0.0, stacked=False, alpha=0.3, ax=axhist)
plt.show()    


with rio.open(R10+'T18NXL_20200109T152631_B04.jp2') as src:
    out_image, out_transform = rio.mask.mask(src, sopo_proj.geometry,crop=True)
    out_meta = src.meta.copy()
    out_meta.update({"driver": "GTiff",
                 "height": out_image.shape[1],
                 "width": out_image.shape[2],
                 "transform": out_transform})
    
with rio.open("RGB_big_red.tif", "w", **out_meta) as dest:
    dest.write(out_image)
    
with rio.open(R10+'T18NXL_20200109T152631_B08.jp2') as src:
    out_image, out_transform = rio.mask.mask(src, sopo_proj.geometry,crop=True)
    out_meta = src.meta.copy()
    out_meta.update({"driver": "GTiff",
                 "height": out_image.shape[1],
                 "width": out_image.shape[2],
                 "transform": out_transform})
    
with rio.open("RGB_big_nir.tif", "w", **out_meta) as dest:
    dest.write(out_image)    
    
    