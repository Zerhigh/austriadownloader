import os
import requests
import geopandas as gpd
from urllib.parse import urlparse
from util import run_cmd


class GeoDataDownloader:
    def __init__(self, data_url: str, save_dir: str = 'data'):
        """
        Initializes the GeoDataDownloader class.

        :param data_url: URL to the geospatial data file.
        :param save_dir: Directory to save the downloaded file (default is 'data').
        """
        # self.data_url = data_url
        # self.save_dir = save_dir
        # self.filename = os.path.basename(urlparse(data_url).path)
        # self.save_path = os.path.join(save_dir, self.filename)
        #
        # # Create the directory if it doesn't exist
        # if not os.path.exists(save_dir):
        #     os.makedirs(save_dir)

    def query_cadastral_data(self, geo_url, layer_name, bbox, output_gpkg):
        """Fetches feature count within a bounding box using remote access."""

        dst = "filted_data_ogr.gpkg"
        dst2 = "filted_data_ogr_clipped.gpkg"
        src = f"/vsicurl/{geo_url}"
        command_sql = f'ogr2ogr -f "GPKG" -spat  {bbox[0]} {bbox[1]} {bbox[2]} {bbox[3]} -dialect OGRSQL -sql "SELECT * FROM {layer_name} WHERE NS=41" {dst} {src}'
        run_cmd(command_sql)

        # transform to clipped extent, rasterize with certain resolution
        command_sql = f'ogr2ogr -f "GPKG" -clipsrc  {bbox[0]} {bbox[1]} {bbox[2]} {bbox[3]} {dst2} {dst}'
        run_cmd(command_sql)

    def download_data(self):
        """
        Downloads geospatial data from the specified URL.
        """
        try:
            print(f"Downloading data from {self.data_url}...")
            response = requests.get(self.data_url)
            response.raise_for_status()  # Will raise an HTTPError for bad responses
            with open(self.save_path, 'wb') as f:
                f.write(response.content)
            print(f"Data saved to {self.save_path}")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading data: {e}")

    def load_data(self):
        """
        Loads the downloaded geospatial data into a GeoDataFrame.
        """
        try:
            print(f"Loading data from {self.save_path}...")
            gdf = gpd.read_file(self.save_path)
            return gdf
        except Exception as e:
            print(f"Error loading data: {e}")
            return None

    def save_data(self, gdf, output_path: str):
        """
        Saves the GeoDataFrame to the specified file path.

        :param gdf: The GeoDataFrame to be saved.
        :param output_path: The output file path (e.g., a shapefile or GeoJSON).
        """
        try:
            print(f"Saving data to {output_path}...")
            gdf.to_file(output_path)
            print(f"Data saved successfully to {output_path}")
        except Exception as e:
            print(f"Error saving data: {e}")

    def get_filename(self):
        """
        Returns the filename of the downloaded geospatial data.
        """
        return self.filename

    def get_save_path(self):
        """
        Returns the full path where the geospatial data is saved.
        """
        return self.save_path
