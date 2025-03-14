"""
Module for loading and managing Austrian cadastral geospatial data.

This module provides functionality to load Austrian cadastral boundaries from
shapefiles stored within the package resources. It implements lazy loading
to optimize memory usage and startup time.
"""

from pathlib import Path
from typing import Final
import geopandas as gpd
import pandas as pd
import importlib.resources

# Constants
RESOURCE_PACKAGE: Final[str] = "austriadownloader.austria_data"
CADASTRAL_FILENAME: Final[str] = "matched_metadata.gpkg"
SAMPLING_FILENAME: Final[str] = "sample_even_download.csv"


def load_cadastral_data() -> gpd.GeoDataFrame:
    """
    Load the Austrian cadastral boundary shapefile into a GeoDataFrame.

    This function loads cadastral boundaries from a shapefile stored in the package
    resources. It includes error handling for common file access issues and
    validates the data source existence.

    Returns:
        gpd.GeoDataFrame: Spatial data containing Austrian cadastral boundaries.

    Raises:
        FileNotFoundError: If the required shapefile cannot be found in resources.
        IOError: If there are problems reading or processing the shapefile.
        ValueError: If the loaded data is invalid or corrupt.
    """
    try:
        with importlib.resources.path(RESOURCE_PACKAGE, CADASTRAL_FILENAME) as resource_path:
            geopackage_path = Path(resource_path).resolve()
            
            if not geopackage_path.exists():
                raise FileNotFoundError(
                    f"Cadastral geopackage not found at: {geopackage_path}"
                )
            
            cadastral_data = gpd.read_file(geopackage_path)
            
            if cadastral_data.empty:
                raise ValueError("Loaded cadastral data is empty")
                
            return cadastral_data
            
    except (FileNotFoundError, ValueError) as e:
        raise e
    except Exception as e:
        raise IOError(f"Failed to load cadastral data: {str(e)}") from e


def load_sampling_data() -> pd.DataFrame:
    """
    Load the Sampling CSV
    Returns:
        pd.DataFrame: Sampling list of points
    Raises:
        FileNotFoundError: If the required shapefile cannot be found in resources.
        IOError: If there are problems reading or processing the shapefile.
        ValueError: If the loaded data is invalid or corrupt.
    """
    try:
        with importlib.resources.path(RESOURCE_PACKAGE, SAMPLING_FILENAME) as resource_path:
            sampling_path = Path(resource_path).resolve()
            if not sampling_path.exists():
                raise FileNotFoundError(
                    f"Sampling csv not found at: {sampling_path}"
                )
            sampled_data = gpd.read_file(sampling_path)
            if sampled_data.empty:
                raise ValueError("Loaded sampling data is empty")
            return sampled_data
    except (FileNotFoundError, ValueError) as e:
        raise e
    except Exception as e:
        raise IOError(f"Failed to load sampling data: {str(e)}") from e

# Lazy-loaded cadastral data
# This will only be loaded when first accessed
#AUSTRIA_CADASTRAL: Final[gpd.GeoDataFrame] = load_cadastral_data()
#AUSTRIA_SAMPLING: Final[pd.DataFrame] = load_sampling_data()
