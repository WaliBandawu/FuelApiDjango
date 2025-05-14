import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

def load_fuel_data(file_path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
        df = df.rename(columns={'latitude': 'lat', 'longitude': 'lon'})
        df = df.sort_values('Retail Price').groupby(
            ['Truckstop Name', 'Address', 'City', 'State'], as_index=False
        ).first()
        df = df.dropna(subset=['lat', 'lon'])
        df['lat_bin'] = np.floor(df['lat'] * 2) / 2
        df['lon_bin'] = np.floor(df['lon'] * 2) / 2

        # ✅ Add a simplified address key for quick lookup
        df['address_key'] = (df['City'].str.lower().str.strip() + ', ' + df['State'].str.lower().str.strip())

        logger.info(f"Loaded {len(df)} fuel stations with coordinates.")
        return df
    except Exception as e:
        logger.error(f"Failed to load fuel data: {e}")
        return pd.DataFrame()
