import os
import time
from pathlib import Path

import numpy
from austriadownloader.downloadmanager import DownloadManager
from austriadownloader.configmanager import ConfigManager

CURRENT_DIR = Path(__file__).parent


def test_configs():
    # RGB - multiple
    manager =  DownloadManager(config=ConfigManager(**{'data_path': './tests/test_samples/demo_single.csv',
                                                   'pixel_size': 1.6,
                                                   'outpath': "./tests/tmp/rgb_multiple",
                                                   'shape': [3, 100, 100],
                                                   'mask_label': [40, 41, 42, 48, 52, 53, 54, 55, 56, 57, 58, 59, 60,
                                                                  61, 62, 63, 64, 65, 72, 83, 84, 87, 88, 92, 95, 96]}))

    # NIR - multiple
    manager =  DownloadManager(config=ConfigManager(**{'data_path': './tests/test_samples/demo_single.csv',
                                                   'pixel_size': 1.6,
                                                   'outpath': "./tests/tmp/nir_multiple",
                                                   'shape': [4, 100, 100],
                                                   'mask_label': [40, 41, 42, 48, 52, 53, 54, 55, 56, 57, 58, 59, 60,
                                                                  61, 62, 63, 64, 65, 72, 83, 84, 87, 88, 92, 95, 96]}))

    # RGB - one class
    manager =  DownloadManager(config=ConfigManager(**{'data_path': './tests/test_samples/demo_single.csv',
                                                   'pixel_size': 1.6,
                                                   'outpath': "./tests/tmp/rgb_single",
                                                   'shape': [3, 512, 512],
                                                   'mask_label': [41]}))

    # NIR - one class
    manager =  DownloadManager(config=ConfigManager(**{'data_path': './tests/test_samples/demo_single.csv',
                                                   'pixel_size': 1.6,
                                                   'outpath': "./tests/tmp/nir_single",
                                                   'shape': [4, 512, 512],
                                                   'mask_label': [41]}))


    return
