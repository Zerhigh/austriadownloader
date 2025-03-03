import pathlib
import pandas as pd
import tqdm

import austriadownloader

pathlib.Path("demo/").mkdir(parents=True, exist_ok=True)
pathlib.Path("demo/output/").mkdir(parents=True, exist_ok=True)

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

dem = pd.DataFrame([{'id': 'id_01', 'lat': 48.40086407732648, 'lon': 15.585103157374359},
                    {'id': 'id_02', 'lat': 47.8015341908452, 'lon': 13.031880967377068},
                    {'id': 'id_03', 'lat': 46.674413481011335, 'lon': 13.9611802108645},
                    {'id': 'id_04', 'lat': 47.37133953187826, 'lon': 16.340480406413537},
                    {'id': 'id_05', 'lat': 48.219523815790424, 'lon': 16.40504050915158},
                    {'id': 'id_06', 'lat': 48.10538361840102, 'lon': 16.22915864360271}])

#dem = pd.read_csv('stratified_sample_austria.csv')

code = 41

for i, row in dem.iterrows():
    request = austriadownloader.DataRequest(
        id=row.id,
        lat=row.lat,
        lon=row.lon,
        pixel_size=1.6,
        resample_size=2.5,
        shape=(4, 512, 512),  # for RGB just use (3, 1024, 1024)
        outpath=f"demo/output/",
        mask_label=code,  # Base: Buildings
        create_gpkg=False,
        nodata_mode='flag', # or 'remove',
    )

    austriadownloader.download(request, verbose=True)

