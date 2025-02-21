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

import pathlib
import austriadownloader

pathlib.Path("demo/").mkdir(parents=True, exist_ok=True)

request = austriadownloader.DataRequest(
    id = "demo02768",
    lat=47.200434,
    lon=14.673408,
    pixel_size=1.6,
    shape=(4, 1024, 1024), # for RGB just use (3, 1024, 1024)
    outpath="demo/"
)


austriadownloader.download(request)

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
