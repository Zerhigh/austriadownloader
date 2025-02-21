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

    Raises:
        ValueError: If any of the parameters fail validation.
    """

    id: str
    lon: float
    lat: float
    pixel_size: float
    shape: ImageShape
    outpath: Path | str

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

    class Config:
        """Pydantic model configuration."""
        frozen = True  # Make instances immutable