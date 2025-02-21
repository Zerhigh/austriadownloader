import shapely
import time
import os
import geopandas as gpd
import typing

from utils import create_output_dirs


def download_rasterdata(gdf: gpd.GeoDataFrame, parameters: dict, url: str):
    """
    Downloads raster data based on the given geospatial extent and parameters.

    Parameters:
        gdf (gpd.GeoDataFrame):
            A GeoDataFrame containing geometries that define the spatial extent for downloading raster data.

        parameters (dict):
            A dictionary containing optional parameters for processing the raster data.
            - 'multispectral' (bool): If True, the function retrieves and merges the Near-Infrared (NIR) band
              with the RGB bands to create a multispectral dataset. NIR download url is in gdf.NIR_raster
            - ...

        url (str):
            The source URL where the RGB raster data is hosted.
    """
    # access the raster data in url with window-extent in gdf.geometry attribute (square tiles)
    # other transform attributes in parameters
    # if parameters['multispectral'] also access and merge NIR band (single band) with RGB (3 band)
    # save tiled output to disk

    print(f'Processing: {url}')
    t1 = time.time()

    src = f'/vsicurl/{url}'

    # ...

    t2 = time.time()
    print('... took: ', t2 - t1)

    return


BASE_DIR = r'C:\Users\PC\Coding\GeoQuery'

# will be external config file
parameters = {"pixel_size": 2.5,
              "image_width": 512,
              "AOI": shapely.box(516143, 470000, 536665, 496558),
              #aoi=[516143, 470000, 536665, 496558],  # [min_x, min_y, max_x, max_y]
              "base_dir": BASE_DIR,
              "multispectral": True, # should include RGB and NIR image bands
              }

# define output path
parameters['output_dir'] = os.path.join(parameters["base_dir"], f'output_ps{str(parameters["pixel_size"]).replace(".", "_")}_imgs{parameters["image_width"]}')
create_output_dirs(parameters)

metadata = gpd.read_file(os.path.join(BASE_DIR, "data", "ortho_cadastral_matched.shp"))
aoi = gpd.GeoDataFrame(geometry=[parameters["AOI"] for i in range(len(metadata))], crs=31287)

Res = aoi.intersection(metadata)


# load metadata table for querying information
query_cells = gpd.read_file(f'{parameters["output_dir"]}/raster_{str(parameters["pixel_size"]).replace(".", "_")}.shp')
query_cells.set_index('index', inplace=True)

geoms_ = []
for _, row in metadata.iterrows():
    geom = row.geometry
    if isinstance(geom, shapely.MultiPolygon):
        for g in geom.geoms:
            geoms_.append(g)
    else:
        geoms_.append(geom)
    pass

geoms_frame = gpd.GeoDataFrame(geometry=geoms_, crs=31287)
geoms_frame.to_file(f'test.shp')


# seperate gdf into sub_gdfs to limit number of http requests
grouped_ = query_cells.groupby('RGB_raster')
for geoUrl, group in grouped_:
    download_rasterdata(gdf=group, parameters=parameters, url=geoUrl)

