import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import json

# List of all CSV files with updated Windows path
base_path = r"J:\Australia\Study\Software Now\Assignment2\temperatures"
files = [f"{base_path}\stations_group_{year}.csv" for year in range(1986, 2006)]

# Define possible column name variations
column_mappings = {
    'Station': ['station_name', 'stn_id', 'station', 'location', 'site'],
    'Month': ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
}

# Months for melting
month_columns = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

# Function to find matching column name (case-insensitive)
def find_column(df_columns, possible_names):
    df_columns_lower = [col.lower() for col in df_columns]
    for name in possible_names:
        if name.lower() in df_columns_lower:
            return df_columns[df_columns_lower.index(name.lower())]
    return None

# Read and process all files
dfs = []
for file in files:
    try:
        df = pd.read_csv(file)
        print(f"Columns in {file}: {list(df.columns)}")  # Debug: Print column names

        # Map 'Station' column
        station_col = find_column(df.columns, column_mappings['Station'])
        if not station_col:
            print(f"Warning: Could not find 'Station' column in {file}, skipping.")
            continue

        # Verify all month columns exist
        missing_months = [month for month in month_columns if month not in df.columns]
        if missing_months:
            print(f"Warning: File {file} missing month columns {missing_months}, skipping.")
            continue

        # Rename station column
        df = df.rename(columns={station_col: 'Station'})

        # Melt the monthly columns into 'Month' and 'Temperature'
        df_melted = pd.melt(
            df,
            id_vars=['Station'],
            value_vars=month_columns,
            var_name='Month',
            value_name='Temperature'
        )

        # Map month names to numbers
        month_to_num = {month: i+1 for i, month in enumerate(month_columns)}
        df_melted['Month'] = df_melted['Month'].map(month_to_num)

        # Create a 'Date' column (use year from filename)
        year = int(file.split('_')[-1].split('.')[0])  # Extract year
        df_melted['Date'] = df_melted['Month'].apply(lambda m: datetime(year, m, 1))

        # Select required columns
        df_melted = df_melted[['Date', 'Station', 'Temperature']]
        dfs.append(df_melted)
    except FileNotFoundError:
        print(f"Warning: File {file} not found, skipping.")
    except Exception as e:
        print(f"Error reading {file}: {e}, skipping.")

if not dfs:
    raise ValueError("No valid CSV files were loaded with all required columns.")

all_data = pd.concat(dfs, ignore_index=True)

# Verify required columns
required_columns = ['Date', 'Station', 'Temperature']
missing_cols = [col for col in required_columns if col not in all_data.columns]
if missing_cols:
    raise ValueError(f"Combined data missing required columns: {missing_cols}")

# Ensure Temperature is numeric
all_data['Temperature'] = pd.to_numeric(all_data['Temperature'], errors='coerce')

# Drop rows with invalid dates or temperatures
all_data = all_data.dropna(subset=['Date', 'Temperature'])

# Extract month for season classification
all_data['Month'] = all_data['Date'].dt.month

# Define season function for Australian seasons
def get_season(month):
    if month in [12, 1, 2]:
        return 'Summer'
    elif month in [3, 4, 5]:
        return 'Autumn'
    elif month in [6, 7, 8]:
        return 'Winter'
    elif month in [9, 10, 11]:
        return 'Spring'

# Add season column
all_data['Season'] = all_data['Month'].apply(get_season)

# 1. Calculate seasonal averages
seasonal_avg = all_data.groupby('Season')['Temperature'].mean().round(1)

# Save to average_temp.txt and print contents
with open('average_temp.txt', 'w') as f:
    for season, avg in seasonal_avg.items():
        f.write(f"{season}: {avg}°C\n")
print("\nContents of average_temp.txt:")
for season, avg in seasonal_avg.items():
    print(f"{season}: {avg}°C")

# 2. Calculate per station stats: min, max, range, std
station_stats = all_data.groupby('Station')['Temperature'].agg(['min', 'max', 'std']).dropna()
station_stats['range'] = station_stats['max'] - station_stats['min']
station_stats = station_stats.round(1)

# Find largest temperature range
max_range_value = station_stats['range'].max()
largest_range_stations = station_stats[station_stats['range'] == max_range_value].index.tolist()

# Save to largest_temp_range_station.txt and print contents
with open('largest_temp_range_station.txt', 'w') as f:
    for station in largest_range_stations:
        max_t = station_stats.loc[station, 'max']
        min_t = station_stats.loc[station, 'min']
        rng = station_stats.loc[station, 'range']
        f.write(f"{station}: Range {rng}°C (Max: {max_t}°C, Min: {min_t}°C)\n")
print("\nContents of largest_temp_range_station.txt:")
for station in largest_range_stations:
    max_t = station_stats.loc[station, 'max']
    min_t = station_stats.loc[station, 'min']
    rng = station_stats.loc[station, 'range']
    print(f"{station}: Range {rng}°C (Max: {max_t}°C, Min: {min_t}°C)")

# 3. Find most stable (min std) and most variable (max std) stations
min_std_value = station_stats['std'].min()
max_std_value = station_stats['std'].max()
stable_stations = station_stats[station_stats['std'] == min_std_value].index.tolist()
variable_stations = station_stats[station_stats['std'] == max_std_value].index.tolist()

# Save to temperature_stability_stations.txt and print contents
with open('temperature_stability_stations.txt', 'w') as f:
    f.write("Most Stable: ")
    for i, station in enumerate(stable_stations):
        if i > 0:
            f.write(", ")
        std = station_stats.loc[station, 'std']
        f.write(f"{station}: StdDev {std}°C")
    f.write("\n")
    f.write("Most Variable: ")
    for i, station in enumerate(variable_stations):
        if i > 0:
            f.write(", ")
        std = station_stats.loc[station, 'std']
        f.write(f"{station}: StdDev {std}°C")
    f.write("\n")
print("\nContents of temperature_stability_stations.txt:")
print("Most Stable: ", end="")
for i, station in enumerate(stable_stations):
    if i > 0:
        print(", ", end="")
    std = station_stats.loc[station, 'std']
    print(f"{station}: StdDev {std}°C", end="")
print()
print("Most Variable: ", end="")
for i, station in enumerate(variable_stations):
    if i > 0:
        print(", ", end="")
    std = station_stats.loc[station, 'std']
    print(f"{station}: StdDev {std}°C", end="")
print()

# Plot 1: Seasonal Average Temperatures (Bar Plot)
plt.figure(figsize=(8, 6))
plt.bar(seasonal_avg.index, seasonal_avg.values, color=['#FF6B6B', '#4ECDC4', '#FFD93D', '#1A535C'])
plt.title('Average Temperature by Season')
plt.xlabel('Season')
plt.ylabel('Temperature (°C)')
plt.ylim(0, max(seasonal_avg.values) + 5)
for i, v in enumerate(seasonal_avg.values):
    plt.text(i, v + 0.5, f'{v}°C', ha='center', va='bottom')
plt.tight_layout()
plt.show()

# Plot 2: Top 5 Stations by Temperature Range (Bar Plot)
top_range_stations = station_stats.nlargest(5, 'range')
plt.figure(figsize=(10, 6))
plt.bar(top_range_stations.index, top_range_stations['range'], color=['#FF6B6B', '#4ECDC4', '#FFD93D', '#1A535C', '#6D8299'])
plt.title('Top 5 Stations by Temperature Range')
plt.xlabel('Station')
plt.ylabel('Temperature Range (°C)')
plt.ylim(0, max(top_range_stations['range']) + 5)
for i, v in enumerate(top_range_stations['range']):
    plt.text(i, v + 0.5, f'{v}°C', ha='center', va='bottom')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

# Plot 3: Temperature Stability (Standard Deviation) for Most Stable and Variable Stations
stability_data = station_stats.loc[stable_stations + variable_stations, 'std']
stability_labels = stable_stations + variable_stations
stability_colors = ['#4ECDC4'] * len(stable_stations) + ['#FF6B6B'] * len(variable_stations)
plt.figure(figsize=(10, 6))
plt.bar(stability_labels, stability_data, color=stability_colors)
plt.title('Temperature Stability (Most Stable vs Most Variable Stations)')
plt.xlabel('Station')
plt.ylabel('Standard Deviation (°C)')
plt.ylim(0, max(stability_data) + 1)
for i, v in enumerate(stability_data):
    plt.text(i, v + 0.1, f'{v}°C', ha='center', va='bottom')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

print("\nProcessing complete. Output files created: average_temp.txt, largest_temp_range_station.txt, temperature_stability_stations.txt")
print("Plots displayed.")