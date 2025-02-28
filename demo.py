import os
import pathlib
import time

import pandas as pd

import austriadownloader

pathlib.Path("demo/").mkdir(parents=True, exist_ok=True)

land_use_codes = {
    41: "Buildings",
    83: "Adjacent building areas",
    59: "Flowing water",
    60: "Standing water",
    61: "Wetlands",
    64: "Waterside areas",
    40: "Permanent crops or gardens",
    48: "Fields, meadows or pastures",
    57: "Overgrown areas",
    55: "Krummholz",
    56: "Forests",
    58: "Forest roads",
    42: "Car parks",
    62: "Low vegetation areas",
    63: "Operating area",
    65: "Roadside areas",
    72: "Cemetery",
    84: "Mining areas, dumps and landfills",
    87: "Rock and scree surfaces",
    88: "Glaciers",
    92: "Rail transport areas",
    95: "Road traffic areas",
    96: "Recreational area",
    52: "Gardens",
    54: "Alps"
}

places = {
    'id_01': {'lat': 48.40086407732648, 'lon': 15.585103157374359},
    'id_02': {'lat': 47.8015341908452, 'lon': 13.031880967377068},
    'id_03': {'lat': 46.674413481011335, 'lon': 13.9611802108645},
    'id_04': {'lat': 47.37133953187826, 'lon': 16.340480406413537},
    'id_05': {'lat': 48.219523815790424, 'lon': 16.40504050915158},
    'id_06': {'lat': 48.10538361840102, 'lon': 16.22915864360271}
}

# Convert to DataFrame
df = pd.DataFrame.from_dict(places, orient='index').reset_index()

# Rename columns for clarity
df.columns = ['id', 'lat', 'lon']
code = 41

for i, row in df.iterrows():
    print('--------------------------')
    t1 = time.time()
    request = austriadownloader.DataRequest(
        id=row.id,
        lat=row.lat,
        lon=row.lon,
        pixel_size=1.6,
        shape=(3, 1024, 1024),  # for RGB just use (3, 1024, 1024)
        outpath=f"demo/output/",
        mask_label=code,  # Base: Buildings
        create_gpkg=False,
        nodata_mode='remove', # or 'remove',
    )

    austriadownloader.download(request, verbose=True)
    print(time.time()-t1)



# places = {'krems': {'lat': 48.40086407732648, 'lon': 15.585103157374359},
#           'salzburg': {'lat': 47.8015341908452, 'lon': 13.031880967377068},
#           'kaernten': {'lat': 46.674413481011335, 'lon': 13.9611802108645},
#           'oberkohl': {'lat': 47.37133953187826, 'lon': 16.340480406413537},
#           'vienna': {'lat': 48.219523815790424, 'lon': 16.40504050915158},
#           }
#
# agg_codes = {'buildings': 41,
#              'agricultural': (40, 48, 57),
#              'forest': (55, 56, 58),
#              'roads': 95}
#
# places = {'test': { 'lat': 48.10538361840102, 'lon': 16.22915864360271}}
# agg_codes = {'forest': (55, 56, 58)}
# Todos
# add metadata generation script

# for place_name, pos in places.items():
#     if not os.path.exists(f'demo/paper_figures/demo_{place_name}'):
#         os.mkdir(f'demo/paper_figures/demo_{place_name}')
#     for names, codes in agg_codes.items():
#         print('--------------------------')
#         request = austriadownloader.DataRequest(
#             id=f"demo_{place_name}_{names}",
#             lat=pos['lat'],
#             lon=pos['lon'],
#             pixel_size=1.6,
#             shape=(3, 1024, 1024),  # for RGB just use (3, 1024, 1024)
#             outpath=f"demo/paper_figures/demo_{place_name}",
#             mask_label=codes,  # Base: Buildings
#             create_gpkg=False,
#             nodata_mode='remove', # or 'remove',
#         )
#
#         austriadownloader.download(request, verbose=True)


# import pathlib
# from austriadownloader.datarequest import ConfigParameters
# pathlib.Path("demo/").mkdir(parents=True, exist_ok=True)
#
# # Example usage
# parameters = ConfigParameters(
#     pixel_size=2.5,
#     image_width=512,
#     lat=xx,
#     lon=xxx,
#     outpath="demo/",  # Ensure this exists
#     multispectral=False
# )
#
# parameters.download()
#
# parameters.aoi
#
#
# import shapely.geometry
# import geopandas as gpd
#
# daa = gpd.GeoDataFrame(geometry=[shapely.geometry.box(*[516143, 470000, 536665, 496558])], crs="EPSG:31287")
# daa.to_file("demo/aoi.geojson", driver="GeoJSON")

#
#
# import rasterio as rio
# ff = "https://data.bev.gv.at/download/DOP//20221231/2022260_Mosaik_RGB.tif"
#
# with rio.open(ff) as src:
#     print(src.profile)
#
#
#
#
