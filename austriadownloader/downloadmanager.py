# Parent class: DownloadManager (Manages the overall download process)
import pandas as pd
import austriadownloader
from austriadownloader.configmanager import RConfigManager
import os
from pathlib import Path
import pathlib

from pydantic import BaseModel
from typing import Dict, Tuple
from pydantic import BaseModel, field_validator
from tqdm import tqdm
from multiprocessing import Pool, Manager

pathlib.Path("demo/").mkdir(parents=True, exist_ok=True)
pathlib.Path("demo/stratification_output/").mkdir(parents=True, exist_ok=True)


# def validate_id(value: str | int) -> str:
#     return str(value) if isinstance(value, int) else value


class RDownloadManager:

    def __init__(self, config: RConfigManager, cols: Tuple[str] = ('id', 'aerial', 'cadster', 'num_items', 'area_items')):
        """
        Initialize the DownloadManager.
        If a file path is provided, it will automatically load the tile list from the file.
        """
        self.tiles = None
        self.config = config

        self.state: pd.DataFrame = pd.DataFrame(columns=cols)
        self.load_datafile(config.data_path)

    def load_datafile(self, file_path):
        try:
            self.tiles = pd.read_csv(file_path)
            print(f"Successfully loaded {len(self.tiles)} tiles from {file_path}.")
        except Exception as e:
            print(f"Error loading file: {e}")

    def start_download(self):
        try:
            if self.config.download_method == 'sequential':
                self.download_sequential()
            elif self.config.download_method == 'parallel':
                self.download_parallel()
        except Exception as e:
            print(f"Error downloading tiles: {e}")

    def download_sequential(self):
        if self.tiles is None:
            raise ValueError('Error: Download Data was not loaded.')

        for i, row in self.tiles.iterrows():

            tile_state = RDownloadState(id=row.id, lat=row.lat, lon=row.lon)

            # if file is already downloaded, skip it
            if os.path.exists(f'{self.config.outpath}/input_{tile_state.id}.tif') and os.path.exists(f'{self.config.outpath}/target_{tile_state}.tif'):
                continue

            download = austriadownloader.download(tile_state, self.config, verbose=True)
            self.state.loc[download.id] = download.get_state()

            # save every 100 steps
            if i % 100 == 0:
                self.state.to_csv(f'{self.config.outpath}/statelog.csv', index=False)

        self.state.to_csv(f'{self.config.outpath}/statelog.csv', index=False)

        return

    def download_parallel(self):

        return


class RDownloadState(BaseModel):
    id: str | int | float
    lat: float
    lon: float
    raster_download_success: bool = False
    vector_download_success: bool = False
    num_items: int = 0
    area_items: float = 0.0


    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str | int | float) -> str:
        return str(value) if isinstance(value, int) else str(int(value)) if isinstance(value, float) else value

    class Config:
        # This ensures that the model is mutable after initialization (default behavior)
        frozen = False

    def get_state(self) -> Dict[str, any]:
        return {
            'id': self.id,
            'aerial': self.raster_download_success,
            'cadster': self.vector_download_success,
            'num_items': self.num_items,
            'area_items': self.area_items
        }

    def set_raster_failed(self):
        """Marks the raster download as failed."""
        self.raster_download_success = False

    def set_raster_successful(self):
        """Marks the raster download as successful."""
        self.raster_download_success = True

    def check_raster(self) -> bool:
        """
        Checks if the raster download was successful.

        Returns:
            bool: True if raster download was successful, False otherwise.
        """
        return self.raster_download_success

    def set_vector_failed(self):
        """Marks the vector download as failed."""
        self.vector_download_success = False

    def set_vector_successful(self):
        """Marks the vector download as successful."""
        self.vector_download_success = True

    def check_vector(self) -> bool:
        """
        Checks if the vector download was successful.

        Returns:
            bool: True if vector download was successful, False otherwise.
        """
        return self.vector_download_success
