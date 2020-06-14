# Compute center of india.
# References:
# [1] https://gdal.org/python/osgeo.ogr.Geometry-class.html

import numpy as np
from osgeo import ogr
import json

import matplotlib as mpl
import matplotlib.pyplot as plt
mpl.style.use('ggplot')
mpl.rcParams['axes.linewidth'] = 0.1
plt.rc('font', family='serif')

with open('./india-composite.geojson') as f:
    jsonTxt = f.read()
    data = json.loads(jsonTxt)

points = [] # data['features'][0]['geometry']['coordinates'][0][0]
coords = data['features'][0]['geometry']['coordinates']

multipolygon = ogr.Geometry(ogr.wkbMultiPolygon)
for x in coords:
    ring = ogr.Geometry(ogr.wkbLinearRing)
    points = np.array(x[0])
    for p in points:
        ring.AddPoint(*p)
    p1 = ogr.Geometry(ogr.wkbPolygon)
    p1.AddGeometry(ring)
    multipolygon.AddGeometry(p1)

print('Area =', multipolygon.GetArea())
center = multipolygon.Centroid()
print('Centroid =', center)

# plot.
for x in coords:
    X, Y = zip(*x[0])
    plt.scatter(X, Y, marker=',', s=1, color='blue')

a, b =  center.GetX(), center.GetY()
plt.title(f'Centroid={a:.5f}, {b:.5f}')
plt.scatter([a], [b], color='red', s=10)

plt.savefig(f'{__file__}.png')
