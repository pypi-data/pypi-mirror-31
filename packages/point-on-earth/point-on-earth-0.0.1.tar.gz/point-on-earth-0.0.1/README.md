[![Build Status](https://travis-ci.org/alekzvik/point-on-earth.svg?branch=master)](https://travis-ci.org/alekzvik/point-on-earth)
[![Coverage Status](https://coveralls.io/repos/github/alekzvik/point-on-earth/badge.svg)](https://coveralls.io/github/alekzvik/point-on-earth)
[![license](https://img.shields.io/github/license/mashape/apistatus.svg)]()
[![PyPI](https://img.shields.io/pypi/pyversions/Django.svg)]()

# point-on-earth
Generate a land point.

## What?
* Generate a point, not in the ocean.

## Why?
Sometimes you just need a point that is not in the water :)

## Examples
```python
>>> from point_on_earth import generate_land_coordinates
>>> generate_land_coordinates()
{'latitude': 65.27012536944775, 'longitude': 99.01158734350156}
```

# Attributions
Made with Natural Earth. Free vector and raster map data @ naturalearthdata.com.
