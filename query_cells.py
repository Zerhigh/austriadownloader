import rasterio
import numpy as np
import geopandas as gpd
import shapely
import os
from rasterio.transform import from_origin
from shapely.geometry import box
import json


def modify_date_acess(date):
    # for the year 2023 the bev data is Accessed with _20230403.gpkg instead of _20230401.gpkg! Manual modification is erQuoiered
    if '202304' in date:
        return '20230403'


def generate_raster_urls(row):
    # manually dEtermined
    series_indicator = {2021: 20221027, 2022: 20221231, 2023: 20240625}

    url_base = 'https://data.bev.gv.at/download/DOP/'

    return f'{url_base}/{series_indicator[row.Jahr]}/{row.ARCHIVNR}_Mosaik_RGB.tif'


def create_uniform_raster(polygon, raster_size, width, height):
    """
    Creates a uniform raster within a user-defined polygon boundary and returns a GeoDataFrame.

    :param polygon_geojson: GeoJSON polygon defining the boundary.
    :param raster_size: Cell size (resolution) of the raster.
    :param width: Number of columns in the raster.
    :param height: Number of rows in the raster.
    :return: GeoDataFrame with raster cell geometries.
    """

    minx, miny, maxx, maxy = polygon.bounds

    # Define cell size
    cell_width = width * raster_size
    cell_height = height * raster_size

    # Create raster grid
    data = {"geometry": [], "centroids": [], "ids_str": []}
    y = maxy
    i, j = 0, 0
    while y - cell_height > miny:
        x = minx
        while x + cell_width < maxx:
            cell = box(x, y - cell_height, x + cell_width, y)
            data["geometry"].append(cell)
            data["centroids"].append(cell.centroid)
            data["ids_str"].append(f"{i}_{j}")
            x += cell_width
            j += 1
        i += 1
        j = 0
        y -= cell_height

    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame(data=data, crs='EPSG:31287')
    return gdf


# Example usage,,536665
polygon = shapely.box(516143,473853, 536665, 496558)
# bbox = gpd.GeoDataFrame(geometry=[polygon], crs='EPSG:31287')
# bbox.to_file("output/bbox.shp")

BASE_PATH = r"C:\Users\PC\Coding\GeoQuery"
metadata = gpd.read_file(os.path.join(BASE_PATH, "data", "ortho_cadastral_matched.shp"))

# Todo1: embedd these in metadata creation function
# metadata['vector_url'] = metadata["prevTime"].apply(lambda date: f"https://data.bev.gv.at/download/Kataster/gpkg/national/KAT_DKM_GST_epsg31287_{modify_date_acess(date)}.gpkg")
# metadata['raster_url'] = metadata.apply(lambda row: generate_raster_urls(row), axis=1)

raster_size = 2.5
uni_raster = create_uniform_raster(polygon, raster_size=2.5, width=512, height=512)
joined = gpd.sjoin(uni_raster, metadata, how="inner")

uni_raster.to_file(f'output/raster_2_5.shp')
print(uni_raster)
