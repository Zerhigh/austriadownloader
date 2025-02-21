import pathlib
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

agg_codes = {'buildings': 41,
             'water': (59, 60),
             'agricultural': (40, 48, 57),
             'forest': (55, 56, 58),
             'railway': 92,
             'roads': (42, 65, 95)}

for names, codes in agg_codes.items():
    print('--------------------------')
    request = austriadownloader.DataRequest(
        id=f"demo_salzburg_{names}",
        lat=47.80599683324095, #47.200434,
        lon=13.036799929282678, #14.673408,
        pixel_size=1.6,
        shape=(4, 1024, 1024),  # for RGB just use (3, 1024, 1024)
        outpath="demo/paper_figures/",
        mask_label=codes,  # Base: Buildings
        create_gpkg=False,
    )

    austriadownloader.download(request, verbose=True)


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
