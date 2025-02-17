import os
import time

from util import run_cmd
import tempfile
import shapely
from osgeo import ogr
import geopandas as gpd
import dask_geopandas as dgpd
from dask.diagnostics import ProgressBar
from tqdm import tqdm
from shapely.geometry import box


def query_cadastral_data_tiled(gdf, geo_url):
    # test
    """Fetches feature count within a bounding box using remote access."""

    layer_name = "NFL"
    bbox = gdf.total_bounds

    src = f"/vsicurl/{geo_url}"
    dst = "output/tmp.gpkg"

    command_sql = f'ogr2ogr -f "GPKG" -spat {bbox[0]} {bbox[1]} {bbox[2]} {bbox[3]} -dialect OGRSQL -sql "SELECT * FROM {layer_name} WHERE NS=41" {dst} {src}'
    run_cmd(command_sql)

    sub = gpd.read_file(dst)
    for ind, row in tqdm(gdf.iterrows()):

        output_file = f'output_vector/{row["index"]}.gpkg'
        if os.path.exists(output_file):
            print(f'This geometry area: {output_file} has alReady been queryied, for this timestamp.')
            continue

        clipped = sub.clip(mask=row.geometry, keep_geom_type=True)
        clipped.to_file(output_file, driver='GPKG', layer='NFL')
    return


TU_PC = False
if TU_PC:
    BASE_PATH = r"U:\master\metadata"
else:
    BASE_PATH = "C:/Users/PC/Desktop/TU/Master/MasterThesis/data/orthofotos/all/metadata"

query_cells = gpd.read_file(f'output/raster_5.shp')

polygon = shapely.box(516143, 470000, 536665, 496558)

time_grouped = query_cells.groupby('vector_url')
for geoUrl, group in time_grouped:
    print(f'Processing: {geoUrl}')

    t1 = time.time()
    query_cadastral_data_tiled(gdf=group, geo_url=geoUrl)
    t2 = time.time()
    print('... took: ', t2-t1)