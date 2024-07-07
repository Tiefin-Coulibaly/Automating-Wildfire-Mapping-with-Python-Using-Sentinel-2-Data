# Automating Wildfire Mapping with Python Using Sentinel-2

This repository contains a Python script designed for wildfire analysis and mapping using pre- and post-fire Sentinel-2 satellite imagery. The script processes Sentinel-2 data to calculate the Normalized Burn Ratio (NBR) and the Relativized Burn Ratio (RBR), which are essential for assessing the severity of fire impacts.

## Purpose

The primary purpose of this script is to automate the processing of Sentinel-2 imagery to identify and classify areas affected by fire. This script is particularly useful for environmental scientists, GIS analysts, and forestry professionals who need to monitor and evaluate fire severity over large areas efficiently.

## Key Functionalities

### 1. User Input:

- Prompts the user to enter the paths for pre-fire and post-fire Sentinel-2 image zip files and the study area shapefile.

### 2. Data Unzipping

- Unzips the provided Sentinel-2 image files into temporary directories for further processing.

### 3. Image Resampling and Clipping

- Resamples the Sentinel-2 bands to a 10-meter resolution.
- Clips the resampled images to the specified study area.

### 4. Water Body Masking

- Removes water bodies from the study area using the Normalized Difference Water Index (NDWI).

### 5. NBR Calculation

- Computes the NBR for both pre-fire and post-fire images to assess fire impact.

### 6. RBR Calculation

- Calculates the RBR to determine the severity of the fire.

### 7. RBR Reclassification

- Allows the user to reclassify the RBR based on a specified threshold.
- Provides predefined reclassification ranges based on USGS standards.

### 8. Burnt Area Calculation

- Computes the total burnt area in hectares based on the reclassified RBR.

### 9. Visualization

- Generates a plot of the fire severity classification and saves it as a PNG file.

### 10. Output Cleanup

- Cleans up temporary directories and unnecessary files to maintain a tidy workspace.

## License

This project is licensed under the MIT License.

## Note

Make sure to read the `User Manual` before using the script.
