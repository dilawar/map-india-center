import matplotlib as mpl
# mpl.use( 'pgf' )
import matplotlib.pyplot as plt
mpl.style.use( ['bmh', 'fivethirtyeight'] )
import json
from collections import defaultdict
import numpy as np
import math

def deg2Km(deg, latitude):
    return math.cos(latitude) * deg * 111.32

# Approximate to 10m range. 1 deg = 111km (roughly at 40deg)
scaleF_ = 1 / deg2Km(1, 25) * (10/1000)

def analyze_region(region):
    region = sorted(region)
    X, Y = [], []
    for x, y in region:
        px = int(x / scaleF_)
        py = int(y/scaleF_)
        X.append(px); Y.append(py)

    bounds = defaultdict(list)
    X = np.array(X)
    Y = np.array(Y)
    print( X.max() - X.min())
    print( Y.max() - Y.min())
    for x, y in sorted(zip(X, Y)):
        bounds[x].append(y)
    quit()

def main():
    with open('./india-composite.geojson', 'r') as f:
        txt = f.read()
        data = json.loads(txt)
    geom = data['features'][0]['geometry']
    coords = geom['coordinates']

    allpts = []
    regions = []
    for c in coords:
        for ps in c:
            regions.append(ps)
            allpts += ps

    for region in regions:
        analyze_region(region)
        X, Y = zip(*region)
        plt.scatter(X, Y, s=1)
    plt.savefig(f'{__file__}.png')


if __name__ == '__main__':
    main()
