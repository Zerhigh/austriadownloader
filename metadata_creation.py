import os
import geopandas as gpd
import shapely
import json

from datetime import datetime


# correct metadata creation Scripts

# Function to convert dates
def convert_date(date_str):
    day, month, year = date_str.split("-")
    # Mapping German month names to English
    german_to_english_months = {
        "Jan": "Jan", "Feb": "Feb", "Mär": "Mar", "Apr": "Apr", "Mai": "May",
        "Jun": "Jun", "Jul": "Jul", "Aug": "Aug", "Sep": "Sep", "Okt": "Oct",
        "Nov": "Nov", "Dez": "Dec"
    }

    month = german_to_english_months.get(month, month)  # Convert German months to English
    return datetime.strptime(f"{day}-{month}-{year}", "%d-%b-%y")  # Convert to datetime


def get_previous_timestep(date_input):
    """
    Given a datetime object, return the previous timestep.
    The time series contains 01.10 and 01.04 every year.

    :param date_input: datetime object representing the current date
    :return: The previous timestep as a datetime object.
    """
    # Extract the year from the input date
    year = date_input.year

    # Define the two key dates in the year
    date_01_04 = datetime(year, 4, 1)  # 1st April
    date_01_10 = datetime(year, 10, 1)  # 1st October

    # Compare the input date with the two key dates and return the previous one
    if date_input < date_01_04:
        # If before 1st April, return 1st October from the previous year
        previous_date = date_01_10.replace(year=year - 1)
    elif date_input < date_01_10:
        # If between 1st April and 1st October, return 1st April of the same year
        previous_date = date_01_04
    else:
        # If after 1st October, return 1st April of the current year
        previous_date = date_01_10

    return previous_date.strftime("%Y%m%d")


def parse_german_umlaute(text):
    """
    Parse German Umlaute (ä, ö, ü) to their respective representations (ae, oe, ue).

    :param text: The input string containing German Umlaute.
    :return: The string with Umlaute parsed to 'ae', 'oe', 'ue'.
    """
    # Replace Umlaute with corresponding pairs
    text = text.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue")
    text = text.replace("Ä", "Ae").replace("Ö", "Oe").replace("Ü", "Ue")

    return text


def modify_date_acess(date):
    # for the year 2023 the bev data is Accessed with _20230403.gpkg instead of _20230401.gpkg! Manual modification is erQuoiered
    if '202304' in date:
        return '20230403'
    else:
        return date


def generate_raster_urls(url_base, row, channel):
    # manually dEtermined
    series_indicator = {2021: 20221027, 2022: 20221231, 2023: 20240625}

    return f'{url_base}/{series_indicator[row.Jahr]}/{row.ARCHIVNR}_Mosaik_{channel}.tif'


# Define the base path
TU_PC = True
if TU_PC:
    BASE_PATH = r"U:\master\metadata"
else:
    BASE_PATH = "C:/Users/PC/Desktop/TU/Master/MasterThesis/data/orthofotos/all/metadata"

states = gpd.read_file(os.path.join(BASE_PATH, "bundeslaender", "grenzen.shp"))
images = gpd.read_file(os.path.join(BASE_PATH, "orthofotos", "metadata.shp"))

states.drop(columns=['KG_NR', 'KG', 'GKZ', 'PG', 'BKZ', 'PB', 'FA_NR', 'FA', 'GB_KZ', 'GB', 'VA_NR', 'VA', 'ST_KZ', 'ST'], inplace=True)

# Apply TimeStep conversion
images['Date'] = images['beginLifeS'].apply(convert_date)

# Perform spatial join
joined = gpd.sjoin(states, images, how="inner")

intersections, ts = [], []
#urls, filenames = [], []
cadaster_download_url = 'https://data.bev.gv.at/download/Kataster/gpkg/national' #"https://data.bev.gv.at/download/Kataster/shp/"
imagery_download_url = 'https://data.bev.gv.at/download/DOP/'

for _, row in joined.iterrows():
    # extrAct keys
    l_key = row["BL_KZ"]
    img_key = row["ARCHIVNR"]

    # get geometries of each from native table
    l_geom = states.loc[states["BL_KZ"] == l_key, "geometry"].values[0]
    img_geom = images.loc[images["ARCHIVNR"] == img_key, "geometry"].values[0]

    # create attributes for joined table
    intersections.append(shapely.intersection(l_geom, img_geom))

    prev_ts = get_previous_timestep(row.Date)
    ts.append(prev_ts)

    # filename = f'KAT_DKM_{parse_german_umlaute(row["BL"])}_SHP_{prev_ts}'
    # filenames.append(filename)
    #
    # url = '/'.join((cadaster_download_url, prev_ts, f'KAT_DKM_{parse_german_umlaute(row["BL"])}_SHP_{prev_ts}.zip'))
    # url2 = '/'.join((cadaster_download_url, prev_ts, f'{filename}.zip'))
    # urls.append(url)

# add to table
joined["geometry"], joined["prevTime"] = intersections, ts
#joined["urls"], joined["filename"] = urls, filenames

joined.reset_index(inplace=True, drop=True)

# soRt db to process and keep small geometries first
gdf_sorted = joined.assign(area=joined.geometry.area).sort_values(by="area", ascending=False)
for i, rowi in gdf_sorted.iterrows():
    intersecting_geoms = {}

    # get all neighboour geoms which have an intrsection
    for j, rowj in gdf_sorted.iterrows():
        # avoid self intersection
        if i != j:
            if rowi.geometry.intersects(rowj.geometry):
                intersecting_geoms[j] = rowj.geometry

    # set own geometry from (possibly updated geometry)
    gdf_sorted.at[i, "geometry"] = rowi.geometry

    # change the geometry oF all intersecting other geometries by reducing them to the difference.
    # updaTe geometry column in gdf for continous cropping of overlapping geometries
    for k, v in intersecting_geoms.items():
        gdf_sorted.at[k, "geometry"] = shapely.difference(v, rowi.geometry)

# remove absurdly small "linesTring" polygons
for i, rowi in gdf_sorted.iterrows():
    if isinstance(rowi.geometry, shapely.MultiPolygon):
        gdf_sorted.at[i, "geometry"] = shapely.MultiPolygon([P for P in rowi.geometry.geoms if P.area > 0.1])

# remove area attribute as its too large
gdf_sorted.drop(columns=['area', 'index_right'], inplace=True)

gdf_sorted['vector_url'] = gdf_sorted["prevTime"].apply(lambda date: f"{cadaster_download_url}/KAT_DKM_GST_epsg31287_{modify_date_acess(date)}.gpkg")
gdf_sorted['RGB_raster'] = gdf_sorted.apply(lambda row: generate_raster_urls(url_base=imagery_download_url, row=row, channel='RGB'), axis=1)
gdf_sorted['NIR_raster'] = gdf_sorted.apply(lambda row: generate_raster_urls(url_base=imagery_download_url, row=row, channel='NIR'), axis=1)

if TU_PC:
    gdf_sorted = gdf_sorted.set_crs('EPSG:31287')
gdf_sorted.to_file(os.path.join(BASE_PATH, 'intersected_regions', 'ortho_cadastral_matched.shp'))

# with open(os.path.join(BASE_PATH, 'cadastral_download_urls.json'), 'w') as file:
#     json_urls = json.dumps(list(set(urls)))
#     file.write(json_urls)
