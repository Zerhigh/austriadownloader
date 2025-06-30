# austriadownloader

[![Release](https://img.shields.io/github/v/release/Zerhigh/austriadownloader)](https://img.shields.io/github/v/release/Zerhigh/austriadownloader)
[![Build status](https://img.shields.io/github/actions/workflow/status/Zerhigh/austriadownloader/main.yml?branch=main)](https://github.com/Zerhigh/austriadownloader/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/Zerhigh/austriadownloader/branch/main/graph/badge.svg)](https://codecov.io/gh/Zerhigh/austriadownloader)
[![Commit activity](https://img.shields.io/github/commit-activity/m/Zerhigh/austriadownloader)](https://img.shields.io/github/commit-activity/m/Zerhigh/austriadownloader)
[![License](https://img.shields.io/github/license/Zerhigh/austriadownloader)](https://img.shields.io/github/license/Zerhigh/austriadownloader)

- **Github repository**: <https://github.com/Zerhigh/austriadownloader/>
- **Documentation** <https://Zerhigh.github.io/austriadownloader/>

### Introduction

This repository contains the code for developing and testing the `austriadownloader` package, capable of downloading temporally and spatially aligned Austrian Orthophoto (RGB & NIR) and Cadastral data for (among others) Deep Learning application.
Available datasets include the Austrian [Orthophoto series](https://data.bev.gv.at/geonetwork/srv/ger/catalog.search#/metadata/f2e11a84-cdc7-4cfa-b048-da3675d58704) of 2024 (includes image tiles from 2021 to 2023) and the corresponding [Cadastral datasets](https://data.bev.gv.at/geonetwork/srv/ger/catalog.search#/metadata/2447c4db-95fc-4163-9df2-d7cedf16e210) (eg. from 01.04.2021) published bi-anually.
For a detailed analysis and description of datasources, processing steps, and methodology please refer to the corresponding publication (to be added upon release, contact authors for a pre-print until then).

### Getting Started

All required meta-datasets are available in `austriadownloader/austria_data/` and can be created by executing `austriadownloader/austria_data/metadata_creation.py`.

Provide sample image POIs as centroids in a dataframe with the following scheme in the WGS84 CRS (EPSG:4326). Image dimensions will be determined by other input parameters such as `pixel_size` and `shape`.
An independent (but closely related) git-repository for automatically creating such a sample file is available under [austriadownloader_sampler](https://github.com/Zerhigh/austriadownloader_sampler).

Sample file structure:

| Column | Type  | Description                             |
|--------|-------|-----------------------------------------|
| `id`   | str   | Unique identifier for each location     |
| `lat`  | float | Latitude coordinate in decimal degrees  |
| `lon`  | float | Longitude coordinate in decimal degrees |

An example for a sample file: 

| id  | lat           | lon           |
|-----|---------------|---------------|
| 0   | 47.6615683485 | 15.9040047148 |
| 1   | 47.6730783029 | 15.9045680914 |
| 2   | 47.6845882247 | 15.9051317152 |
| ... | ...           | ...           |

### Code Example:

Refer to `demo/demo.py` for code, config, and sample files.

```python
from pathlib import Path
from austriadownloader.downloadmanager import DownloadManager
from austriadownloader.configmanager import ConfigManager

config_path = Path("path_to_your_config.yml")
manager = DownloadManager(config=ConfigManager.from_config_file(config_path))
manager.start_download()
```

Input parameters are provided in the config file and include:

| Column             | Type                                   | Description                                                                                                                                                          |
|--------------------|----------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `data_path`        | `Path` or `str`                        | Input path for sampling POI table.                                                                                                                                   |
| `pixel_size`       | `float`                                | Pixel resolution in meters. Must be a predefined value from (0.2, 0.4, 0.8, ... 204.8)                                                                               |
| `shape`            | `tuple[int, int, int]`                 | Image dimensions as `(channels, height, width)`. Channels must be `3` (RGB) or `4` (RGB & NIR).                                                                      |
| `outpath`          | `Path` or `str`                        | Directory path where output files will be saved.                                                                                                                     |
| `mask_label`       | `list`, `tuple[int]` or `int`          | Cadastral mask(s) to be extracted. A single cadastral label will result in a binary mask, if several cadastral classes are provided a multi-label mask is generated. |
| `mask_remapping`   | `Dict` (default: `None`)               | Allows the selection and merging of several cadastral classes.                                                                                                       |
| `create_gpkg`      | `bool` (default: `False`)              | Indicates whether vectorized but unclipped tiles should be saved as `.GPKG` in addition to image tiles.                                                              |
| `nodata_mode`      | `str` (default: `'flag'`)              | Mode for handling no-data values (`'flag'` or `'remove'`).                                                                                                           |
| `nodata_value`     | `int` (default: `0`)                   | Value assigned to no-data pixels in all image data products.                                                                                                         |
| `outfile_prefixes` | `Dict` (default: `input` and `target`) | Custom name assignement for ouput files: `raster` -> `input`, `vector` -> `target`                                                                                   |
| `verbose`          | `bool` (default: `False`)              | Providing verbose comments during script execution.                                                                                                                  |

### Available Classes

To select your class labels, select one or more from the following list (Source: [BEV, page 12 ff.](https://data.bev.gv.at/download/Kataster/gpkg/national/BEV_S_KA_Katastralmappe_Grundstuecksdaten_GPKG_V1.0.pdf)):

| **Category**       | **Code** | **Subcategory**                   |
|--------------------|----------|-----------------------------------|
| Building areas     | 41       | Buildings                         |
|                    | 83       | Adjacent building areas           |
| Water body         | 59       | Flowing water                     |
|                    | 60       | Standing water                    |
|                    | 61       | Wetlands                          |
|                    | 64       | Waterside areas                   |
| Agricultural       | 40       | Permanent crops or gardens        |
|                    | 48       | Fields, meadows or pastures       |
|                    | 53       | Vineyards                         |
|                    | 57       | Overgrown areas                   |
| Forest             | 55       | Krummholz                         |
|                    | 56       | Forests                           |
|                    | 58       | Forest roads                      |
| Other              | 42       | Car parks                         |
|                    | 62       | Low vegetation areas              |
|                    | 63       | Operating area                    |
|                    | 65       | Roadside areas                    |
|                    | 72       | Cemetery                          |
|                    | 84       | Mining areas, dumps and landfills |
|                    | 87       | Rock and scree surfaces           |
|                    | 88       | Glaciers                          |
|                    | 92       | Rail transport areas              |
|                    | 95       | Road traffic areas                |
|                    | 96       | Recreational area                 |
| Gardens            | 52       | Gardens                           |
| Alps               | 54       | Alps                              |

### Results

Multi-label mask with all available cadastral classes selected (not all are present in the selected sample):

<p float="left">
  <img src="figures/input_2.png" alt="RGB Orthophoto" width="45%" />
  <img src="figures/target_2.png" alt="Multi-label mask" width="45%" />
</p>

General overview of different cadastral classes merged into a binary mask:

<p float="left">
  <img src="figures/example_results.png" alt="Cadastral classes" width="66%" />
</p>

Selection of unique cadastral classes:

<p float="left">
  <img src="figures/example_results2.png" alt="Unique classes" width="50%" />
</p>


### Citation

This repository was created for a presentation at the AGIT 2025 conference.

Repository initiated with [fpgmaas/cookiecutter-poetry](https://github.com/fpgmaas/cookiecutter-poetry).
