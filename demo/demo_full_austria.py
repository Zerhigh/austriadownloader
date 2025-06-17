import time
from pathlib import Path

from austriadownloader.downloadmanager import DownloadManager
from austriadownloader.configmanager import ConfigManager

if __name__ == "__main__":
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

    # Start the full scale sample of whole austria in parallel mode
    start_time = time.time()

    # NOTE:
    # Sampling the whole of Austria can lead to tiles with NaN values, as tiles can sample areas outside
    # of the Austrian border. This has to be considered when using the tiles in further processes. This behaviour is
    # expected and wanted, as it is the only solution to allow sampling of border areas.

    config_path = Path("./configs/full_config.yml")
    manager = DownloadManager(config=ConfigManager.from_config_file(config_path))
    manager.start_download()

    end_time = time.time()

    print(f'Download for full scale sample took: {round(end_time - start_time, 2)}')

    pass
