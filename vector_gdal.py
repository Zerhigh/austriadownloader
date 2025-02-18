import os
import time
import geopandas as gpd
import numpy as np
import rasterio
import shapely

from rasterio.features import rasterize
from tqdm import tqdm
from osgeo import gdal, ogr

from utils import run_cmd, create_output_dirs


def query_cadastral_data_tiled(gdf, geo_url, parameters):
    """Fetches feature count within a bounding box using remote access."""

    layer_name = "NFL"
    bbox = gdf.total_bounds
    src = f'/vsicurl/{geo_url}'

    # dst = "output/tmp.gpkg"
    # command_sql = f'ogr2ogr -f "GPKG" -spat {bbox[0]} {bbox[1]} {bbox[2]} {bbox[3]} -dialect OGRSQL -sql "SELECT * FROM {layer_name} WHERE NS=41" {dst} {src}'
    # run_cmd(command_sql)

    dst_memory = "/vsimem/temp.gpkg"

    gdal.VectorTranslate(
        dst_memory,
        src,
        format="GPKG",  # Output format (GeoPackage)
        spatFilter=(bbox[0], bbox[1], bbox[2], bbox[3]),  # Spatial filter (minx, miny, maxx, maxy)
        SQLStatement=f'SELECT * FROM {layer_name} WHERE NS=41',
        SQLDialect="OGRSQL"
    )

    sub = gpd.read_file(dst_memory)
    for ind, row in tqdm(gdf.iterrows()):

        clipped = None

        output_gpkg = f'{parameters["output_dir"]}/output_vector/{row["index"]}.gpkg'
        if os.path.exists(output_gpkg):
            print(f'This geometry area: {output_gpkg} has alReady been queryied, for this timestamp.')
        else:
            clipped = sub.clip(mask=row.geometry, keep_geom_type=True)
            clipped.to_file(output_gpkg, driver='GPKG', layer='NFL')

        rasterize_ = True
        output_tif = f'{parameters["output_dir"]}/output_raster_mask/{row["index"]}.tif'
        if os.path.exists(output_tif) and rasterize_:
            print(f'This geometry area: {output_tif} has alReady been vectorized.')
        else:
            bounds = row.geometry.bounds
            width = int((bounds[2] - bounds[0]) / parameters["pixel_size"])
            height = int((bounds[3] - bounds[1]) / parameters["pixel_size"])

            transform = rasterio.transform.from_origin(bounds[0], bounds[3], parameters["pixel_size"], parameters["pixel_size"])

            if clipped is None:
                clipped = gpd.read_file(output_gpkg)

            # Rasterize the geometries into the raster
            shapes = [(geom, 1) for geom in clipped.geometry]  # Assign value 1 to features
            binary_raster = rasterize(shapes, out_shape=(height, width), transform=transform, fill=0)

            # Save the rasterized binary image
            with rasterio.open(
                    fp=output_tif,
                    mode="w+",
                    driver="GTiff",
                    height=height,
                    width=width,
                    count=1,
                    dtype=np.uint8,
                    crs=gdf.crs,
                    transform=transform
            ) as dst:
                dst.write(binary_raster, 1)
    return


TU_PC = True
if TU_PC:
    BASE_PATH = r"U:\master\metadata"
    BASE_DIR = r'C:\Users\shollend\PycharmProjects\GeoQuery'
else:
    BASE_PATH = "C:/Users/PC/Desktop/TU/Master/MasterThesis/data/orthofotos/all/metadata"
    BASE_DIR = r'C:\Users\PC\Coding\GeoQuery'

parameters = {"pixel_size": 2.5,
              "image_width": 512,
              "AOI": shapely.box(516143, 470000, 536665, 496558),
              "base_dir": BASE_DIR}

parameters['output_dir'] = os.path.join(parameters["base_dir"], f'output_ps{str(parameters["pixel_size"]).replace(".", "_")}_imgs{parameters["image_width"]}')
create_output_dirs(parameters)

query_cells = gpd.read_file(f'{parameters["output_dir"]}/raster_{str(parameters["pixel_size"]).replace(".", "_")}.shp')
#query_cells.set_index('index', inplace=True)


time_grouped = query_cells.groupby('vector_url')
for geoUrl, group in time_grouped:
    print(f'Processing: {geoUrl}')

    t1 = time.time()
    query_cadastral_data_tiled(gdf=group, geo_url=geoUrl, parameters=parameters)
    t2 = time.time()
    print('... took: ', t2-t1)
