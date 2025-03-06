import json
import yaml
from pathlib import Path
from typing import Literal, Final, TypeAlias
from pydantic import BaseModel, field_validator, ValidationError

# Type aliases
ChannelCount: TypeAlias = Literal[3, 4]  # RGB or RGBN
ImageShape = tuple[ChannelCount, int, int]

# Valid constants
VALID_PIXEL_SIZES: Final = (0.2, 0.4, 0.8, 1.6, 3.2, 6.4, 12.8, 25.6, 51.2, 102.4, 204.8)
VALID_MASK_LABELS: Final = (40, 41, 42, 48, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 72, 83, 84, 87, 88, 92, 95, 96)
VALID_DOWNLOADS_METHODS: Final = ('sequential', 'parallel')


class RConfigManager(BaseModel):
    # id: str | int
    # lon: float
    # lat: float
    data_path: Path | str
    pixel_size: float
    resample_size: float | None = None
    shape: ImageShape
    outpath: Path | str
    mask_label: list[int] | tuple[int] | int
    download_method: str = 'sequential'
    create_gpkg: bool = False
    nodata_mode: str = 'flag'
    nodata_value: int = 0

    # @field_validator("id")
    # @classmethod
    # def validate_id(cls, value: str | int) -> str:
    #     return str(value) if isinstance(value, int) else value

    @field_validator("nodata_mode")
    @classmethod
    def validate_nodata_mode(cls, value: str) -> str:
        if value not in {"flag", "remove"}:
            raise ValueError("Operation mode must be either 'flag' or 'remove'")
        return value

    @field_validator("shape")
    @classmethod
    def validate_shape(cls, value: ImageShape) -> ImageShape:
        if len(value) != 3 or value[0] not in (3, 4) or any(dim <= 0 for dim in value):
            raise ValueError("Invalid shape: (channels, height, width) required with channels 3 or 4.")
        return value

    @field_validator("outpath")
    @classmethod
    def validate_outpath(cls, value: Path | str) -> Path:
        path = Path(value)
        if not path.exists() or not path.is_dir():
            raise ValueError(f"Output path is invalid: {path}")
        return path

    @field_validator("data_path")
    @classmethod
    def validate_data_path(cls, value: Path | str) -> Path:
        path = Path(value)
        if not path.exists():
            raise ValueError(f"data_path path is invalid: {path}")
        return path

    @field_validator("pixel_size")
    @classmethod
    def validate_pixel_size(cls, value: float) -> float:
        if value not in VALID_PIXEL_SIZES:
            raise ValueError(f"Invalid pixel size: {value}. Must be one of {VALID_PIXEL_SIZES}")
        return value

    @field_validator("mask_label")
    @classmethod
    def validate_mask_label(cls, value: list[int] | tuple[int] | int) -> list[int]:
        if isinstance(value, int):
            value = [value]
        if not all(val in VALID_MASK_LABELS for val in value):
            raise ValueError(f"Invalid mask labels: {value}. Must be within {VALID_MASK_LABELS}")
        return value

    @field_validator("download_method")
    @classmethod
    def validate_download_method(cls, value: str) -> str:
        if value not in VALID_DOWNLOADS_METHODS:
            raise ValueError(f"Invalid download method: {value}. Must be one of {VALID_DOWNLOADS_METHODS}")
        return value

    class Config:
        frozen = True  # Make instances immutable

    @classmethod
    def from_config_file(cls, file_path: str | Path) -> "DataRequest":
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")

        with open(path, "r", encoding="utf-8") as file:
            if path.suffix.lower() == ".json":
                config_data = json.load(file)
            elif path.suffix.lower() in {".yaml", ".yml"}:
                config_data = yaml.safe_load(file)
            else:
                raise ValueError("Unsupported config file format. Use JSON or YAML.")

        # Ensure all parameters are loaded, using defaults if necessary
        default_values = {
            "resample_size": None,
            "create_gpkg": False,
            "nodata_mode": "flag",
            "nodata_value": 0,
            "download_method": "sequential"
        }
        config_data = {**default_values, **config_data}  # Merge defaults with provided values

        try:
            return cls(**config_data)
        except ValidationError as e:
            raise ValueError(f"Invalid configuration: {e}")


# # Path to your configuration file (JSON or YAML)
# config_path = Path("C:/Users/PC/Coding/GeoQuery/demo/config.yml")  # Change to "config.json" if using JSON
#
# # Load the configuration into a DataRequest instance
# try:
#     data_request = RConfigManager.from_config_file(config_path)
#     print("Configuration loaded successfully:")
#     print(data_request)
# except Exception as e:
#     print(f"Error loading configuration: {e}")
#
#
# pass



