import rasterio
import numpy as np
import geopandas as gpd
import shapely
from rasterio.transform import from_origin
from shapely.geometry import box
import json


def create_uniform_raster(polygon, raster_size, width, height):
    """
    Creates a uniform raster within a user-defined polygon boundary and returns a GeoDataFrame.

    :param polygon_geojson: GeoJSON polygon defining the boundary.
    :param raster_size: Cell size (resolution) of the raster.
    :param width: Number of columns in the raster.
    :param height: Number of rows in the raster.
    :return: GeoDataFrame with raster cell geometries.
    """

    # Get bounding box
    # Get bounding box
    minx, miny, maxx, maxy = polygon.bounds

    # Define cell size
    cell_width = width * raster_size
    cell_height = height * raster_size

    # Create raster grid
    geometries = []
    y = maxy
    while y - cell_height > miny:
        x = minx
        while x + cell_width < maxx:
            cell = box(x, y - cell_height, x + cell_width, y)
            geometries.append(cell)
            x += cell_width
        y -= cell_height

    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame(geometry=geometries, crs='EPSG:31287')
    return gdf


# Example usage
polygon_geojson = shapely.box(487897, 509158, 474260, 528192)

gdf = create_uniform_raster(polygon_geojson, raster_size=1, width=512, height=512)
gdf.to_file(f'output/raster.shp')
print(gdf)
