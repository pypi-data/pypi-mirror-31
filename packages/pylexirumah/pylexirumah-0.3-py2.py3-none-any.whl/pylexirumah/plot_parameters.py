# coding: utf8
"""Plot the number of filled-in parameters for each language.

parameter_sampled: map languages to sets of parameters
"""
import sys
import argparse
import colorsys
import re
import json
from collections import defaultdict, Counter

import numpy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

import pycldf
from clldutils.path import Path
from pyglottolog.api import Glottolog


def parameters_sampled(dataset):
    """Check which parameters are given for which languages.

    Return the dictionary mapping all language ids present in the dataset's
    primary table to the set of parameter ids with values for that language.

    Parameters
    ----------
    dataset: pycldf.Dataset

    Returns
    -------
    dict

    """
    languageReference = dataset[dataset.primary_table, "languageReference"].name
    parameterReference = dataset[dataset.primary_table, "parameterReference"].name
    return Counter(row[languageReference] for row in dataset[dataset.primary_table])


def main(args=sys.argv):
    """The main CLI"""
    # Parse options
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        'dataset', type=Path,
        help="Path to the CLDF dataset's JSON description")
    parser.add_argument(
        "output",
        help="File name to write output to")
    parser.add_argument(
        "--glottolog-repos", default=None,
        help="Path to local clone or export of clld/glottolog")
    parser.add_argument(
        "--cmap", type=plt.get_cmap, default=plt.get_cmap("magma_r"),
        help="Colormap to be used for the parameter counts")
    options = parser.parse_args()

    dataset = pycldf.Dataset.from_metadata(options.dataset)

    # Try to load language locations from the dataset
    locations = {}
    try:
        idcol = dataset["LanguageTable", "id"].name
        latcol = dataset["LanguageTable", "latitude"].name
        loncol = dataset["LanguageTable", "longitude"].name
        for row in dataset["LanguageTable"]:
            if row[latcol] is not None:
                locations[row[idcol]] = row[latcol], row[loncol]
    except ValueError:
        # No language table
        pass

    for lang in Glottolog(options.glottolog_repos).languoids():
        if lang.latitude is not None:
            if lang.id not in locations:
                locations[lang.id] = (lang.latitude, lang.longitude)
            if lang.iso and lang.iso not in locations:
                locations[lang.iso] = (lang.latitude, lang.longitude)

    # Aggregate the data
    lats, lons, sizes = [], [], []

    for language, sample_size in parameters_sampled(dataset).items():
        if language in locations:
            lat, lon = locations[language]
            lats.append(float(lat))
            lons.append(float(lon))
            sizes.append(sample_size)

    assert len(sizes) == len(lats) == len(lons)

    # Calculate coordinate boundaries
    min_lat, max_lat = min(lats), max(lats)
    d_lat = max_lat - min_lat
    min_lat = max(-90, min_lat - 0.1 * d_lat)
    max_lat = min(90, max_lat + 0.1 * d_lat)

    min_lon, max_lon = min(lons), max(lons)
    d_lon = max_lon - min_lon
    min_lon = max(-180, min_lon - 0.1 * d_lon)
    max_lon = min(180, max_lon + 0.1 * d_lon)

    # Draw the base map
    # TODO: Get coordinates from commandline, fallback to bounding box of data
    # TODO: Give more control over map drawing to user (projection, level of
    # detail, drawing other patterns (countries, eg.) instead of just coast
    # lines, continent color) – What is a good way to do that?
    map = Basemap(llcrnrlat=min_lat, llcrnrlon=min_lon, urcrnrlat=max_lat, urcrnrlon=max_lon,
                  # projection='lcc',
                  resolution='h', area_thresh=10)
    map.drawcoastlines()
    map.fillcontinents(color='#fff7ee', zorder=0)

    # Plot the sample sizes
    map.scatter(lons, lats, c=sizes, cmap=options.cmap, latlon=True)

    # TODO: Improve shape of components: Colorbar is very huge, margins are quite large
    plt.colorbar()
    plt.gcf().set_size_inches(12, 9)

    plt.savefig(options.output)
    return 0

if __name__ == "__main__":
    main(sys.argv)

