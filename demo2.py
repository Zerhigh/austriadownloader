from pathlib import Path
import pathlib

from austriadownloader.downloadmanager import RDownloadManager
from austriadownloader.configmanager import RConfigManager

pathlib.Path("demo/").mkdir(parents=True, exist_ok=True)
pathlib.Path("demo/stratification_output/").mkdir(parents=True, exist_ok=True)

land_use_codes = {
    41: "Buildings",
    83: "Adjacent building areas",
    59: "Flowing water",
    60: "Standing water",
    61: "Wetlands",
    64: "Waterside areas",
    40: "Permanent crops or gardens",
    48: "Fields, meadows or pastures",
    57: "Overgrown areas",
    55: "Krummholz",
    56: "Forests",
    58: "Forest roads",
    42: "Car parks",
    62: "Low vegetation areas",
    63: "Operating area",
    65: "Roadside areas",
    72: "Cemetery",
    84: "Mining areas, dumps and landfills",
    87: "Rock and scree surfaces",
    88: "Glaciers",
    92: "Rail transport areas",
    95: "Road traffic areas",
    96: "Recreational area",
    52: "Gardens",
    54: "Alps"
}

def main():
    config_path = Path("C:/Users/PC/Coding/GeoQuery/demo/config.yml")
    manager = RDownloadManager(config=RConfigManager.from_config_file(config_path))
    manager.start_download()
    pass


if __name__ == "__main__":
    main()
