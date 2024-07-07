#=================================================================================================
# Program   : WildfireMapping.py
#
# Purpose   : The primary purpose of this script is to automate the processing of Sentinel-2 
#             imagery to identify and classify areas affected by fire. This script is particularly 
#             useful for environmental scientists, GIS analysts, and forestry professionals who 
#             need to monitor and evaluate fire severity over large areas efficiently.
#
# Author: Mamadou Coulibaly                                                           July 6, 2024
#=================================================================================================

# Import libraries
import os
import zipfile
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import datetime as dt
import arcpy
from arcpy.sa import *
import shutil
import numpy as np

# Set environment settings for the script
arcpy.env.workspace = r"C:\Users\ctief\Documents\ArcGIS\Projects\MyProject17\MyProject17.gdb"
arcpy.env.overwriteOutput = True

print("="*240)

# User inputs
pre_fire_zip = input("Enter the path to the pre-fire Sentinel-2 image zip file: ")
post_fire_zip = input("Enter the path to the post-fire Sentinel-2 image zip file: ")
study_area_shapefile = input("Enter the path to the shapefile of the study area: ")

# Start time
start_time = dt.datetime.now()

# Define unzip directories
temp_dir = r"C:\temp\fire_analysis"
pre_fire_unzip_dir = os.path.join(temp_dir, "pre_fire")
post_fire_unzip_dir = os.path.join(temp_dir, "post_fire")

# Create directories if they don't exist
os.makedirs(pre_fire_unzip_dir, exist_ok=True)
os.makedirs(post_fire_unzip_dir, exist_ok=True)

def unzip_data(zip_path, extract_to):
    """Unzip data to specified directory."""
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)

def resample_and_clip_sentinel_image(directory, input_bands, study_area):
    """Resample and clip Sentinel-2 composite image based on study area."""
    for root, dirs, files in os.walk(directory):
        for file in files:
            filePath = os.path.join(root, file)
            if "R10m" in root and "B" in file:
                input_bands.append(filePath)
            elif "R20m" in root and "B12" in file:
                input_bands.append(filePath)

    # Create a composite image
    compositeImage = arcpy.management.CompositeBands(input_bands, "in_memory/compositeImage")

    # Resample all bands to 10m
    compositeImageResampled = arcpy.management.Resample(
        in_raster=compositeImage,
        out_raster="in_memory/compositeImageResampled",
        cell_size=10,
        resampling_type="BILINEAR"
    )

    # Clip the study area
    study_area_clipped = arcpy.management.Clip(
        in_raster=compositeImageResampled,
        rectangle=None,
        out_raster=f"in_memory/studyArea_{os.path.basename(input_bands[0]).split('_')[1]}",
        in_template_dataset=study_area,
        clipping_geometry="NONE",
        maintain_clipping_extent="NO_MAINTAIN_EXTENT"
    )

    # Delete unnecessary data
    arcpy.management.Delete("compositeImage")
    arcpy.management.Delete("compositeImageResampled")

    return study_area_clipped

def water_body_mask(study_area):
    """Remove water bodies from the study area using NDWI."""

    # Convert the study_area result object to a string path
    study_area_path = study_area.getOutput(0)
    green_band = arcpy.Raster(f"{study_area_path}/Band_2")
    nir_band = arcpy.Raster(f"{study_area_path}/Band_4")

    # Calculate NDWI
    ndwi = Float(green_band - nir_band) / Float(green_band + nir_band)

    # Reclassify NDWI to separate water bodies
    remap = RemapRange([[-1, 0, 1], [0, 1, "NoData"]])
    ndwi_reclassified = Reclassify(ndwi, "Value", remap)

    # Extract the study area by mask
    study_area_masked = ExtractByMask(
        in_raster=study_area_path,
        in_mask_data=ndwi_reclassified,
        extraction_area="INSIDE"
    )

    # Save the masked study area
    study_area_masked.save(f"studyAreaMasked_{os.path.basename(study_area_path)}")

    return study_area_masked.catalogPath

def calculate_nbr(study_area_masked_path):
    """Calculate the Normalized Burn Ratio (NBR)."""

    # Load NIR and SWIR bands
    nir_band = arcpy.Raster(f"{study_area_masked_path}/Band_4")
    swir_band = arcpy.Raster(f"{study_area_masked_path}/Band_5")

    # Calculate NBR
    nbr = Float(nir_band - swir_band) / Float(nir_band + swir_band)

    # Save the NBR result
    nbr.save(f"NBR_{os.path.basename(study_area_masked_path)}")

    return nbr

def calculate_rbr(master_nbr, slave_nbr):
    """Calculate the Relativized Burn Ratio (RBR)."""

    dnbr = arcpy.Raster(master_nbr) - arcpy.Raster(slave_nbr)
    rbr = dnbr / (arcpy.Raster(master_nbr) + 1.001)
    rbr.save("RBR")
    
    return rbr


def plot_results(reclass_rbr, burnt_area):
    """Plot the results and save the figure."""
    class_names = ["None", "Unburned", "Low severity", "Moderate low severity", "Moderate high severity", "High severity"]
    class_colors = ["#FFFFFF", "#00ff00", "#ffff00", "#ff9000", "#ff4d00", "#ff00ff"]
    cmap = ListedColormap(class_colors)

    rbr_array = arcpy.RasterToNumPyArray(reclass_rbr)
    extent = arcpy.Raster(reclass_rbr).extent

    fig, ax = plt.subplots(figsize=(10, 4))
    cax = ax.imshow(rbr_array, cmap=cmap, vmin=1, vmax=6, extent=[extent.XMin, extent.XMax, extent.YMin, extent.YMax])

    ax.set_title(f"Fire Severity Classification (Burnt Area: {burnt_area:.2f} ha)")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")

    cbar = fig.colorbar(cax, ticks=[1.45, 2.25, 3.05, 3.95, 4.74, 5.6])
    cbar.set_ticklabels(class_names, fontsize=7)


    # Save the plot
    output_dir = os.path.join(temp_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    fig.savefig(os.path.join(output_dir, "fire_severity_classification.png"), dpi=300)


    print(f"The final map has been saved in the folder: {output_dir}")
    print("="*240)


def process_data(pre_fire_zip, post_fire_zip, study_area):
    """Process Sentinel-2 data."""
    try:
        unzip_data(pre_fire_zip, pre_fire_unzip_dir)
        unzip_data(post_fire_zip, post_fire_unzip_dir)

        # Initialize input_bands list
        input_bands_pre = []
        input_bands_post = []

        # Clip study area
        pre_fire_study_area = resample_and_clip_sentinel_image(pre_fire_unzip_dir, input_bands_pre, study_area)
        post_fire_study_area = resample_and_clip_sentinel_image(post_fire_unzip_dir, input_bands_post, study_area)

        # Remove water bodies
        pre_fire_study_area_masked = water_body_mask(pre_fire_study_area)
        post_fire_study_area_masked = water_body_mask(post_fire_study_area)

        # Calculate NBR
        pre_fire_nbr = calculate_nbr(pre_fire_study_area_masked)
        post_fire_nbr = calculate_nbr(post_fire_study_area_masked)

        # Calculate RBR
        rbr = calculate_rbr(pre_fire_nbr, post_fire_nbr)

        print("-"*240)
        print("The Relativized Burn Ratio (RBR) has been generated and saved in the geodatabase of your project. Please analyze it to identify the threshold for burnt areas. Remember that positive values represent burnt areas while negative values represent unburnt areas.\nAfter finding the threshold that eliminates false positives, come back here and provide that information.")

        # User input for threshold
        threshold = float(input("Enter the threshold to reclassify the RBR: "))
        print("-"*240)

        # Define reclassification ranges based on USGS proposed reclassification
        remap = RemapRange([["NoData", "NoData", 1], [-0.5, threshold, 2], [threshold, 0.269, 3], [0.270, 0.439, 4], [0.440, 0.659, 5], [0.660, 1.300, 6]])

        # Reclassify RBR
        reclass_rbr = Reclassify(rbr, "Value", remap)
        reclass_rbr.save("RBR_reclassified")

        # Calculate burnt area
        rbr_array = arcpy.RasterToNumPyArray(reclass_rbr)
        burnt_pixels = rbr_array >= 3
        pixel_area = reclass_rbr.meanCellWidth ** 2
        burnt_area = (np.sum(burnt_pixels) * pixel_area) / 10000

        # Convert burnt areas to feature class
        burnt_areas_fc = "BurntAreas"
        shp_remap = RemapRange([[1, 2, "NoData"], [3, 6, 1]])
        reclass_rbr_to_shp = Reclassify(reclass_rbr, "Value", shp_remap)
        reclass_rbr_to_shp.save("RBR_reclass_to_shp")
        arcpy.conversion.RasterToPolygon(in_raster=reclass_rbr_to_shp, out_polygon_features=burnt_areas_fc, simplify="NO_SIMPLIFY", raster_field="Value")
        
        # Plot the results
        plot_results(reclass_rbr, burnt_area)

    except Exception as e:
        print(f"Error processing data: {e}")
    finally:
        # Clean up
        shutil.rmtree(pre_fire_unzip_dir)
        shutil.rmtree(post_fire_unzip_dir)

    # Delete unnecessary files
    for i in arcpy.ListRasters():
        if "RBR" not in i or "shp" in i:
            arcpy.management.Delete(i)

# Process the data
process_data(pre_fire_zip, post_fire_zip, study_area_shapefile)

# End time
end_time = dt.datetime.now()
print("Processing Time: ", end_time - start_time)