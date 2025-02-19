"""
Geospatial data download and processing module for Austrian cadastral data.

This module provides functionality to download and process both raster and vector
geospatial data based on specified coordinates and parameters. It handles RGB and
RGBN raster data, vector data processing, and rasterization operations.

The module supports various pixel sizes through overview levels and ensures proper
coordinate transformations between different coordinate reference systems (CRS).
"""

from pathlib import Path
from typing import Final, TypeAlias, Literal, Dict, Tuple
import numpy as np
import pandas as pd
import rasterio as rio
import fiona
from pyproj import Transformer
from shapely.geometry import Point
from rasterio.windows import Window

from geoquery.datarequest import DataRequest
from geoquery.data import AUSTRIA_CADASTRAL

# Type aliases for improved readability
Coordinates: TypeAlias = Tuple[float, float]
OverviewLevel: TypeAlias = Literal[-1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
BoundingBox: TypeAlias = Tuple[float, float, float, float]

# Mapping of pixel sizes to overview levels
VALID_OVERVIEWS: Final[Dict[float, OverviewLevel]] = {
    0.2: -1,   # Original resolution
    0.4: 0,    # First overview
    0.8: 1,
    1.6: 2,
    3.2: 3,
    6.4: 4,
    12.8: 5,
    25.6: 6,
    51.2: 7,
    102.4: 8,
    204.8: 9
}

# Constants for coordinate reference systems
WGS84: Final[str] = "EPSG:4326"
AUSTRIA_CRS: Final[str] = "EPSG:31287"
BUILDING_CLASS: Final[int] = 41  # Building class code

def download(request: DataRequest) -> Path:
    """
    Download and process both raster and vector data for the requested area.

    Args:
        request: DataRequest object containing download parameters and specifications.

    Returns:
        Path: Output directory containing the processed data.

    Raises:
        ValueError: If the request contains invalid parameters.
        IOError: If there are issues with file operations.
    """
    try:
        # Download appropriate raster data based on channel count
        if request.shape[0] == 3:
            download_rasterdata_rgb(request)
        elif request.shape[0] == 4:
            download_rasterdata_rgbn(request)
        else:
            raise ValueError(f"Invalid channel count: {request.shape[0]}. Must be 3 (RGB) or 4 (RGBN).")
        
        # Process vector data
        download_vector(request)
        rasterize_vector(request)
        
        return request.outpath
    
    except Exception as e:
        raise IOError(f"Failed to process data request: {str(e)}") from e

def download_vector(request: DataRequest) -> Path:
    """
    Download and process vector data for the specified location.

    Args:
        request: DataRequest object containing location and output specifications.

    Returns:
        Path: Path to the processed vector data.

    Raises:
        ValueError: If the location is outside Austria or invalid.
        IOError: If vector data processing fails.
    """
    try:
        # Transform coordinates to planar CRS
        point_planar = transform_coordinates(
            (request.lon, request.lat),
            from_crs=WGS84,
            to_crs=AUSTRIA_CRS
        )
        point_geometry = Point(*point_planar)
        
        # Find intersecting cadastral data
        vector_data = get_intersecting_cadastral(point_geometry)
        
        # Calculate bounding box
        bbox = calculate_bbox(
            point_planar,
            pixel_size=request.pixel_size,
            shape=request.shape[1:]
        )
        
        # Process and save vector data
        output_path = request.outpath / f"target_{request.id}.gpkg"
        process_vector_data(
            vector_url=vector_data["vector_url"],
            bbox=bbox,
            output_path=output_path
        )
        
        return output_path
    
    except Exception as e:
        raise IOError(f"Vector data processing failed: {str(e)}") from e

def download_rasterdata_rgb(request: DataRequest) -> pd.Series:
    """
    Download and process RGB raster data.

    Args:
        request: DataRequest object containing download specifications.

    Returns:
        pd.Series: Metadata about the downloaded raster data.

    Raises:
        ValueError: If the requested area is invalid.
        IOError: If raster processing fails.
    """
    try:
        point_planar = transform_coordinates(
            (request.lon, request.lat),
            from_crs=WGS84,
            to_crs=AUSTRIA_CRS
        )
        point_geometry = Point(*point_planar)
        
        # Get appropriate raster data
        raster_data = get_intersecting_cadastral(point_geometry)
        overview_level = VALID_OVERVIEWS[request.pixel_size]
        
        process_rgb_raster(
            raster_path=raster_data["RGB_raster"],
            request=request,
            point=(request.lon, request.lat),
            overview_level=overview_level
        )
        
        return raster_data
    
    except Exception as e:
        raise IOError(f"RGB raster processing failed: {str(e)}") from e

def download_rasterdata_rgbn(request: DataRequest) -> pd.Series:
    """
    Download and process RGBN (RGB + Near Infrared) raster data.

    Args:
        request: DataRequest object containing download specifications.

    Returns:
        pd.Series: Metadata about the downloaded raster data.

    Raises:
        ValueError: If the requested area is invalid.
        IOError: If raster processing fails.
    """
    try:
        point_planar = transform_coordinates(
            (request.lon, request.lat),
            from_crs=WGS84,
            to_crs=AUSTRIA_CRS
        )
        point_geometry = Point(*point_planar)
        
        # Get appropriate raster data
        raster_data = get_intersecting_cadastral(point_geometry)
        overview_level = VALID_OVERVIEWS[request.pixel_size]
        
        process_rgbn_raster(
            rgb_path=raster_data["RGB_raster"],
            nir_path=raster_data["NIR_raster"],
            request=request,
            point=(request.lon, request.lat),
            overview_level=overview_level
        )
        
        return raster_data
    
    except Exception as e:
        raise IOError(f"RGBN raster processing failed: {str(e)}") from e


# Helper functions

def transform_coordinates(
    point: Coordinates,
    from_crs: str,
    to_crs: str
) -> Coordinates:
    """Transform coordinates between coordinate reference systems."""
    transformer = Transformer.from_crs(from_crs, to_crs, always_xy=True)
    return transformer.transform(*point)

def get_intersecting_cadastral(point_geometry: Point) -> pd.Series:
    """Get cadastral data intersecting with the given point."""
    intersecting = AUSTRIA_CADASTRAL[
        AUSTRIA_CADASTRAL.intersects(point_geometry, align=True)
    ]
    if intersecting.empty:
        raise ValueError("Location is outside Austria's cadastral boundaries")
    return intersecting.iloc[0]

def calculate_bbox(
    point: Coordinates,
    pixel_size: float,
    shape: Tuple[int, int]
) -> BoundingBox:
    """Calculate bounding box for the given point and dimensions."""
    x_size = (pixel_size * shape[1]) // 2
    y_size = (pixel_size * shape[0]) // 2
    return (
        point[0] - x_size,
        point[1] - y_size,
        point[0] + x_size,
        point[1] + y_size
    )

def process_vector_data(
    vector_url: str,
    bbox: BoundingBox,
    output_path: Path
) -> None:
    """Process and save vector data within the specified bounding box."""
    with fiona.open(vector_url, layer="NFL") as src:
        profile = src.profile
        filtered_features = [
            feat for feat in src.filter(bbox=bbox)
            if feat["properties"].get("NS") == BUILDING_CLASS
        ]
        
        with fiona.open(output_path, "w", **profile) as dst:
            dst.writerecords(filtered_features)

def process_rgb_raster(
    raster_path: str,
    request: DataRequest,
    point: Coordinates,
    overview_level: int
) -> None:
    """Process and save RGB raster data."""
    with rio.open(raster_path, overview_level=overview_level) as src:
        window, profile = prepare_raster_window(src, point, request)
        data = src.read(window=window)
        
        save_raster_data(
            data=data,
            profile=profile,
            request=request,
            window=window,
            transform=src.transform
        )

def process_rgbn_raster(
    rgb_path: str,
    nir_path: str,
    request: DataRequest,
    point: Coordinates,
    overview_level: int
) -> None:
    """Process and save RGBN raster data."""
    with rio.open(rgb_path, overview_level=overview_level) as src_rgb:
        window, profile = prepare_raster_window(src_rgb, point, request)
        data_rgb = src_rgb.read(window=window)
        
        with rio.open(nir_path, overview_level=overview_level) as src_nir:
            data_nir = src_nir.read(window=window)
            data_total = np.concatenate([data_rgb, data_nir], axis=0)
            
            profile.update({'count': 4})
            save_raster_data(
                data=data_total,
                profile=profile,
                request=request,
                window=window,
                transform=src_rgb.transform
            )

def prepare_raster_window(
    src: rio.DatasetReader,
    point: Coordinates,
    request: DataRequest
) -> Tuple[Window, Dict]:
    """Prepare raster window and profile for data extraction."""
    point_raster = transform_coordinates(
        point,
        from_crs=WGS84,
        to_crs=src.crs
    )
    
    y, x = src.index(*point_raster)
    window = Window(
        x - request.shape[2] // 2,
        y - request.shape[1] // 2,
        request.shape[2],
        request.shape[1]
    )
    
    profile = src.profile.copy()
    profile.update({
        'height': request.shape[1],
        'width': request.shape[2],
        'compress': 'DEFLATE',
        'driver': 'GTiff',
        'photometric': None
    })
    
    return window, profile

def save_raster_data(
    data: np.ndarray,
    profile: Dict,
    request: DataRequest,
    window: Window,
    transform: rio.Affine
) -> None:
    """Save raster data to disk."""
    profile.update({
        'transform': rio.windows.transform(window, transform)
    })
    
    output_path = request.outpath / f"input_{request.id}.tif"
    with rio.open(output_path, "w", **profile) as dst:
        dst.write(data)

def rasterize_vector(request: DataRequest) -> None:
    """
    Rasterize vector data based on the request parameters.
    
    This is a placeholder for the rasterization implementation.
    """
    pass  # Implementation needed