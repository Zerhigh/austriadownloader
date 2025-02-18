import os
import geopandas as gpd
import shapely

from shapely.geometry import box

from utils import create_output_dirs


def modify_date_acess(date):
    # for the year 2023 the bev data is Accessed with _20230403.gpkg instead of _20230401.gpkg! Manual modification is erQuoiered
    if '202304' in date:
        return '20230403'


def generate_raster_urls(row):
    # manually dEtermined
    series_indicator = {2021: 20221027, 2022: 20221231, 2023: 20240625}

    url_base = 'https://data.bev.gv.at/download/DOP/'

    return f'{url_base}/{series_indicator[row.Jahr]}/{row.ARCHIVNR}_Mosaik_RGB.tif'


def create_uniform_raster(polygon, pixel_size, width, height):
    """
    Creates a uniform raster within a user-defined polygon boundary and returns a GeoDataFrame.

    :param polygon_geojson: GeoJSON polygon defining the boundary.
    :param pixel_size: Cell size (resolution) of the raster.
    :param width: Number of columns in the raster.
    :param height: Number of rows in the raster.
    :return: GeoDataFrame with raster cell geometries.
    """

    minx, miny, maxx, maxy = polygon.bounds

    # Define cell size
    cell_width = width * pixel_size
    cell_height = height * pixel_size

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


TU_PC = False
if TU_PC:
    BASE_PATH = r"U:\master\metadata"
else:
    BASE_PATH = "C:/Users/PC/Desktop/TU/Master/MasterThesis/data/orthofotos/all/metadata"
metadata = gpd.read_file(os.path.join(BASE_PATH, "intersected_regions", "ortho_cadastral_matched.shp"))

parameters = {"pixel_size": 2.5,
              "image_width": 512,
              "AOI": shapely.box(516143, 470000, 536665, 496558),
              "base_dir": r'C:\Users\PC\Coding\GeoQuery'}

parameters['output_dir'] = os.path.join(parameters["base_dir"], f'output_ps{str(parameters["pixel_size"]).replace(".", "_")}_imgs{parameters["image_width"]}')
create_output_dirs(parameters)

# bbox = gpd.GeoDataFrame(geometry=[parameters["AOI"]], crs='EPSG:31287')
# bbox.to_file("output/bbox.shp")

centroids, uni_raster = create_uniform_raster(polygon=parameters["AOI"],
                                              pixel_size=parameters["pixel_size"],
                                              width=parameters["image_width"],
                                              height=parameters["image_width"])

joined = gpd.sjoin(centroids, metadata, how="inner")

# set geometry as polygon area of field
joined['geometry'] = uni_raster.loc[joined.index, 'geometry']
joined.to_file(f'{parameters["output_dir"]}/raster_{str(parameters["pixel_size"]).replace(".", "_")}.shp')
print(joined)
