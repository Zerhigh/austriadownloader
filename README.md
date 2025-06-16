# austriadownloader

[![Release](https://img.shields.io/github/v/release/Zerhigh/austriadownloader)](https://img.shields.io/github/v/release/Zerhigh/austriadownloader)
[![Build status](https://img.shields.io/github/actions/workflow/status/Zerhigh/austriadownloader/main.yml?branch=main)](https://github.com/Zerhigh/austriadownloader/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/Zerhigh/austriadownloader/branch/main/graph/badge.svg)](https://codecov.io/gh/Zerhigh/austriadownloader)
[![Commit activity](https://img.shields.io/github/commit-activity/m/Zerhigh/austriadownloader)](https://img.shields.io/github/commit-activity/m/Zerhigh/austriadownloader)
[![License](https://img.shields.io/github/license/Zerhigh/austriadownloader)](https://img.shields.io/github/license/Zerhigh/austriadownloader)

- **Github repository**: <https://github.com/Zerhigh/austriadownloader/>
- **Documentation** <https://Zerhigh.github.io/austriadownloader/>

## Getting started with your project

Clone this repository to start developing. 
All required datasets are available in `austriadownloader/austria_data/` and can be created by executing `austriadownloader/austria_data/metadata_creation.py`.

To access and download Austrian Orthophoto and matching cadastral classes, execute the `demo.py` script.
Provide POIs as a dataframe with the following scheme in the WGS84 format (EPSG:4326):

| Column | Type  | Description                             |
|--------|-------|-----------------------------------------|
| `id`   | str   | Unique identifier for each location     |
| `lat`  | float | Latitude coordinate in decimal degrees  |
| `lon`  | float | Longitude coordinate in decimal degrees |

An example for a config file: 

| id  | lat           | lon           |
|-----|---------------|---------------|
| 0   | 47.6615683485 | 15.9040047148 |
| 1   | 47.6730783029 | 15.9045680914 |
| 2   | 47.6845882247 | 15.9051317152 |
| ... | ...           | ...           |


Other input parameters are:

| Column             | Type                          | Description                                                                                                                                                         |
|--------------------|-------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `data_path`        | `Path` or `str`               | Input path for sampled POI table.                                                                                                                                   |
| `pixel_size`       | `float`                       | Pixel resolution in meters. Must be a predefined value from (0.2, 0.4, 0.8, ... 204.8)                                                                              |
| `shape`            | `tuple[int, int, int]`        | Image dimensions as `(channels, height, width)`. Channels must be `3` (RGB) or `4` (RGBN).                                                                          |
| `outpath`          | `Path` or `str`               | Directory path where output files will be saved.                                                                                                                    |
| `mask_label`       | `list`, `tuple[int]` or `int` | Cadastral mask(s) to be extracted. A single cadastral label will result in a binary mask, if several cadastral classes are provided a multi-label mask is generated.|
| `mask_remapping`   | `Dict` (default: `None`)      | Allows the selection and merging of several cadastral classes.                                                                                                      |
| `create_gpkg`      | `bool` (default: `False`)     | Indicates whether vectorized but unclipped tiles should be saved as `.GPKG`.                                                                                        |
| `nodata_mode`      | `str` (default: `'flag'`)     | Mode for handling no-data values (`'flag'` or `'remove'`).                                                                                                          |
| `nodata_value`     | `int` (default: `0`)          | Value assigned to no-data pixels.                                                                                                                                   |
| `outfile_prefixes` | `Dict`                        | Custom name assignement for ouput files: `raster` -> `input`, `vector` -> `target`                                                                                  |
| `verbose`          | `bool` (default: `False`)     | Providing verbose comments during script execution.                                                                                                                 |


## Results

Multi-label mask with all available cadastral classes selected (not all are present in the selected sample):

<p float="left">
  <img src="figures/input_2.png" alt="RGB Orthophoto" width="45%" />
  <img src="figures/target_2.png" alt="Multi-label mask" width="45%" />
</p>

General overview of different cadastral classes merged into a binary mask:

<p float="left">
  <img src="results/example_results.png" alt="Cadastral classes" width="80%" />
</p>

Selection of unique cadastral classes:

<p float="left">
  <img src="results/example_results2.png" alt="Unique classes" width="80%" />
</p>


## Available Classes

To select your class labels, select one or more from the following list:

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

## Releasing a new version

- Create an API Token on [PyPI](https://pypi.org/).
- Add the API Token to your projects secrets with the name `PYPI_TOKEN` by visiting [this page](https://github.com/Zerhigh/austriadownloader/settings/secrets/actions/new).
- Create a [new release](https://github.com/Zerhigh/austriadownloader/releases/new) on Github.
- Create a new tag in the form `*.*.*`.
- For more details, see [here](https://fpgmaas.github.io/cookiecutter-poetry/features/cicd/#how-to-trigger-a-release).

---

Repository initiated with [fpgmaas/cookiecutter-poetry](https://github.com/fpgmaas/cookiecutter-poetry).
