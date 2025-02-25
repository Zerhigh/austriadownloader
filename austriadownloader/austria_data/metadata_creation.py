import glob
import os
import zipfile
import requests
import shapely
import geopandas as gpd

from datetime import datetime


class MetaDataCreator:
    """
    A class to download, process, and generate metadata for cadastral and imagery datasets.
    """

    def __init__(self, verbose: bool = False):
        """
        Initialize the metadata creator with necessary URLs and parameters.

        :param verbose: Whether to print debug messages.
        """
        self.verbose = verbose

        # BEV Download URLS
        self.cadaster_download_url = 'https://data.bev.gv.at/download/Kataster/gpkg/national'
        self.imagery_download_url = 'https://data.bev.gv.at/download/DOP/'
        self.series_metadata_url = 'https://data.bev.gv.at/download/DOP/20240625/Aktualitaet_Orthophoto_Operate_Farbe_und_Infrarot_2021-2023.zip'

        # file names and folders
        self.extract_folder = "downloaded_data"
        self.metadata_fn = 'matched_metadata.gpkg'

    def convert_date(self, date_str: str) -> datetime:
        """
        Convert a German date string to a datetime object.

        :param date_str: The input date string in 'dd-Mon-yy' format with German month names.
        :return: A datetime object.
        :raises ValueError: If the date string is incorrectly formatted.
        """
        try:
            day, month, year = date_str.split("-")
            german_to_english_months = {
                "Jan": "Jan", "Feb": "Feb", "Mär": "Mar", "Apr": "Apr", "Mai": "May",
                "Jun": "Jun", "Jul": "Jul", "Aug": "Aug", "Sep": "Sep", "Okt": "Oct",
                "Nov": "Nov", "Dez": "Dec"
            }

            month = german_to_english_months.get(month, month)
            return datetime.strptime(f"{day}-{month}-{year}", "%d-%b-%y")
        except Exception as e:
            raise ValueError(f"Error parsing date {date_str}: {e}")

    def get_previous_timestep(self, date_input: datetime) -> str:
        """
        Get the previous timestep from a given date. Timesteps occur on April 1st and October 1st.

        :param date_input: A datetime object.
        :return: A string representing the previous timestep in 'YYYYMMDD' format.
        """
        year = date_input.year
        date_01_04 = datetime(year, 4, 1)
        date_01_10 = datetime(year, 10, 1)

        if date_input < date_01_04:
            previous_date = date_01_10.replace(year=year - 1)
        elif date_input < date_01_10:
            previous_date = date_01_04
        else:
            previous_date = date_01_10

        return previous_date.strftime("%Y%m%d")

    def modify_date_access(self, date: str) -> str:
        """
        Adjust specific date formats due to special cases in BEV data.

        :param date: Date string.
        :return: Adjusted date string.
        """
        return '20230403' if '202304' in date else date

    def generate_raster_urls(self, url_base: str, row, channel: str) -> str:
        """
        Generate raster image URLs.

        :param url_base: Base URL for imagery data.
        :param row: A row of metadata containing the 'Jahr' (year) and 'ARCHIVNR' fields.
        :param channel: The channel type ('RGB' or 'NIR').
        :return: A formatted URL string.
        """
        series_indicator = {2021: 20221027, 2022: 20221231, 2023: 20240625}
        return f'{url_base}/{series_indicator.get(row.Jahr, 20240625)}/{row.ARCHIVNR}_Mosaik_{channel}.tif'

    def clean_folder(self, dst: str) -> None:
        """
        Remove non-GPKG files from the specified folder.

        :param dst: Directory to clean.
        """
        try:
            for file in glob.glob(f'{dst}/*'):
                if not file.endswith('.gpkg'):
                    os.remove(file)
        except Exception as e:
            print(f"Error cleaning folder {dst}: {e}")

    def download_metadata(self) -> None:
        """
        Download and extract metadata ZIP file if necessary.
        """
        zip_path = "data.zip"

        try:
            response = requests.get(self.series_metadata_url, stream=True)
            response.raise_for_status()

            with open(zip_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            if self.verbose:
                print("Metadata Download complete.")

            os.makedirs(self.extract_folder, exist_ok=True)
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(self.extract_folder)
            if self.verbose:
                print("Metadata Extraction complete.")

            os.remove(zip_path)
        except requests.RequestException as e:
            print(f"Failed to download file: {e}")
        except zipfile.BadZipFile as e:
            print(f"Error extracting ZIP file: {e}")

    def process_metadata(self) -> None:
        """
        Process downloaded shapefile metadata, perform geometric corrections, and save it as a GeoPackage.
        """
        if os.path.exists(self.metadata_fn):
            print('Not processing and creating geopackage as file already exists.')
        else:
            try:
                if self.verbose:
                    print('Processing metadata to geopackage')

                shp_files = list(glob.glob(f'{self.extract_folder}/*.shp'))
                if not shp_files:
                    raise FileNotFoundError("No shapefile found in extracted zip data.")

                bev_meta = gpd.read_file(shp_files[0])

                # Sort footprints by area to allow special case of Windischgarten reflight in 2023
                bev_meta = bev_meta.assign(area=bev_meta.geometry.area).sort_values(by="area", ascending=False)
                for i, rowi in bev_meta.iterrows():
                    intersecting_geoms = {}

                    # Get all neighbouring geometries which have an intersection
                    for j, rowj in bev_meta.iterrows():
                        # Avoid self intersection
                        if i != j:
                            if rowi.geometry.intersects(rowj.geometry):
                                intersecting_geoms[j] = rowj.geometry

                    # Reset own geometry from (possibly updated geometry)
                    bev_meta.at[i, "geometry"] = rowi.geometry

                    # Change the geometry of all intersecting other geometries by reducing them to the difference
                    # Update geometry column in gdf for continuous cropping of overlapping geometries
                    for k, v in intersecting_geoms.items():
                        bev_meta.at[k, "geometry"] = shapely.difference(v, rowi.geometry)

                bev_meta.drop(columns=['area'], inplace=True)

                # Update columns with modified and datetime coherent time columns
                bev_meta['Date'] = bev_meta['beginLifeS'].apply(self.convert_date)
                bev_meta['prevTime'] = bev_meta['Date'].apply(self.get_previous_timestep)

                # Generate download urls for vector and raster data (both RGB and NIR)
                bev_meta['vector_url'] = bev_meta.apply(lambda row: f"{self.cadaster_download_url}/KAT_DKM_GST_epsg31287_{self.modify_date_access(row.prevTime)}.gpkg", axis=1)
                bev_meta['RGB_raster'] = bev_meta.apply(lambda row: self.generate_raster_urls(self.imagery_download_url, row, 'RGB'), axis=1)
                bev_meta['NIR_raster'] = bev_meta.apply(lambda row: self.generate_raster_urls(self.imagery_download_url, row, 'NIR'), axis=1)

                # Save as a Geopackage
                bev_meta.to_file(self.metadata_fn, driver='GPKG')
                if self.verbose:
                    print("Metadata processing complete.")
            except Exception as e:
                print(f"Error processing metadata: {e}")


if __name__ == "__main__":
    """
    Execute this script if you want to adapt or update the matched_metadata.gpkg file used for querying raster and vector data. 
    """

    t = MetaDataCreator(verbose=True)
    t.download_metadata()
    t.process_metadata()
