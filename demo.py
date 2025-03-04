import os.path
import pathlib
import pandas as pd
from tqdm import tqdm
from austriadownloader.downloadstate import DownloadManager
import austriadownloader

from multiprocessing import Pool, Manager

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

dem = pd.DataFrame([{'id': 'id_01', 'lat': 48.40086407732648, 'lon': 15.585103157374359},
                    {'id': 'id_02', 'lat': 47.8015341908452, 'lon': 13.031880967377068},
                    {'id': 'id_03', 'lat': 46.674413481011335, 'lon': 13.9611802108645},
                    {'id': 'id_04', 'lat': 47.37133953187826, 'lon': 16.340480406413537},
                    {'id': 'id_05', 'lat': 48.219523815790424, 'lon': 16.40504050915158},
                    {'id': 'id_06', 'lat': 48.10538361840102, 'lon': 16.22915864360271}])

# manager = DownloadManager(file_path='sample_even_download.csv')
#
# code = 41
#
# op = 'demo/stratification_output/'


def download_tile(row, queue):
    op = 'demo/stratification_output/'
    code = 41

    request = austriadownloader.DataRequest(
        id=row.id,
        lat=row.lat,
        lon=row.lon,
        pixel_size=1.6,
        resample_size=2.5,
        shape=(4, 512, 512),  # for RGB just use (3, 1024, 1024)
        outpath=f"{op}",
        mask_label=code,  # Base: Buildings
        create_gpkg=False,
        nodata_mode='flag',  # or 'remove',
    )

    # Skip if the file already exists
    if os.path.exists(f'{op}/input_{request.id}.tif') and os.path.exists(f'{op}/target_{request.id}.tif'):
        queue.put((request.id, None))  # Skip processing, report status
        return request.id, None  # Skip processing

    download = austriadownloader.download(request, verbose=False)

    # Put the result into the queue
    queue.put((download.id, download.get_state()))

    return download.id, download.get_state()


def main():
    manager = DownloadManager(file_path='sample_even_download.csv')

    op = 'demo/stratification_output/'

    # Extract rows as dictionaries for easier parallel processing
    rows = [row for _, row in manager.tiles[:10].iterrows()]

    # Create a Queue to communicate with the main process
    with Manager() as manager_instance:
        queue = manager_instance.Queue()

        # Set up the progress bar using tqdm
        with Pool(processes=os.cpu_count()) as pool:
            # Initialize tqdm with the number of rows to process
            progress_bar = tqdm(total=len(rows), desc="Downloading Tiles", unit="tile")

            # Use starmap to pass both the row and the queue to the worker
            # Pass the progress_bar to update it in the worker
            pool.starmap(download_tile, [(row, queue) for row in rows])

            # Now process the results that are put into the queue
            for _ in range(len(rows)):
                tile_id, state = queue.get()  # Retrieve results from queue
                if state:  # If state is not None, update the manager
                    manager.state.loc[tile_id] = state
                progress_bar.update(1)  # Update the progress bar for each completed task

            progress_bar.close()  # Close the progress bar after all tasks are finished

        # Save the state log
        manager.state.to_csv(f'{op}/statelog.csv', index=False)


if __name__ == "__main__":
    main()
# for i, row in manager.tiles.iterrows():
#     request = austriadownloader.DataRequest(
#         id=row.id,
#         lat=row.lat,
#         lon=row.lon,
#         pixel_size=1.6,
#         resample_size=2.5,
#         shape=(4, 512, 512),  # for RGB just use (3, 1024, 1024)
#         outpath=f"{op}",
#         mask_label=code,  # Base: Buildings
#         create_gpkg=False,
#         nodata_mode='flag', # or 'remove',
#     )
#
#     # if file is already downloaded, skip it
#     if os.path.exists(f'{op}/input_{request.id}.tif') and os.path.exists(f'{op}/target_{request.id}.tif'):
#         continue
#
#     download = austriadownloader.download(request, verbose=True)
#     manager.state.loc[download.id] = download.get_state()
#
#     # save every 100 steps
#     if i % 100 == 0:
#         manager.state.to_csv(f'{op}/statelog.csv', index=False)
#
# manager.state.to_csv(f'{op}/statelog.csv', index=False)
#
# pass