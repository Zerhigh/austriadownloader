# # Parent class: DownloadManager (Manages the overall download process)
# import pandas as pd
#
#
# class DownloadManager:
#
#     def __init__(self, file_path=None, cols=('id', 'aerial', 'cadster', 'num_items', 'area_items')):
#         """
#         Initialize the DownloadManager.
#         If a file path is provided, it will automatically load the tile list from the file.
#         """
#         self.tiles: pd.DataFrame | None = None
#         self.state: pd.DataFrame = pd.DataFrame(columns=cols)
#
#         # Automatically load file if provided
#         if file_path:
#             self.load_datafile(file_path)
#
#     def load_datafile(self, file_path):
#         try:
#             self.tiles = pd.read_csv(file_path)
#             print(f"Successfully loaded {len(self.tiles)} tiles from {file_path}.")
#         except Exception as e:
#             print(f"Error loading file: {e}")
#
#
# class DownloadState:
#     """
#     Manages the state of raster and vector data downloads.
#
#     This class keeps track of whether raster and vector downloads have succeeded or failed.
#     It provides methods to update and check the download status for both types of data.
#
#     Attributes:
#         id (str): A unique identifier for the download process.
#         raster_download_success (bool): Indicates if the raster download was successful.
#         vector_download_success (bool): Indicates if the vector download was successful.
#
#     Methods:
#         set_raster_failed():
#             Marks the raster download as failed.
#         set_raster_successful():
#             Marks the raster download as successful.
#         check_raster() -> bool:
#             Returns True if the raster download was successful, otherwise False.
#         set_vector_failed():
#             Marks the vector download as failed.
#         set_vector_successful():
#             Marks the vector download as successful.
#         check_vector() -> bool:
#             Returns True if the vector download was successful, otherwise False.
#     """
#
#     def __init__(self, id: str):
#         """
#         Initializes the DownloadState with a unique identifier.
#
#         Args:
#             id (str): Unique identifier for the download process.
#         """
#         self.id: str = id
#         self.raster_download_success: bool = False
#         self.vector_download_success: bool = False
#         self.num_items: int = 0
#         self.area_items: float = 0
#
#     def get_state(self) -> dict:
#         return {'id': self.id,
#                 'aerial': self.raster_download_success,
#                 'cadster': self.vector_download_success,
#                 'num_items': self.num_items,
#                 'area_items': self.area_items}
#
#     def set_raster_failed(self):
#         """Marks the raster download as failed."""
#         self.raster_download_success = False
#
#     def set_raster_successful(self):
#         """Marks the raster download as successful."""
#         self.raster_download_success = True
#
#     def check_raster(self) -> bool:
#         """
#         Checks if the raster download was successful.
#
#         Returns:
#             bool: True if raster download was successful, False otherwise.
#         """
#         return self.raster_download_success
#
#     def set_vector_failed(self):
#         """Marks the vector download as failed."""
#         self.vector_download_success = False
#
#     def set_vector_successful(self):
#         """Marks the vector download as successful."""
#         self.vector_download_success = True
#
#     def check_vector(self) -> bool:
#         """
#         Checks if the vector download was successful.
#
#         Returns:
#             bool: True if vector download was successful, False otherwise.
#         """
#         return self.vector_download_success
