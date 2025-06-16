# Parent class: DownloadManager (Manages the overall download process)
import datetime
import os
import pathlib

import yaml
import pandas as pd

from typing import Tuple, Optional, Dict
from pydantic import BaseModel, Field, model_validator
from multiprocessing import Pool
from tqdm import tqdm

import austriadownloader
from austriadownloader.configmanager import ConfigManager
from austriadownloader.downloadstate import DownloadState


class DownloadManager(BaseModel):
    config: ConfigManager
    state: pd.DataFrame = None # = Field(default_factory=lambda: pd.DataFrame(columns=('id', 'aerial', 'cadster', 'num_items', 'area_items', 'contains_nodata')))
    #cols: Tuple[str, ...] = ('id', 'aerial', 'cadster', 'num_items', 'area_items')
    tiles: pd.DataFrame = None

    log: Dict = {}

    class Config:
        arbitrary_types_allowed = True  # Allows using non-Pydantic types like pd.DataFrame
        frozen = False  # Allows modifying attributes after initialization

    @model_validator(mode="before")
    @classmethod
    def load_tiles(cls, data):
        """Reads the DataFrame from the path stored in config and assigns it to tiles."""
        if isinstance(data, dict) and 'config' in data:
            config = data["config"]
            if isinstance(config, ConfigManager) and hasattr(config, "data_path"):
                data["tiles"] = pd.read_csv(config.data_path)

        # If its set, validate remapping again
        if config.mask_remapping is not None and set(config.mask_label) != set(config.mask_remapping.keys()):
            raise Warning(f"Selected mask_label ({config.mask_label}) is not identical to provided mask_remapping labels ({list(config.mask_remapping.keys())})! "
                          f"This will lead to unexpected behaviour if not corrected.")
        return data

    def add_row(self, new_data: dict):
        """
        Adds a new row to the DataFrame. If it doesn't exist, it initializes it.
        :param new_data: Dictionary containing column names as keys and values as row data.
        """
        new_row = pd.DataFrame([new_data])

        if self.state is None:
            self.state = new_row
        else:
            self.state = pd.concat([self.state, new_row], ignore_index=True)

    def start_download(self):
        """Initiates the download process based on the specified method in the configuration."""
        try:
            # save config file
            save_config = {k: str(v) if isinstance(v, pathlib.Path) else v for k, v in self.config.config_data.items()}
            with open(pathlib.Path(self.config.config_data['outpath']) / 'rgb.yml', "w") as f:
                yaml.safe_dump(save_config, f, sort_keys=False)

            # add logging info
            self.log['Start Time'] = datetime.datetime.now()
            self.log['Errors'] = None

            if self.config.download_method == 'sequential':
                self.download_sequential()
            elif self.config.download_method == 'parallel':
                self.download_parallel()
        except Exception as e:
            self.log['Errors'] = e
            self.end_of_download()
            print(f"Error downloading tiles: {e}")

    def end_of_download(self):
        # save downlaod log
        self.log['End Time'] = datetime.datetime.now()
        self.log['Duration'] = str(self.log['End Time'] - self.log['Start Time'])
        self.log['Number of Processed tiles'] = len(self.tiles)

        with open(pathlib.Path(self.config.config_data['outpath']) / 'log.yml', "w") as f:
            yaml.safe_dump(self.log, f, sort_keys=False)

        # Save the state log
        self.state.to_csv(f'{self.config.outpath}/statelog.csv', index=False)

        return

    def download_sequential(self) -> None:
        """Downloads tiles sequentially, ensuring each tile is processed one at a time.
        Raises:
            ValueError: If no tile data is loaded before initiating the download.
        """
        if self.tiles is None:
            raise ValueError('Error: Download Data was not loaded.')

        for i, row in tqdm(self.tiles.iterrows()):
            tile_state = DownloadState(id=row.id, lat=row.lat, lon=row.lon)

            # if file is already downloaded, skip it
            if os.path.exists(f'{self.config.outpath}/input_{tile_state.id}.tif') and os.path.exists(f'{self.config.outpath}/target_{tile_state}.tif'):
                continue

            download = austriadownloader.download(tile_state, self.config, verbose=self.config.verbose)
            self.add_row(download.get_state())

            # save every 100 steps
            if i % 100 == 0:
                self.state.to_csv(f'{self.config.outpath}/statelog.csv', index=False)

        self.end_of_download()
        return

    def _parallel(self, row: pd.Series) -> Tuple[str, Dict[str, any] | None]:
        """Handles downloading a single tile in parallel processing mode.
        Args:
            row (pd.Series): A row from the tile dataset containing tile information.
        Returns:
            Tuple[str, Optional[dict]]: The tile ID and its download state if successful, otherwise None.
        """
        tile_state = DownloadState(id=row.id, lat=row.lat, lon=row.lon)

        # if file is already downloaded, skip it
        if os.path.exists(f'{self.config.outpath}/input_{tile_state.id}.tif') and os.path.exists(
                f'{self.config.outpath}/target_{tile_state}.tif'):
            return tile_state.id, None

        download = austriadownloader.download(tile_state, self.config, verbose=self.config.verbose)

        return download.id, download.get_state()

    def download_parallel(self) -> None:
        """Downloads tiles in parallel using multiprocessing for improved performance.
        Raises:
            ValueError: If no tile data is loaded before initiating the download.
        """
        if self.tiles is None:
            raise ValueError('Error: Download Data was not loaded.')

        if self.config.verbose:
            print("Verbosity with parallel loading will result in no pretty-prints as outputs are created by pooled download requests.")

        # Extract rows as dictionaries for easier parallel processing
        rows = [row for _, row in self.tiles.iterrows()]

        with Pool(processes=os.cpu_count()) as pool:
            results = list(tqdm(pool.imap_unordered(self._parallel, rows), total=len(rows), desc="Processing"))

        # Update manager state after parallel processing
        for tile_id, state in results:
            if state:  # If state is not None, update the manager
                self.add_row(state)

        self.end_of_download()
        return
