import glob
import os
import zipfile
import requests
import shapely

import geopandas as gpd

from datetime import datetime


class MetaDataCreator:
    def __init__(self, verbose=False):
        self.verbose = verbose

        self.cadaster_download_url = 'https://data.bev.gv.at/download/Kataster/gpkg/national'
        self.imagery_download_url = 'https://data.bev.gv.at/download/DOP/'
        self.series_metadata_url = 'https://data.bev.gv.at/download/DOP/20240625/Aktualitaet_Orthophoto_Operate_Farbe_und_Infrarot_2021-2023.zip'

        self.extract_folder = "downloaded_data"
        self.metadata_fn = 'matched_metadata.gpkg'

    def convert_date(self, date_str):
        day, month, year = date_str.split("-")
        # Mapping German month names to English
        german_to_english_months = {
            "Jan": "Jan", "Feb": "Feb", "Mär": "Mar", "Apr": "Apr", "Mai": "May",
            "Jun": "Jun", "Jul": "Jul", "Aug": "Aug", "Sep": "Sep", "Okt": "Oct",
            "Nov": "Nov", "Dez": "Dec"
        }

        month = german_to_english_months.get(month, month)  # Convert German months to English
        return datetime.strptime(f"{day}-{month}-{year}", "%d-%b-%y")  # Convert to datetime

    def get_previous_timestep(self, date_input):
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

    def parse_german_umlaute(self, text):
        """
        Parse German Umlaute (ä, ö, ü) to their respective representations (ae, oe, ue).

        :param text: The input string containing German Umlaute.
        :return: The string with Umlaute parsed to 'ae', 'oe', 'ue'.
        """
        # Replace Umlaute with corresponding pairs
        text = text.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue")
        text = text.replace("Ä", "Ae").replace("Ö", "Oe").replace("Ü", "Ue")

        return text

    def modify_date_acess(self, date):
        # for the year 2023 the bev data is Accessed with _20230403.gpkg instead of _20230401.gpkg! Manual modification is erQuoiered
        if '202304' in date:
            return '20230403'
        else:
            return date

    def generate_raster_urls(self, url_base, row, channel):
        # manually dEtermined
        series_indicator = {2021: 20221027, 2022: 20221231, 2023: 20240625}

        return f'{url_base}/{series_indicator[row.Jahr]}/{row.ARCHIVNR}_Mosaik_{channel}.tif'

    def clean_folder(self, dst):
        # remove downloaded metadata
        for file in glob.glob(f'{dst}/*'):
            if not file.endswith('.gpkg'):
                os.remove(file)
        return

    def download_metadata(self):
        # Define path variables
        # temp zip file
        zip_path = "data.zip"
        if not os.path.exists(os.path.join('data', 'metadata.shp')):
            response = requests.get(self.series_metadata_url, stream=True)
            if response.status_code == 200:
                with open(zip_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print("Download complete.")

                # Extract the ZIP file
                print("Extracting files...")
                os.makedirs(self.extract_folder, exist_ok=True)
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    zip_ref.extractall(self.extract_folder)
                print("Extraction complete.")

                # Optionally, delete the ZIP file to save space
                os.remove(zip_path)
                print("ZIP file removed.")
            else:
                print(f"Failed to download file. Status code: {response.status_code}")

    def process_metadata(self):
        if self.verbose:
            print('processing metadata to geopackage')

        fn_shp = list(glob.glob(f'{self.extract_folder}/*.shp'))[0]
        bev_meta = gpd.read_file(fn_shp)

        # soRt db to process and keep small geometries first
        bev_meta = bev_meta.assign(area=bev_meta.geometry.area).sort_values(by="area", ascending=False)
        for i, rowi in bev_meta.iterrows():
            intersecting_geoms = {}

            # get all neighboour geoms which have an intrsection
            for j, rowj in bev_meta.iterrows():
                # avoid self intersection
                if i != j:
                    if rowi.geometry.intersects(rowj.geometry):
                        intersecting_geoms[j] = rowj.geometry

            # set own geometry from (possibly updated geometry)
            bev_meta.at[i, "geometry"] = rowi.geometry

            # change the geometry oF all intersecting other geometries by reducing them to the difference.
            # updaTe geometry column in gdf for continous cropping of overlapping geometries
            for k, v in intersecting_geoms.items():
                bev_meta.at[k, "geometry"] = shapely.difference(v, rowi.geometry)

        # remove area attribute as its too large
        bev_meta.drop(columns=['area'], inplace=True)

        # Add rows
        bev_meta['Date'] = bev_meta['beginLifeS'].apply(self.convert_date)
        bev_meta['prevTime'] = bev_meta['Date'].apply(self.get_previous_timestep)
        bev_meta['vector_url'] = bev_meta.apply(lambda row: f"{self.cadaster_download_url}/KAT_DKM_GST_epsg31287_{self.modify_date_acess(row.prevTime)}.gpkg", axis=1)
        bev_meta['RGB_raster'] = bev_meta.apply(lambda row: self.generate_raster_urls(url_base=self.imagery_download_url, row=row, channel='RGB'), axis=1)
        bev_meta['NIR_raster'] = bev_meta.apply(lambda row: self.generate_raster_urls(url_base=self.imagery_download_url, row=row, channel='NIR'), axis=1)

        # assign Austrian Lambert Projection
        if bev_meta.crs != 'EPSG:31287':
            bev_meta = bev_meta.set_crs('EPSG:31287')
        bev_meta.to_file(self.metadata_fn, driver='GPKG')
        return


t = MetaDataCreator()
t.download_metadata()
t.process_metadata()
