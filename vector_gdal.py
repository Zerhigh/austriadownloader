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


def modify_date_acess(date):
    # for the year 2023 the bev data is Accessed with _20230403.gpkg instead of _20230401.gpkg! Manual modification is erQuoiered
    if '202304' in date:
        return '20230403'


def query_cadastral_data(geo_url, geom, output_file):
    # test
    """Fetches feature count within a bounding box using remote access."""

    if os.path.exists(output_file):
        print(f'This geometry area: {output_file} has alReady been queryied, for this timestamp.')
        return

    layer_name = "NFL"

    bbox = geom.bounds
    src = f"/vsicurl/{geo_url}"
    dst = "output/tmp.gpkg"

    command_sql = f'ogr2ogr -f "GPKG" -spat {bbox[0]} {bbox[1]} {bbox[2]} {bbox[3]} -dialect OGRSQL -sql "SELECT * FROM {layer_name} WHERE NS=41" {dst} {src}'
    run_cmd(command_sql)

    sub = gpd.read_file(dst)
    dask_gdf = dgpd.from_geopandas(sub, npartitions=8)
    with ProgressBar():
        clipped = dask_gdf.map_partitions(lambda df: df.clip(geometry, keep_geom_type=True)).compute()
    clipped.to_file(f'{output_file}', driver='GPKG', layer='NFL')

    # transform to clipped extent, rasterize with certain resolution
    #command_sql2 = f'ogr2ogr -f "ESRI Shapefile" -progress -clipdst "{shapely.to_wkt(geom)}" -clipsrc "{shapely.to_wkt(geom)}" {output_gpkg} {dst}'
    # command_sql2 = f'ogr2ogr -f "GPKG" -progress {output_gpkg} {dst}'
    #run_cmd(command_sql2)

    return


# Example usage
BASE_PATH = "C:/Users/PC/Desktop/TU/Master/MasterThesis/data/orthofotos/all/metadata"
metadata = gpd.read_file(os.path.join(BASE_PATH, "intersected_regions", "ortho_cadastral_matched.shp"))

#AOI = lu: 487897, 509158 rd: 474260, 528192

#AOI = lu: 487897, 509158 rd: 474260, 528192

time_grouped = metadata.groupby('prevTime')
for date, group in time_grouped:
    group_sorted = group.assign(area=group.geometry.area).sort_values(by="area", ascending=True)

    date = modify_date_acess(date)

    geo_url = f"https://data.bev.gv.at/download/Kataster/gpkg/national/KAT_DKM_GST_epsg31287_{date}.gpkg"

    for _, entry in group_sorted.iterrows():
        geometry = entry.geometry
        # query_cadastral_data(geo_url=geo_url, geom=geometry,
        #                      output_gpkg=f'output/{entry.BL}_{entry.Operat}_{entry.prevTime}.shp')

        print(f'Processing: {entry.BL}_{entry.Operat}_{entry.prevTime}')

        t1 = time.time()

        if isinstance(geometry, shapely.MultiPolygon):
            print('MuLtiGeometry: Splitting up into smaller chunks')
            for i, sub_geometry in enumerate(geometry.geoms):
                query_cadastral_data(geo_url=geo_url, geom=sub_geometry,
                                     output_file=f'output/{entry.BL}_{entry.Operat}_{entry.prevTime}_{i}.gpkg')
        else:
            query_cadastral_data(geo_url=geo_url, geom=geometry, output_file=f'output/{entry.BL}_{entry.Operat}_{entry.prevTime}.gpkg')

        t2 = time.time()
        print('... took: ', t2-t1)