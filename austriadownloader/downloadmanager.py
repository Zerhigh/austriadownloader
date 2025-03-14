# Parent class: DownloadManager (Manages the overall download process)
import os
import pandas as pd

from typing import Tuple, Optional, Any
from pydantic import BaseModel, Field
from multiprocessing import Pool

import austriadownloader
from austriadownloader.configmanager import ConfigManager
from austriadownloader.downloadstate import DownloadState
#from austriadownloader.data import AUSTRIA_SAMPLING


class DownloadManager(BaseModel):
    config: ConfigManager
    cols: Tuple[str, ...] = ('id', 'aerial', 'cadster', 'num_items', 'area_items')
    tiles: Optional[pd.DataFrame] = Any #AUSTRIA_SAMPLING
    state: pd.DataFrame = Field(
        default_factory=lambda: pd.DataFrame(columns=('id', 'aerial', 'cadster', 'num_items', 'area_items', 'contains_nodata')))

    class Config:
        arbitrary_types_allowed = True  # Allows using non-Pydantic types like pd.DataFrame
        frozen = False  # Allows modifying attributes after initialization

    def start_download(self):
        """Initiates the download process based on the specified method in the configuration."""
        try:
            if self.config.download_method == 'sequential':
                self.download_sequential()
            elif self.config.download_method == 'parallel':
                self.download_parallel()
        except Exception as e:
            print(f"Error downloading tiles: {e}")

    def download_sequential(self):
        """Downloads tiles sequentially, ensuring each tile is processed one at a time.
        Raises:
            ValueError: If no tile data is loaded before initiating the download.
        """
        if self.tiles is None:
            raise ValueError('Error: Download Data was not loaded.')

        for i, row in self.tiles.iterrows():

            tile_state = DownloadState(id=row.id, lat=row.lat, lon=row.lon)

            # if file is already downloaded, skip it
            if os.path.exists(f'{self.config.outpath}/input_{tile_state.id}.tif') and os.path.exists(f'{self.config.outpath}/target_{tile_state}.tif'):
                continue

            download = austriadownloader.download(tile_state, self.config, verbose=self.config.verbose)
            self.state.loc[download.id] = download.get_state()

            # save every 100 steps
            if i % 100 == 0:
                self.state.to_csv(f'{self.config.outpath}/statelog.csv', index=False)

        self.state.to_csv(f'{self.config.outpath}/statelog.csv', index=False)

        return

    def _parallel(self, row):
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

    def download_parallel(self):
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
            results = pool.map(self._parallel, rows)

        # Update manager state after parallel processing
        for tile_id, state in results:
            if state:  # If state is not None, update the manager
                self.state.loc[tile_id] = state

        # Save the state log
        self.state.to_csv(f'{self.config.outpath}/statelog.csv', index=False)
        return
