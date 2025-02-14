import requests
import sqlite3
import io


def fetch_geopackage_range(url, byte_range):
    """
    Fetches a specific byte range from a remote GeoPackage using HTTP Range Requests.

    Parameters:
    - url (str): URL of the remote GeoPackage.
    - byte_range (tuple): (start_byte, end_byte) specifying the range to fetch.

    Returns:
    - BytesIO: In-memory file-like object with the requested data.
    """
    headers = {"Range": f"bytes={byte_range[0]}-{byte_range[1]}"}
    response = requests.get(url, headers=headers, stream=True)

    if response.status_code not in [200, 206]:  # 206 means Partial Content
        raise ValueError(f"Failed to fetch data: HTTP {response.status_code}")

    return io.BytesIO(response.content)


def load_geopackage_in_memory(geopackage_stream):
    """
    Load the GeoPackage into an SQLite in-memory database from the binary stream.

    Parameters:
    - geopackage_stream (BytesIO): The in-memory stream containing the GeoPackage data.

    Returns:
    - sqlite3.Connection: The SQLite connection to the loaded GeoPackage.
    """
    # Create a new in-memory SQLite database
    conn = sqlite3.connect(":memory:")

    # Attach the in-memory GeoPackage to the SQLite database
    with io.BytesIO(geopackage_stream.getvalue()) as f:
        conn.backup(sqlite3.connect(":memory:"))  # Use SQLite backup API to attach the in-memory GPkg file

    return conn


def extract_spatial_index(geopackage_stream):
    """
    Extracts the spatial index (R-Tree) from the GeoPackage to identify relevant tiles/pages.

    Parameters:
    - geopackage_stream (BytesIO): The in-memory stream containing the GeoPackage data.

    Returns:
    - List of (rowid, minX, minY, maxX, maxY) tuples from the spatial index.
    """
    conn = load_geopackage_in_memory(geopackage_stream)
    cursor = conn.cursor()

    # Find R-Tree index table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'rtree_%'")
    index_table = cursor.fetchone()
    if not index_table:
        raise ValueError("No spatial index found in the GeoPackage.")

    index_table_name = index_table[0]

    # Extract spatial index (R-Tree)
    cursor.execute(f"SELECT rowid, minx, miny, maxx, maxy FROM {index_table_name}")
    spatial_index = cursor.fetchall()

    conn.close()
    return spatial_index


def find_relevant_byte_ranges(spatial_index, bbox):
    """
    Identifies the byte ranges to request based on the bounding box intersection with the spatial index.

    Parameters:
    - spatial_index (list): List of (rowid, minX, minY, maxX, maxY) tuples from the R-Tree.
    - bbox (tuple): (minX, minY, maxX, maxY) defining the spatial query area.

    Returns:
    - List of byte ranges [(start, end), ...] needed to fetch relevant data.
    """
    minX, minY, maxX, maxY = bbox
    relevant_rowids = [
        row[0] for row in spatial_index if not (row[3] < minX or row[1] > maxX or row[4] < minY or row[2] > maxY)
    ]

    if not relevant_rowids:
        return []

    # Example: Assuming rowid corresponds to page offsets (this depends on the file format)
    PAGE_SIZE = 4096  # Typical SQLite page size
    byte_ranges = [(rowid * PAGE_SIZE, (rowid + 1) * PAGE_SIZE - 1) for rowid in relevant_rowids]

    return byte_ranges


def query_geopackage(geopackage_stream, sql_query):
    """
    Executes an SQL query on an in-memory SQLite database from a GeoPackage.

    Parameters:
    - geopackage_stream (BytesIO): The in-memory GeoPackage.
    - sql_query (str): SQL query to execute.

    Returns:
    - List of tuples: Query results.
    """
    conn = load_geopackage_in_memory(geopackage_stream)
    cursor = conn.cursor()
    cursor.execute(sql_query)
    results = cursor.fetchall()

    conn.close()
    return results


def inspect_geopackage(geopackage_stream):
    """
    Inspects the structure of the GeoPackage by listing tables and key metadata.

    Parameters:
    - geopackage_stream (BytesIO): The in-memory GeoPackage stream.

    Returns:
    - None: Prints the tables and relevant metadata.
    """
    conn = load_geopackage_in_memory(geopackage_stream)
    cursor = conn.cursor()

    # List all tables in the GeoPackage
    #cursor.execute("SELECT * FROM sqlite_master WHERE type='table'")
    cursor.execute("SELECT name FROM sqlite_master WHERE layer='NFL'")

    tables = cursor.fetchall()
    print("Tables in the GeoPackage:")
    for table in tables:
        print(f"- {table[0]}")

    # List all columns in the gpkg_contents table
    cursor.execute("PRAGMA table_info(gpkg_contents)")
    contents_columns = cursor.fetchall()
    print("\nColumns in gpkg_contents:")
    for column in contents_columns:
        print(f"- {column[1]}")

    # List all columns in the gpkg_geometry_columns table
    cursor.execute("PRAGMA table_info(gpkg_geometry_columns)")
    geom_columns = cursor.fetchall()
    print("\nColumns in gpkg_geometry_columns:")
    for column in geom_columns:
        print(f"- {column[1]}")

    conn.close()


def get_geopackage_header(url):
    # Send an HTTP HEAD request to the GeoPackage URL
    response = requests.head(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Print metadata (headers)
        print("HTTP Status Code:", response.status_code)
        print("Content Type:", response.headers.get("Content-Type"))
        print("Content Length (File Size):", response.headers.get("Content-Length"))
        print("Last Modified:", response.headers.get("Last-Modified"))
    else:
        print("Failed to fetch header information. HTTP Status Code:", response.status_code)



# Define the remote GeoPackage URL
# Define the remote GeoPackage URL
geo_url = "https://data.bev.gv.at/download/Kataster/gpkg/national/KAT_DKM_GST_epsg31287_20241002.gpkg"
query_bbox = (483495.7,614734.9, 483897.0,615310.3)

get_geopackage_header(geo_url)


# Step 1: Fetch the first few MB to locate the spatial index (initial range example)
initial_range = (0, 5000000)  # Adjust based on GeoPackage structure
gpkg_data = fetch_geopackage_range(geo_url, initial_range)




inspect_geopackage(gpkg_data)

# Step 2: Extract the spatial index
spatial_index = extract_spatial_index(gpkg_data)

# Step 4: Find the relevant byte ranges
byte_ranges = find_relevant_byte_ranges(spatial_index, query_bbox)

# Step 5: Fetch only the necessary byte ranges
full_data = io.BytesIO()
for byte_range in byte_ranges:
    chunk = fetch_geopackage_range(geo_url, byte_range)
    full_data.write(chunk.getvalue())

# Step 6: Run SQL Query on the downloaded data
spatial_query = f"""
SELECT * FROM merged
WHERE ST_Intersects(geom, ST_MakeEnvelope({query_bbox[0]}, {query_bbox[1]}, {query_bbox[2]}, {query_bbox[3]}, 31287));
"""

results = query_geopackage(full_data, spatial_query)

# Step 7: Print Results
print("Spatial Query Results:", results)
