import subprocess

import shapely
from osgeo import ogr
import geopandas as gpd
import dask_geopandas as dgpd
from tqdm import tqdm
from shapely.geometry import box

def run_cmd(cmd, verbose=True, ret_vals=False):
    if verbose:
        print(cmd)
    if not ret_vals:
        subprocess.run(cmd, shell=True)
    else:
        return subprocess.run(cmd, capture_output=True, text=True).stdout



def query_spatially(geo_url, layer_name, bbox, output_gpkg):
    """Fetches feature count within a bounding box using remote access."""
    # dataset = ogr.Open(f"/vsicurl/{geo_url}")
    #
    # for i in range(dataset.GetLayerCount()):
    #     print(f"- {dataset.GetLayer(i).GetName()}")
    #
    # layer = dataset.GetLayerByName(layer_name)
    # print(layer.GetExtent())

    dst = "filted_data_ogr.gpkg"
    dst2 = "filted_data_ogr_clipped.gpkg"
    src = f"/vsicurl/{geo_url}"
    command_sql = f'ogr2ogr -f "GPKG" -spat  {bbox[0]} {bbox[1]} {bbox[2]} {bbox[3]} -dialect OGRSQL -sql "SELECT * FROM {layer_name} WHERE NS=41" {dst} {src}'
    run_cmd(command_sql)

    command_sql = f'ogr2ogr -f "GPKG" -clipsrc  {bbox[0]} {bbox[1]} {bbox[2]} {bbox[3]} {dst2} {dst}'
    run_cmd(command_sql)


    # Apply bounding box filter (xmin, ymin, xmax, ymax)
    #layer.SetSpatialFilterRect(*bbox)

    #sql_condition = 41
    #geom = box(*bbox)
    #sql_query = f"SELECT * FROM {layer_name} WHERE NS=41"
    # sql_query = f""" SELECT * FROM {layer_name}
    #                     WHERE NS={sql_condition}
    #                     AND ST_Intersects(geometry, {shapely.to_wkt(geom)}))
    #                 """

    #sql_layer = dataset.ExecuteSQL(sql_query)


    #print(feature)

    pass

    # feature_count = layer.GetFeatureCount()
    # print(f"Found {feature_count} features in bounding box {bbox}. Extracting...")

    # driver = ogr.GetDriverByName("GPKG")
    # output_ds = driver.CreateDataSource(output_gpkg)
    #
    # # Copy schema & features to new GeoPackage
    # output_layer = output_ds.CopyLayer(layer, layer_name)
    #
    # print(f"Extracted data saved to {output_gpkg}")
    #
    # # Cleanup
    # dataset = None
    # output_ds = None
    return



# Example usage curl -I -H "Range: bytes=0-1000" "https://data.bev.gv.at/download/Kataster/gpkg/national/KAT_DKM_GST_epsg31287_20241002.gpkg"

# Example usage
geo_url = "https://data.bev.gv.at/download/Kataster/gpkg/national/KAT_DKM_GST_epsg31287_20241002.gpkg"
layer_name = "NFL"

#bbox = (483789.68,614745.60, 483906.97,614905.30)  # Define your area of interest
# xmin, xmax, ymin, ymax
bbox = (614745.60, 483798, 614848, 483873)  # Define your area of interest
output_gpkg = "filtered_data.gpkg"

query_spatially(geo_url, layer_name=layer_name, bbox=bbox, output_gpkg=output_gpkg)
#inspect_layer_structure(geo_url, layer_name)

#ogrinfo -ro -al -so /vsicurl/https://data.bev.gv.at/download/Kataster/gpkg/national/KAT_DKM_GST_epsg31287_20241002.gpkg
