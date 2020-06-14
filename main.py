"""in.py: 
"""
    
__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2017-, Dilawar Singh"
__version__          = "1.0.0"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"
__status__           = "Development"

import sys
from osgeo import gdal_array
#from mpl_toolkits.basemap import Basemap, cm
import matplotlib as mpl
import matplotlib.pyplot as plt
mpl.style.use( ['bmh', 'fivethirtyeight'] )
import numpy as np
import scipy.spatial
import pandas as pd

scale_ = 111.03    # At 40deg from equation 1deg=111.03km

cols='id:name:asciiname:alternatenames:latitude: longitude:' \
        + 'featureclass:featurecode: countrycode: cc2:' \
        + 'admin1code: admin2code: admin3code: admin4code: population:'\
        + 'elevation:dem:timezone:modificationdate'

cols = [x.strip() for x in cols.split(':')]

def info(df):
    print( 'MIN ELEVATION', df['elevation'].min() )
    print( 'MAX ELEVATION', df['elevation'].max() )
    print('TOTAL POINTS: ', len(df))

def center_of_mass(xs, ys, ws):
    gmean = xs.mean(), ys.mean()
    pts = np.dstack((xs, ys))[0]
    hull = scipy.spatial.ConvexHull(pts)
    outline = pts[hull.vertices]
    mean = sum(xs * ws)/sum(ws), sum(ys*ws)/sum(ws)
    return mean, gmean, outline

def main_gdal(infile):
    raster = gdal_array.LoadFile(infile)
    print(raster)

    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.tight_layout( )
    plt.savefig(f'{__file__}.png')

def main_png(pngfile):
    data = plt.imread(pngfile)
    print(data.shape)
    print(data.min(), data.max())

if __name__ == '__main__':
    infile = sys.argv[1]
    main_png(infile)
