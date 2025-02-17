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


def query_cadastral_data(geo_url, geom, output_file):
    # test
    """Fetches feature count within a bounding box using remote access."""

    if os.path.exists(output_file):
        print(f'This geometry area: {output_file} has alReady been queryied, for this timestamp.')
        return

    layer_name = "NFL"
    geo_url = f"https://data.bev.gv.at/download/Kataster/gpkg/national/KAT_DKM_GST_epsg31287_{geo_url}.gpkg"

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


def query_cadastral_data_tiled(gdf, geo_url):
    # test
    """Fetches feature count within a bounding box using remote access."""

    # if os.path.exists(output_file):
    #     print(f'This geometry area: {output_file} has alReady been queryied, for this timestamp.')
    #     return

    layer_name = "NFL"
    bbox = gdf.total_bounds

    src = f"/vsicurl/{geo_url}"
    dst = "output/tmp.gpkg"

    command_sql = f'ogr2ogr -f "GPKG" -spat {bbox[0]} {bbox[1]} {bbox[2]} {bbox[3]} -dialect OGRSQL -sql "SELECT * FROM {layer_name} WHERE NS=41" {dst} {src}'
    run_cmd(command_sql)

    sub = gpd.read_file(dst)
    for ind, row in tqdm(gdf.iterrows()):
        clipped = sub.clip(mask=row.geometry, keep_geom_type=True)
        clipped.to_file(f'output_vector/{row["index"]}.gpkg', driver='GPKG', layer='NFL')

    # dask_gdf = dgpd.from_geopandas(sub, npartitions=8)
    # with ProgressBar():
    #     clipped = dask_gdf.map_partitions(lambda df: df.clip(cell_geom, keep_geom_type=True)).compute()
    #clipped.to_file(f'{output_file}', driver='GPKG', layer='NFL')

    # transform to clipped extent, rasterize with certain resolution
    #command_sql2 = f'ogr2ogr -f "ESRI Shapefile" -progress -clipdst "{shapely.to_wkt(geom)}" -clipsrc "{shapely.to_wkt(geom)}" {output_gpkg} {dst}'
    # command_sql2 = f'ogr2ogr -f "GPKG" -progress {output_gpkg} {dst}'
    #run_cmd(command_sql2)

    return


TU_PC = False
if TU_PC:
    BASE_PATH = r"U:\master\metadata"
else:
    BASE_PATH = "C:/Users/PC/Desktop/TU/Master/MasterThesis/data/orthofotos/all/metadata"

#metadata = gpd.read_file(os.path.join(BASE_PATH, "intersected_regions", "ortho_cadastral_matched.shp"))
query_cells = gpd.read_file(f'output/raster_5.shp')

polygon = shapely.box(516143, 470000, 536665, 496558)

time_grouped = query_cells.groupby('vector_url')
#for geo_url, group in time_grouped:
# time_grouped = query_cells.groupby('prevTime')
for geoUrl, group in time_grouped:
    print(f'Processing: {geoUrl}')

    t1 = time.time()
    query_cadastral_data_tiled(gdf=group, geo_url=geoUrl)
    t2 = time.time()
    print('... took: ', t2-t1)


    # for _, entry in group.iterrows():
    #     geometry = shapely.from_wkt(entry.cell_geom)
    #     print(f'Processing: {entry.BL}_{entry.Operat}_{entry.prevTime}')
    #
    #     t1 = time.time()
    #
    #     if isinstance(geometry, shapely.MultiPolygon):
    #         print('MuLtiGeometry: Splitting up into smaller chunks')
    #         for i, sub_geometry in enumerate(geometry.geoms):
    #             query_cadastral_data(geo_url=date, geom=sub_geometry,
    #                                  output_file=f'output/{entry.BL}_{entry.Operat}_{entry.prevTime}_{i}.gpkg')
    #     else:
    #         query_cadastral_data(geo_url=date, geom=geometry, output_file=f'output/{entry.BL}_{entry.Operat}_{entry.prevTime}.gpkg')
    #
    #     t2 = time.time()
    #     print('... took: ', t2-t1)