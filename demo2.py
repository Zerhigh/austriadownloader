from pathlib import Path

from austriadownloader.downloadmanager import DownloadManager
from austriadownloader.configmanager import ConfigManager

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
    Path("demo/").mkdir(parents=True, exist_ok=True)
    Path("demo/stratification_output/").mkdir(parents=True, exist_ok=True)

    config_path = Path("C:/Users/PC/Coding/GeoQuery/demo/config.yml")
    manager = DownloadManager(config=ConfigManager.from_config_file(config_path))
    manager.start_download()
    pass


if __name__ == "__main__":
    main()
