"""
Geospatial data download and processing module for Austrian cadastral data.

This module provides functionality to download and process both raster and vector
geospatial data based on specified coordinates and parameters. It handles RGB and
RGBN raster data, vector data processing, and rasterization operations.

The module supports various pixel sizes through overview levels and ensures proper
coordinate transformations between different coordinate reference systems (CRS).
"""
import fiona
import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio as rio
import warnings

from typing import Final, TypeAlias, Literal, Dict, Tuple, Optional
from pyproj import Transformer
from rasterio.features import rasterize
from rasterio.windows import Window
from shapely.geometry import Point, shape

#from austriadownloader.data import AUSTRIA_CADASTRAL
from austriadownloader.configmanager import ConfigManager
from austriadownloader.downloadmanager import DownloadState

# Type aliases for improved readability
Coordinates: TypeAlias = Tuple[float, float]
OverviewLevel: TypeAlias = Literal[-1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
BoundingBox: TypeAlias = Tuple[float, float, float, float]

# Mapping of pixel sizes to overview levels
VALID_OVERVIEWS: Final[Dict[float, OverviewLevel]] = {
    0.2: -1,  # Original resolution
    0.4: 0,  # First overview
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


# BUILDING_CLASS: Final[int] = 92  # Building class code
def download(tile_state: DownloadState, config: ConfigManager, verbose: bool) -> DownloadState:
    """
    Download and process both raster and vector data for the requested area.

    Args:
        tile_state: DataRequest object containing download parameters and specifications.
        config: RConfigManager object.
        verbose: bool triggers output

    Returns:
        Path: Output directory containing the processed data.

    Raises:
        ValueError: If the request contains invalid parameters.
        IOError: If there are issues with file operations.
    """
    # using environment options is disabled for now
    # with AustriaServerConfig().get_env("default"):
    try:
        if verbose:
            print(f'Tile: {tile_state.id}')

        # Transform coordinates to planar CRS
        point_planar = transform_coordinates(
            (tile_state.lon, tile_state.lat),
            from_crs=WGS84,
            to_crs=AUSTRIA_CRS
        )
        point_geometry = Point(*point_planar)

        # Find intersecting meta data
        meta_data = get_intersecting_cadastral(point_geometry)

        # Point has been sampeld out of queryable area of Austria
        if meta_data is None:
            tile_state.set_raster_failed()
            tile_state.set_vector_failed()
            return tile_state

        # Download appropriate raster data based on channel count
        if config.shape[0] == 3:
            if verbose:
                print("    Downloading RGB raster data.")
            download_rasterdata_rgb(tile_state, config, meta_data)
        elif config.shape[0] == 4:
            if verbose:
                print("    Downloading RGB and NIR raster data.")
            download_rasterdata_rgbn(tile_state, config, meta_data)
        else:
            raise ValueError(f"    Invalid channel count: {config.shape[0]}. Must be 3 (RGB) or 4 (RGB and NIR).")

        # Process vector data
        if tile_state.check_raster():
            if verbose:
                print(f"    Downloading vector cadastral data: Code(s): {config.mask_label}")
            download_vector(tile_state, config, point_planar, meta_data)
            if verbose:
                print(f"    Finished downloading and processing data to: {config.outpath}/*_{tile_state.id}.tif")
        else:
            if verbose:
                print(f'    Did not download raster and vector data as no raster was accessed. Likely due to NoData values and {config.nodata_mode} set as "remove"')

        return tile_state

    except Exception as e:
        raise IOError(f"Failed to process data request: {str(e)}") from e


def download_vector(tile_state: DownloadState, config: ConfigManager, point_planar: Coordinates, vector_data: pd.Series) -> None:
    """
    Download and process vector data for the specified location.

    Args:
        tile_state: Class for keeping track of Download Processes
        config: RConfigManager object.
        point_planar: Coordinate tuple
        vector_data: Metadata Series with download URL

    Returns:
        Path: Path to the processed vector data.

    Raises:
        ValueError: If the location is outside Austria or invalid.
        IOError: If vector data processing fails.
    """
    try:
        # Calculate bounding box: define rasterization and extent size
        bbox_pixel_size = config.pixel_size
        if config.resample_size is not None:
            bbox_pixel_size = config.resample_size

        bbox = calculate_bbox(
            point_planar,
            pixel_size=bbox_pixel_size,
            shape=config.shape[1:]
        )

        # Process and save vector data
        process_vector_data(
            vector_url=vector_data["vector_url"],
            bbox=bbox,
            config=config,
            tile_state=tile_state
        )

        tile_state.set_vector_successful()
        return

    except Exception as e:
        tile_state.set_vector_failed()
        raise IOError(f"Vector data processing failed: {str(e)}") from e


def download_rasterdata_rgb(tile_state: DownloadState, config: ConfigManager, raster_data: pd.Series) -> pd.Series:
    """
    Download and process RGB raster data.

    Args:
        tile_state: Class for keeping track of Donwload Processes
        config: RConfigManager object.
        raster_data: Metadata Series with download URL

    Returns:
        pd.Series: Metadata about the downloaded raster data.

    Raises:
        ValueError: If the requested area is invalid.
        IOError: If raster processing fails.
    """
    try:

        overview_level = VALID_OVERVIEWS[config.pixel_size]

        point = (tile_state.lon, tile_state.lat)
        raster_hw = config.shape[1]  # assumption raster is squaRe

        with rio.open(raster_data["RGB_raster"], overview_level=overview_level) as src:
            window, profile = prepare_raster_window(src, point, config)
            data = src.read(window=window)

            # If the data is not already of shape of the blocksize, pad it
            data = pad_tensor(data, tile_state, href=profile["height"], wref=profile["width"], nodata_method=config.nodata_mode)

            if data is None:
                # creation option for nodata is on remove
                tile_state.set_raster_failed()
                print(
                    f'Skipping raster {config.outpath} as NoData values were contained and nodata_mode={config.nodata_mode}')
            else:
                # apply resampling
                if config.resample_size is not None:
                    data = np.array([
                        cv2.resize(data[channel], (raster_hw, raster_hw), interpolation=cv2.INTER_LINEAR)
                        for channel in range(data.shape[0])
                    ])

                    # change window: height and width
                    window = Window(window.col_off, window.row_off, raster_hw, raster_hw)

                    # Scale factor: 1 / (old pixel size  / new pixel size) -> division as Affine doesnt accept division
                    scale_factor = 1 / (src.transform[0] / config.resample_size)

                    # calculate neW trafo based on new window
                    new_transform = rio.windows.transform(window, src.transform)
                    trafo = new_transform * new_transform.scale(scale_factor, scale_factor)

                    # update profiler
                    profile.update({
                        'height': raster_hw,
                        'width': raster_hw
                    })
                else:
                    # define normal transformation here (no upsampling done)
                    trafo = rio.windows.transform(window, src.transform)

                tile_state.set_raster_successful()
                profile.update({'nodata': config.nodata_value})
                save_raster_data(
                    data=data,
                    profile=profile,
                    config=config,
                    tile_state=tile_state,
                    transform=trafo
                )

        return raster_data

    except Exception as e:
        raise IOError(f"RGB raster processing failed: {str(e)}") from e


def download_rasterdata_rgbn(tile_state: DownloadState, config: ConfigManager, raster_data: pd.Series) -> pd.Series:
    """
    Download and process RGBN (RGB + Near Infrared) raster data.

    Args:
        tile_state: Class for keeping track of Donwload Processes
        config: RConfigManager object.
        raster_data: Metadata Series with download URL

    Returns:
        pd.Series: Metadata about the downloaded raster data.

    Raises:
        ValueError: If the requested area is invalid.
        IOError: If raster processing fails.
    """
    try:

        overview_level = VALID_OVERVIEWS[config.pixel_size]

        point = (tile_state.lon, tile_state.lat)
        raster_hw = config.shape[1]  # assumption raster is squaRe

        with rio.open(raster_data["RGB_raster"], overview_level=overview_level) as src_rgb:
            window, profile = prepare_raster_window(src_rgb, point, config)
            data_rgb = src_rgb.read(window=window)

            with rio.open(raster_data["NIR_raster"], overview_level=overview_level) as src_nir:
                data_nir = src_nir.read(window=window)
                data_total = np.concatenate([data_rgb, data_nir], axis=0)

                # If the data is not already of shape of the blocksize, pad it
                data_total = pad_tensor(data_total, tile_state, href=profile["height"], wref=profile["width"],
                                        nodata_method=config.nodata_mode)

                if data_total is None:
                    # creation option for nodata is on remove
                    tile_state.set_raster_failed()
                    print(
                        f'Removed raster {config.outpath} as NoData values were contained and nodata_mode={config.nodata_mode}')
                else:
                    # resample and resize
                    if config.resample_size is not None:
                        data_total = np.array([
                            cv2.resize(data_total[channel], (raster_hw, raster_hw),
                                       interpolation=cv2.INTER_LINEAR)
                            for channel in range(data_total.shape[0])
                        ])

                        # change window: height and width
                        window = Window(window.col_off, window.row_off, raster_hw, raster_hw)

                        # Scale factor: 1 / (old pixel size  / new pixel size) -> division as Affine doesnt accept division
                        scale_factor = 1 / (src_rgb.transform[0] / config.resample_size)

                        # calculate neW trafo based on new window
                        new_transform = rio.windows.transform(window, src_rgb.transform)
                        trafo = new_transform * new_transform.scale(scale_factor, scale_factor)

                        # update profiler
                        profile.update({
                            'height': raster_hw,
                            'width': raster_hw
                        })
                    else:
                        # define normal transformation here (no upsampling done)
                        trafo = rio.windows.transform(window, src_rgb.transform)

                    tile_state.set_raster_successful()
                    profile.update({'count': 4, 'nodata': config.nodata_value})
                    save_raster_data(
                        data=data_total,
                        profile=profile,
                        config=config,
                        tile_state=tile_state,
                        transform=trafo
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


def get_intersecting_cadastral(point_geometry: Point) -> pd.Series | None:
    """Get cadastral data intersecting with the given point."""
    intersecting = AUSTRIA_CADASTRAL[
        AUSTRIA_CADASTRAL.intersects(point_geometry, align=True)
    ]
    if intersecting.empty:
        warnings.warn("Skipping: Location is outside Austria's cadastral boundaries", UserWarning)
        return None
        # raise ValueError("Location is outside Austria's cadastral boundaries")
    else:
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
        config: ConfigManager,
        tile_state: DownloadState
) -> None:
    """Process and save vector data within the specified bounding box."""

    # Without file extension!
    fp = config.outpath / f"{config.outfile_prefixes['vector']}_{tile_state.id}"

    with fiona.open(vector_url, layer="NFL") as src:
        # conversion to gdf: removed any property values
        filtered_features = [
            {"geometry": shape(feat["geometry"])}
                for feat in src.filter(bbox=bbox)
                    if feat["properties"].get("NS") in config.mask_label
        ]

        # add number of objects to state managEr
        tile_state.num_items = len(filtered_features)

        # Objects ahve been found and will be transformed into raster
        if len(filtered_features) > 0:
            gdf = gpd.GeoDataFrame(filtered_features, crs=src.crs)

            # Rasterize the geometries into the raster
            # change this and add the info to the state_manager
            with rio.open(config.outpath / f"{config.outfile_prefixes['raster']}_{tile_state.id}.tif") as img_src:
                # convert geoemtries to raster specific crs
                gdf.to_crs(crs=img_src.crs, inplace=True)

                # if requested provide transformed vector file
                if config.create_gpkg:
                    gdf.to_file(fp.with_suffix(".gpkg"), driver='GPKG', layer='NFL')
                shapes = [(geom, 1) for geom in gdf.geometry]  # Assign value 1 to features
                binary_raster = rasterize(shapes, out_shape=config.shape[1:], transform=img_src.transform,
                                          fill=0)

                # add the pixel number to state manager
                set_pixels = np.count_nonzero(binary_raster == 1)
                tile_state.set_pixels = set_pixels
                # psize = config.pixel_size if config.resample_size is None else config.resample_size
                #tile_state.area_items = round(psize**2 * set_pixels, 2)

                # Save the rasterized binary image
                with rio.open(
                        fp=fp.with_suffix(".tif"),
                        mode="w+",
                        driver="GTiff",
                        height=config.shape[1],
                        width=config.shape[1],
                        count=1,
                        dtype=np.uint8,
                        crs=img_src.crs,
                        transform=img_src.transform
                ) as dst:
                    dst.write(binary_raster, 1)
        # write empty image
        else:
            print(f'    No results for class {config.mask_label} at lat: {tile_state.lat} // lon: {tile_state.lon}')
            with rio.open(config.outpath / f"input_{tile_state.id}.tif") as img_src:
                binary_raster = np.zeros((config.shape[1], config.shape[1]), dtype=np.uint8)

                # Save the rasterized binary image
                with rio.open(
                        fp=fp.with_suffix(".tif"),
                        mode="w+",
                        driver="GTiff",
                        height=config.shape[1],
                        width=config.shape[1],
                        count=1,
                        dtype=np.uint8,
                        crs=img_src.crs,
                        transform=img_src.transform
                ) as dst:
                    dst.write(binary_raster, 1)
    return


def prepare_raster_window(
        src: rio.DatasetReader,
        point: Coordinates,
        config: ConfigManager
) -> Tuple[Window, Dict]:
    """Prepare raster window and profile for data extraction."""
    point_raster = transform_coordinates(
        point,
        from_crs=WGS84,
        to_crs=src.crs
    )

    # if request.resample_size is not None:
    y, x = src.index(*point_raster)

    h, w = config.shape[1:]
    if config.resample_size is not None:
        # reshape Windpow for inceades coverage area
        scaling_factor = config.resample_size / config.pixel_size
        adjusted_window_size = int(config.shape[1] * scaling_factor)
        window = Window(
            x - adjusted_window_size // 2,  # Start column (x)
            y - adjusted_window_size // 2,  # Start row (y)
            adjusted_window_size,  # Window width (adjusted for resolution)
            adjusted_window_size  # Window height (adjusted for resolution)
        )
        h, w = adjusted_window_size, adjusted_window_size
    else:
        window = Window(
            x - config.shape[2] // 2,
            y - config.shape[1] // 2,
            config.shape[2],
            config.shape[1]
        )

    profile = src.profile.copy()
    profile.update({
        'height': h,
        'width': w,
        'compress': 'DEFLATE',
        'driver': 'GTiff',
        'photometric': None
    })

    return window, profile


def save_raster_data(
        data: np.ndarray,
        profile: Dict,
        config: ConfigManager,
        tile_state: DownloadState,
        transform: rio.Affine,
) -> None:
    """Save raster data to disk."""
    profile.update({
        'transform': transform,  # rio.windows.transform(window, transform),
        'tiled': True,
        'nodata': 0,
        'blockxsize': 256,
        'blockysize': 256
    })

    output_path = config.outpath / f"{config.outfile_prefixes['raster']}_{tile_state.id}.tif"
    with rio.open(output_path, "w", **profile) as dst:
        dst.write(data)


def pad_tensor(data: np.ndarray, tile_state: DownloadState, href: int = 512, wref: int = 512, nodata_method: str = 'flag') -> Optional[np.ndarray]:
    """
    Pads a (3, H, W) tensor to (3, href, wref) by filling with zeros.

    Args:
        :param data: Input tensor of shape (3, H, W).
        :param tile_state: state
        :param nodata_method: Either 'flag' or 'remove'
        :param href: Padding image size.
        :param wref: Padding image size.

    Returns:
        np.ndarray: Zero-padded tensor of shape (3, href, wref).
    """
    c, h, w = data.shape

    if h == href and w == wref:
        return data  # No changes needed

    # check for nodata_method
    if nodata_method == 'flag':
        print(f'Queryied window contains NoData values, set to: 0')

        tile_state.contains_nodata = True

        # Create a zero-filled array of the target shape
        padded = np.zeros((c, href, wref), dtype=data.dtype)

        # Copy the original data into the top-left corner of the padded array
        padded[:, :h, :w] = data

        return padded
    elif nodata_method == 'remove':
        tile_state.contains_nodata = True
        return None
