"""
Configuration parameters for downloading Austrian Orthophotos and Cadastral data.

This module defines a Pydantic BaseModel for validating and managing configuration
parameters used in satellite image processing operations. It includes validation
for geographical coordinates, pixel sizes, image shape, and output path.
"""

from pathlib import Path
from typing import Literal, Final, TypeAlias
from pydantic import BaseModel, field_validator

# Type aliases for better readability
ChannelCount: TypeAlias = Literal[3, 4]  # RGB or RGBN
ImageShape = tuple[ChannelCount, int, int]

# Valid pixel sizes in meters
VALID_PIXEL_SIZES: Final = (0.2, 0.4, 0.8, 1.6, 3.2, 6.4, 12.8, 25.6, 51.2, 102.4, 204.8)
VALID_MASK_LABELS: Final = (40, 41, 42, 48, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 72, 83, 84, 87, 88, 92, 95, 96)


class DataRequest(BaseModel):
    """
    Configuration parameters for satellite image processing.

    Attributes:
        lon (float): Longitude coordinate in decimal degrees.
        lat (float): Latitude coordinate in decimal degrees.
        pixel_size (float): Pixel resolution in meters. Must be one of the predefined values.
        shape (tuple[int, int, int]): Image dimensions as (channels, height, width).
            Channels must be either 3 (RGB) or 4 (RGBN).
        outpath (Path | str): Directory path where output files will be saved.
        create_gpkg (bool) = False: Indicates if the vectoried but unclipped tiles should be saved as individual .GPKG
        mask_label (list[int]| tuple[int] | int): Indicates Cadaster mask(s) to be extracted, any provided mask will be
            merged and a binary mask will be created. Creating multi-class msks is not supported.
            Classes and Codes:

    Raises:
        ValueError: If any of the parameters fail validation.
    """

    id: str | int
    lon: float
    lat: float
    pixel_size: float
    resample_size: float | None = None
    shape: ImageShape
    outpath: Path | str
    mask_label: list[int] | tuple[int] | int
    create_gpkg: bool = False
    nodata_mode: str = 'flag'
    nodata_value: int = 0

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str | int) -> str:
        """
        Validate the id.

        Args:
            value: The id as a string or integer.

        Returns:
            str: Validated id.

        Raises:
            ValueError: If the value is not 'str' or 'int'.
        """
        if isinstance(value, str):
            return value
        elif isinstance(value, int):
            return str(value)
        else:
            raise ValueError("Id must be string or int")

    @field_validator("nodata_mode")
    @classmethod
    def validate_nodata_mode(cls, value: str) -> str:
        """
        Validate the operation mode.

        Args:
            value: The operation mode as a string.

        Returns:
            str: Validated operation mode.

        Raises:
            ValueError: If the value is not 'flag' or 'remove'.
        """
        if value not in {"flag", "remove"}:
            raise ValueError("Operation mode must be either 'flag' or 'remove'")
        return value

    @field_validator("shape")
    @classmethod
    def validate_shape(cls, value: ImageShape) -> ImageShape:
        """
        Validate the image shape dimensions.

        Args:
            value: Tuple of (channels, height, width).

        Returns:
            The validated shape tuple.

        Raises:
            ValueError: If shape dimensions are invalid.
        """
        if len(value) != 3:
            raise ValueError("Shape must be a tuple of 3 integers: (channels, height, width)")
        
        channels = value[0]
        if channels not in (3, 4):
            raise ValueError(
                f"Channel count must be 3 for RGB or 4 for RGBN, got {channels}"
            )

        if any(dim <= 0 for dim in value):
            raise ValueError("All dimensions must be positive integers")

        return value

    @field_validator("outpath")
    @classmethod
    def validate_outpath(cls, value: Path | str) -> Path:
        """
        Validate and convert the output path.

        Args:
            value: Path-like object pointing to the output directory.

        Returns:
            Path: Validated Path object.

        Raises:
            ValueError: If the path doesn't exist or isn't a directory.
        """
        path = Path(value)
        if not path.exists():
            raise ValueError(f"Output path does not exist: {path}")
        if not path.is_dir():
            raise ValueError(f"Output path is not a directory: {path}")
        return path

    @field_validator("pixel_size")
    @classmethod
    def validate_pixel_size(cls, value: float) -> float:
        """
        Validate the pixel size.

        Args:
            value: Pixel resolution in meters.

        Returns:
            float: Validated pixel size.

        Raises:
            ValueError: If the pixel size is not in the predefined list.
        """
        if value not in VALID_PIXEL_SIZES:
            raise ValueError(
                f"Invalid pixel size: {value}. Must be one of {VALID_PIXEL_SIZES}"
            )
        
        return value

    @field_validator("mask_label")
    @classmethod
    def validate_mask_label(cls, value: list[int] | tuple[int] | int) -> list[int] | tuple[int] | int:
        """
        Validate the mask_label.

        Args:
            value: Mask label of cadastral registry

        Returns:
            float: Validated mask label.

        Raises:
            ValueError: If the mask label is not in the predefined list.
        """
        if isinstance(value, (list, tuple)):
            for val in value:
                if val not in VALID_MASK_LABELS:
                    raise ValueError(
                        f"Invalid mask label: {val}. Must be one of {VALID_MASK_LABELS}"
                    )
            return value
        else:
            if value not in VALID_MASK_LABELS:
                raise ValueError(
                    f"Invalid mask label: {value}. Must be one of {VALID_MASK_LABELS}"
                )
            return [value]

    class Config:
        """Pydantic model configuration."""
        frozen = True  # Make instances immutable