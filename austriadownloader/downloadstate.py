from typing import Dict
from pydantic import BaseModel, field_validator


class DownloadState(BaseModel):
    id: str | int | float
    lat: float
    lon: float
    land_use_mapped: Dict[int, int] = {
        41: 1,
        83: 2,
        59: 3,
        60: 4,
        61: 5,
        64: 6,
        40: 7,
        48: 8,
        57: 9,
        55: 10,
        56: 11,
        58: 12,
        42: 13,
        62: 14,
        63: 15,
        65: 16,
        72: 17,
        84: 18,
        87: 19,
        88: 20,
        92: 21,
        95: 22,
        96: 23,
        52: 24,
        54: 25
    }

    contains_nodata: bool = False
    raster_download_success: bool = False
    vector_download_success: bool = False
    num_items: int = 0
    set_pixels: int = 0

    class Config:
        # This ensures that the model is mutable after initialization (default behavior)
        frozen = False

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str | int | float) -> str:
        return str(value) if isinstance(value, int) else str(int(value)) if isinstance(value, float) else value

    def get_state(self) -> Dict[str, any]:
        """Returns the state information for adding to df."""
        return {
            'id': self.id,
            'aerial': self.raster_download_success,
            'cadster': self.vector_download_success,
            'num_items': self.num_items,
            'area_items': self.set_pixels,
            'contains_nodata': self.contains_nodata
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
