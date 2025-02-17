import rasterio
import numpy as np
import geopandas as gpd
import shapely
import os
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
    centroids = []
    y = maxy
    while y - cell_height > miny:
        x = minx
        while x + cell_width < maxx:
            cell = box(x, y - cell_height, x + cell_width, y)
            geometries.append(cell)
            centroids.append(cell.centroid)
            x += cell_width
        y -= cell_height

    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame(data={'geometry': centroids, 'grid_cells': geometries}, crs='EPSG:31287')
    return gdf


# Example usage,,536665
polygon = shapely.box(516143,473853, 536665, 496558)
# bbox = gpd.GeoDataFrame(geometry=[polygon], crs='EPSG:31287')
# bbox.to_file("output/bbox.shp")

BASE_PATH = r"C:\Users\PC\Coding\GeoQuery"
metadata = gpd.read_file(os.path.join(BASE_PATH, "data", "ortho_cadastral_matched.shp"))

raster_size=2.5
uni_raster = create_uniform_raster(polygon, raster_size=2.5, width=512, height=512)
joined = gpd.sjoin(uni_raster, metadata, how="inner")

uni_raster.to_file(f'output/raster_2_5.shp')
print(uni_raster)
