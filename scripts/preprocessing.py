# File: scripts/preprocessing.py
import os
import polars as pl
from sqlalchemy import create_engine

print("Starting data preprocessing script...")

# --- Configuration (from Environment Variables) ---
DATABASE_HOST = os.getenv('DATABASE_HOST')
DATABASE_PORT = os.getenv('DATABASE_PORT')
DATABASE_USER = os.getenv('DATABASE_USER')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
DATABASE_NAME = os.getenv('DATABASE_NAME')

# Paths inside the container due to volume mounts
RAW_DATA_PATH = "/app/raw_data/your_unclean_data.csv" # Your main raw data (bike counts)
DEVICE_LIST_PATH = "/app/raw_data/device_list.csv" # Path to your device list CSV
OUTPUT_CSV_PATH = "/app/output/final_clean_data.csv"

# --- 1. Load Raw Data (Main Bike Counts) ---
try:
    print(f"Attempting to load raw bike counts data from: {RAW_DATA_PATH}")
    # Read CSV, now we know 'device_name' in this file has an underscore and lowercase 'd'
    # Ensure it's read as string and then rename it immediately for consistency
    df_unclean = pl.read_csv(RAW_DATA_PATH, dtypes={"device_name": pl.String})
    # RENAME THE JOIN KEY IN DF_UNCLEAN TO MATCH DF_DEVICES
    df_unclean = df_unclean.rename({"device_name": "Device name"})

    print(f"Successfully loaded {df_unclean.shape[0]} rows of unclean bike counts data.")
    print("Unclean Bike Counts Data Head:")
    print(df_unclean.head())
    print("Unclean Bike Counts Schema:")
    print(df_unclean.schema) # Verify 'Device name' is now here
except Exception as e:
    print(f"Error loading raw bike counts data: {e}")
    exit(1)

# --- 2. Load Device List Data ---
try:
    print(f"Attempting to load device list from: {DEVICE_LIST_PATH}")
    # Read CSV. 'Device name' in this file has a capital 'D' and a space.
    df_devices = pl.read_csv(DEVICE_LIST_PATH, dtypes={"Device name": pl.String})

    # Validate required columns are present based on the provided headers
    required_device_cols = ["Device name", "Lon (WGS 84)", "Lat (WGS 84)", "X (Lb72)", "Y (Lb72)"]
    if not all(col in df_devices.columns for col in required_device_cols):
        raise ValueError(f"Device list CSV missing one of required columns: {required_device_cols}")

    print(f"Successfully loaded {df_devices.shape[0]} devices from the list.")
    print("Device List Data Head:")
    print(df_devices.head())
    print("Device List Schema:")
    print(df_devices.schema) # Verify 'Device name' is here
except Exception as e:
    print(f"Error loading device list: {e}")
    exit(1)

# --- 3. Preprocess and Join Data with Polars ---
print("Starting Polars preprocessing and data enrichment (joining with geo-coordinates)...")
try:
    # 3.1. Basic cleaning on the main bike counts data
    # Use the now consistent "Device name" for operations if needed before join
    df_temp = df_unclean.with_columns(
        pl.col("Date").str.strptime(pl.Date, "%Y-%m-%d").alias("event_date"),
        # Calculate minutes from 'Time gap': (Time gap - 1) * 15 minutes
        ((pl.col("Time gap") - 1) * 15).alias("minutes_offset")
    ).with_columns(
        # Convert date to datetime and add the minute offset
        (pl.col("event_date").cast(pl.Datetime) + pl.duration(minutes=pl.col("minutes_offset")))
        .alias("timestamp")
    ).drop(["Date", "Time gap", "minutes_offset"]) # Drop original columns

    # 3.2. Perform the join operation to add spatial information
    # The 'on' column is now consistently "Device name"
    df_joined = df_temp.join(
        df_devices.select([
            "Device name", # This is now consistent
            "Lon (WGS 84)",
            "Lat (WGS 84)",
            "X (Lb72)",
            "Y (Lb72)"
        ]),
        on="Device name", # Join on the common column (now consistent)
        how="left"
    )

    # 3.3. Further cleaning, casting, and renaming on the joined data
    df_cleaned = df_joined.with_columns(
        pl.col("Count").cast(pl.Int64, strict=False), # Use 'Count' (capital C)
        pl.col("Average speed").cast(pl.Float64, strict=False), # Use 'Average speed' (capital A, space)
        # Explicitly cast and rename spatial columns
        pl.col("Lon (WGS 84)").cast(pl.Float64, strict=False).alias("longitude"),
        pl.col("Lat (WGS 84)").cast(pl.Float64, strict=False).alias("latitude"),
        pl.col("X (Lb72)").cast(pl.Float64, strict=False).alias("easting"),
        pl.col("Y (Lb72)").cast(pl.Float64, strict=False).alias("northing")
    ).drop_nulls(subset=[ # Drop rows if any of these crucial columns are null
        'timestamp', 'Count', 'Average speed', # Use original names for drop_nulls
        'longitude', 'latitude', 'easting', 'northing' # Use the new alias names here
    ]).filter(pl.col("Count") > 0) # Use 'Count' (capital C)

    # 3.4. Final column selection and renaming for output (database and CSV)
    df_cleaned = df_cleaned.select([
        "timestamp",
        pl.col("Device name").alias("device_name"), # Final rename for DB/CSV output
        pl.col("Count").alias("count"), # Rename for DB/CSV output
        pl.col("Average speed").alias("average_speed"), # Rename for DB/CSV output
        "longitude",
        "latitude",
        "easting",
        "northing"
    ])

    print(f"Successfully joined and cleaned data. New shape: {df_cleaned.shape}")
    print("Cleaned Data Head (with Latitude/Longitude/Easting/Northing):")
    print(df_cleaned.head())
    print("Cleaned Data Schema:")
    print(df_cleaned.schema)

except Exception as e:
    print(f"Error during Polars preprocessing and joining: {e}")
    # Print the full exception for better debugging
    import traceback
    traceback.print_exc()
    exit(1)


# --- 4. Store Cleaned Data to PostgreSQL ---
if not df_cleaned.is_empty():
    conn_str = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
    try:
        print(f"Attempting to connect to PostgreSQL at {DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}...")
        engine = create_engine(conn_str)
        with engine.connect() as conn:
            df_cleaned.write_database(
                table_name="cleaned_data",
                connection=conn,
                if_exists="replace" # or "append", "fail"
            )
        print(f"Successfully wrote {df_cleaned.shape[0]} rows to 'cleaned_data' table in PostgreSQL.")
    except Exception as e:
        print(f"Error storing data to PostgreSQL: {e}")
        print("Please ensure your 'db' service is running and accessible and database credentials are correct.")
        import traceback
        traceback.print_exc() # Print full traceback for DB errors too
else:
    print("No cleaned data to store in PostgreSQL.")


# --- 5. Save Final Clean Data to CSV ---
if not df_cleaned.is_empty():
    try:
        df_cleaned.write_csv(OUTPUT_CSV_PATH)
        print(f"Successfully saved cleaned data to CSV at: {OUTPUT_CSV_PATH}")
        print(f"This file should now be available in your local './output' directory.")
    except Exception as e:
        print(f"Error saving final CSV: {e}")
        import traceback
        traceback.print_exc() # Print full traceback for CSV errors too
else:
    print("No cleaned data to save to CSV.")

print("Preprocessing script finished.")