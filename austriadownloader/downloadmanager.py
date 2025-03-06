# Parent class: DownloadManager (Manages the overall download process)
import os
import pandas as pd

from typing import Tuple, Optional
from pydantic import BaseModel, Field
from multiprocessing import Pool

import austriadownloader
from austriadownloader.configmanager import ConfigManager
from austriadownloader.downloadstate import DownloadState
from austriadownloader.data import AUSTRIA_SAMPLING


class DownloadManager(BaseModel):
    config: ConfigManager
    cols: Tuple[str, ...] = ('id', 'aerial', 'cadster', 'num_items', 'area_items')
    tiles: Optional[pd.DataFrame] = AUSTRIA_SAMPLING
    state: pd.DataFrame = Field(
        default_factory=lambda: pd.DataFrame(columns=('id', 'aerial', 'cadster', 'num_items', 'area_items')))

    class Config:
        arbitrary_types_allowed = True  # Allows using non-Pydantic types like pd.DataFrame
        frozen = False  # Allows modifying attributes after initialization

    # def __init__(self, config: ConfigManager, cols: Tuple[str] = ('id', 'aerial', 'cadster', 'num_items', 'area_items')):
    #     """
    #     Initialize the DownloadManager.
    #     If a file path is provided, it will automatically load the tile list from the file.
    #     """
    #     self.tiles = None
    #     self.config = config
    #
    #     self.state: pd.DataFrame = pd.DataFrame(columns=cols)
    #     self.load_datafile(config.data_path)
    #
    # def load_datafile(self, file_path):
    #     try:
    #         self.tiles = pd.read_csv(file_path)
    #         print(f"Successfully loaded {len(self.tiles)} tiles from {file_path}.")
    #     except Exception as e:
    #         print(f"Error loading file: {e}")

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

            tile_state = DownloadState(id=row.id, lat=row.lat, lon=row.lon)

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

    def _parallel(self, row):
        tile_state = DownloadState(id=row.id, lat=row.lat, lon=row.lon)

        # if file is already downloaded, skip it
        if os.path.exists(f'{self.config.outpath}/input_{tile_state.id}.tif') and os.path.exists(
                f'{self.config.outpath}/target_{tile_state}.tif'):
            return tile_state.id, None

        download = austriadownloader.download(tile_state, self.config, verbose=False)

        return download.id, download.get_state()

    def download_parallel(self):
        if self.tiles is None:
            raise ValueError('Error: Download Data was not loaded.')
        # Extract rows as dictionaries for easier parallel processing
        rows = [row for _, row in self.tiles[:10].iterrows()]

        with Pool(processes=os.cpu_count()) as pool:
            results = pool.map(self._parallel, rows)

        # Update manager state after parallel processing
        for tile_id, state in results:
            if state:  # If state is not None, update the manager
                self.state.loc[tile_id] = state

        # Save the state log
        self.state.to_csv(f'{self.config.outpath}/statelog.csv', index=False)
        return
