from osgeo import gdal
import matplotlib.pyplot as plt


def read_overview_demo(raster_path, overview_index, window=None):
    """
    Read a specific overview from a raster file using GDAL, optionally with a window.

    Parameters:
    raster_path (str): Path to the raster file
    overview_index (int): Index of the overview to read (0 is first overview)
    window (tuple, optional): Window to read in format (xoff, yoff, xsize, ysize)
                            Coordinates are in the overview's coordinate space
    """
    # Open the dataset
    ds = gdal.Open(raster_path)
    if ds is None:
        raise ValueError("Could not open the raster file")

    # Get the first band
    band = ds.GetRasterBand(1)

    # Get overview count
    overview_count = band.GetOverviewCount()
    print(f"Number of overviews: {overview_count}")

    if overview_count == 0:
        raise ValueError("This raster has no overviews!")

    if overview_index >= overview_count:
        raise ValueError(f"Overview index {overview_index} is out of range. "
                         f"Only {overview_count} overviews available.")

    # Get the overview band
    overview = band.GetOverview(overview_index)
    if overview is None:
        raise ValueError(f"Could not get overview {overview_index}")

    # Print information
    print(f"\nFull resolution size: {band.XSize} x {band.YSize}")
    print(f"Overview size: {overview.XSize} x {overview.YSize}")

    # Read the data - with window if specified
    if window:
        xoff, yoff, xsize, ysize = window
        # Validate window parameters
        if (xoff < 0 or yoff < 0 or
                xoff + xsize > overview.XSize or
                yoff + ysize > overview.YSize):
            raise ValueError("Window parameters out of bounds")

        print(f"\nReading window: xoff={xoff}, yoff={yoff}, "
              f"xsize={xsize}, ysize={ysize}")
        overview_data = overview.ReadAsArray(xoff, yoff, xsize, ysize)

        # For comparison, read the same relative area from full resolution
        scaling_factor = band.XSize / overview.XSize
        full_xoff = int(xoff * scaling_factor)
        full_yoff = int(yoff * scaling_factor)
        full_xsize = int(xsize * scaling_factor)
        full_ysize = int(ysize * scaling_factor)
        full_res_data = band.ReadAsArray(full_xoff, full_yoff, full_xsize, full_ysize)
    else:
        overview_data = overview.ReadAsArray()
        full_res_data = band.ReadAsArray()

    # Get geotransform
    transform = ds.GetGeoTransform()
    print(f"\nGeotransform: {transform}")

    if window:
        # Adjust transform for window
        new_transform = list(transform)
        new_transform[0] += xoff * transform[1]  # Adjust x origin
        new_transform[3] += yoff * transform[5]  # Adjust y origin
        print(f"Window geotransform: {new_transform}")

    # Visualize
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))

    # Full resolution
    im1 = ax1.imshow(full_res_data, cmap='viridis')
    ax1.set_title('Full Resolution' + (' (Window)' if window else ''))
    plt.colorbar(im1, ax=ax1, label='Pixel Values')

    # Overview
    im2 = ax2.imshow(overview_data, cmap='viridis')
    ax2.set_title(f'Overview Level {overview_index}' + (' (Window)' if window else ''))
    plt.colorbar(im2, ax=ax2, label='Pixel Values')

    plt.tight_layout()
    plt.show()

    # Clean up
    ds = None

    return overview_data


# Remote COG file
data = "/vsicurl/https://data.bev.gv.at/download/DOP/20221027/2019260_Mosaik_RGB.tif"

# Example usage
read_overview_demo(raster_path=data, overview_index=3, window=(2000, 2000, 100, 100))
