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
    data_centroids = {"geometry": [], "ids_str": []}
    data = {"geometry": [], "ids_str": []}
    y = maxy
    i, j = 0, 0
    while y - cell_height > miny:
        x = minx
        while x + cell_width < maxx:
            cell = box(x, y - cell_height, x + cell_width, y)
            data["geometry"].append(cell)
            data_centroids["geometry"].append(cell.centroid)
            data["ids_str"].append(f"{i}_{j}")
            data_centroids["ids_str"].append(f"{i}_{j}")
            x += cell_width
            j += 1
        i += 1
        j = 0
        y -= cell_height

    # Create GeoDataFrame
    gdf_centroids = gpd.GeoDataFrame(index=data_centroids["ids_str"], geometry=data_centroids['geometry'], crs='EPSG:31287')
    gdf = gpd.GeoDataFrame(index=data["ids_str"], geometry=data['geometry'], crs='EPSG:31287')
    return gdf_centroids, gdf


# Example usage,,536665
polygon = shapely.box(516143, 470000, 536665, 496558)
# bbox = gpd.GeoDataFrame(geometry=[polygon], crs='EPSG:31287')
# bbox.to_file("output/bbox.shp")

TU_PC = False
if TU_PC:
    BASE_PATH = r"U:\master\metadata"
else:
    BASE_PATH = "C:/Users/PC/Desktop/TU/Master/MasterThesis/data/orthofotos/all/metadata"
metadata = gpd.read_file(os.path.join(BASE_PATH, "intersected_regions", "ortho_cadastral_matched.shp"))

raster_size = 2.5
centroids, uni_raster = create_uniform_raster(polygon, raster_size=5, width=512, height=512)
joined = gpd.sjoin(centroids, metadata, how="inner")

# set geometry as polygon area of field
joined['geometry'] = uni_raster.loc[joined.index, 'geometry']

joined.to_file(f'output/raster_5.shp')
print(joined)
