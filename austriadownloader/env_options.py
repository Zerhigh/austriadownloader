""" HTTP and caching configuration options for austria_server.

This module provides configuration options for rasterio/GDAL to optimize
HTTP requests and caching. The configuration options are used to create 
a rasterio environment that can be used as a context manager to open 
and read mCOG files.
"""

from typing import ClassVar, Literal

from rasterio.env import Env


class AustriaServerConfig:
    """
    Provides predefined configurations for optimizing rasterio/GDAL environments.
    
    Contains two class-level configurations:
    - DEFAULT_CONFIG: GDAL Conservative settings for general-purpose raster operations
    - austria_server_CONFIG: Enhanced configuration optimized for multi-threaded processing
        and better mCOG performance.
    """
    
    # Base configuration balancing compatibility and performance
    DEFAULT_CONFIG: ClassVar[dict[str, str | int]] = {
        "GDAL_HTTP_MERGE_CONSECUTIVE_RANGES": "YES",
        "GDAL_HTTP_MULTIPLEX": "YES",
        "GDAL_DISABLE_READDIR_ON_OPEN": "FALSE",
        "CPL_VSIL_CURL_ALLOWED_EXTENSIONS": "",
        "GDAL_INGESTED_BYTES_AT_OPEN": 16384,
        "GDAL_CACHEMAX": 64,
        "CPL_VSIL_CURL_CACHE_SIZE": 16777216,
        "CPL_VSIL_CURL_CHUNK_SIZE": 16384,
        "VSI_CACHE": "FALSE",
        "VSI_CACHE_SIZE": 26214400,
        "GDAL_BAND_BLOCK_CACHE": "AUTO",
    }

    # Optimized configuration for high-performance multi-threaded reading
    austria_server_CONFIG: ClassVar[dict[str, str | int]] = {
        "GDAL_HTTP_MERGE_CONSECUTIVE_RANGES": "YES",
        "GDAL_HTTP_MULTIPLEX": "YES",
        "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR",
        "CPL_VSIL_CURL_ALLOWED_EXTENSIONS": ".tif,.TIF,.tiff",
        "GDAL_INGESTED_BYTES_AT_OPEN": 393216,  # 384 KB  (optimized for large mCOG headers)
        "GDAL_CACHEMAX": 512,
        "CPL_VSIL_CURL_CACHE_SIZE": 167772160,
        "CPL_VSIL_CURL_CHUNK_SIZE": 10485760,
        "VSI_CACHE": "TRUE",
        "VSI_CACHE_SIZE": 10485760,
        "GDAL_BAND_BLOCK_CACHE": "HASHSET",
        "PROJ_NETWORK": "ON",  # Enable PROJ network for geodetic transformations
    }

    @staticmethod
    def get_env(config: Literal["default", "austria_server"] | dict[str, str] = "austria_server") -> Env:
        """
        Create a configured rasterio environment with optimized GDAL settings.

        Args:
            config: Configuration selection. Can be:
                - "austria_server": Use austria_server_CONFIG (default)
                - "default": Use DEFAULT_CONFIG
                - Custom dictionary: User-provided GDAL options

        Returns:
            Configured rasterio environment context manager

        Examples:
            Basic usage with default austria_server configuration:
            >>> with austria_serverConfig.get_env() as env:
            >>>     with rasterio.open('large_cog.tif') as src:
            >>>         print(src.profile)

            Using conservative defaults:
            >>> with austria_serverConfig.get_env('default') as env:
            >>>     # Perform raster operations
        """
        if config == "austria_server":
            settings = AustriaServerConfig.austria_server_CONFIG
        elif config == "default":
            settings = AustriaServerConfig.DEFAULT_CONFIG
        else:
            settings = config
        return Env(**settings)

    @staticmethod
    def print_config(config: dict) -> None:
        """
        Display configuration settings in a standardized format.

        Args:
            config: Configuration dictionary to display

        Example:
            >>> AustriaServerConfig.print_config(austria_serverConfig.austria_server_CONFIG)
            >>> custom_config = {"GDAL_CACHEMAX": 256}
            >>> austria_serverConfig.print_config(custom_config)
        """
        print("\nRasterio/GDAL Configuration:")
        for key, value in sorted(config.items()):
            print(f"{key}: {value}")


