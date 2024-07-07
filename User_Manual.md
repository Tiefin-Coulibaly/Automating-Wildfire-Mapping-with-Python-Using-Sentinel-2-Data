# User Manual for the WildfireMapping.py Script

## Requirements

1. ArcGIS Pro License: Ensure you have a valid ArcGIS Pro license.
2. Spatial Analyst Module License: Ensure you have a license for the Spatial Analyst module.
3. IDE: Use an integrated development environment (IDE) such as Visual Studio Code (VS Code), PyCharm, or any other IDE of your choice.

## Steps

### 1. Create an ArcGIS Pro Project

- Open ArcGIS Pro.
- Create a new project selecting _Map_.
- Pick a location for your new project.

### 2. Clone the ArcGIS Pro Python Environment

Cloning the ArcGIS Pro Python environment ensures you can install additional libraries without affecting the default environment.

While your ArcGIS pro is open:

- Go to `Project` > `Package manager` > `Active Environment`.
- Select the gear ⚙️ icon.
- Click on `arcgispro-py (Default)`.
- Select the three dots symbol `...`.
- Choose `clone`.

The cloning process may take some time to complete.

After the process is done, make sure to memorize the path to the cloned environment, as you will need it when selecting the interpreter in your IDE.

### 3. Set Up Your IDE

In your IDE, ensure you select the Python interpreter from your cloned ArcGIS Pro environment.

For VS Code for example:

- Open VS Code.
- Install the Python extension if not already installed.
- Press `Ctrl + Shift + P` on your keyboard.
- Type `Select Interpreter` and select `Python: Select Interpreter`.
- Navigate to your cloned ArcGIS Pro environment folder and select `python.exe`. The path to the interpreter is typically: `C:\Users\<YourUsername>\Anaconda3\envs\arcgis_clone\python.exe`

### 4. Install Necessary Libraries

If the required libraries are not already installed, you can install them in the package manager.

### 5. Update Workspace Path in the Code

In the provided script, replace the line below with your ArcGIS Pro project's geodatabase path.

Original line:
`arcpy.env.workspace = r"C:\Users\ctief\Documents\ArcGIS\Projects\MyProject17\MyProject17.gdb"`

Updated line:
`arcpy.env.workspace = r"C:\Path\To\Your\Project\YourProject.gdb"`

Make sure to use the correct path to your project's geodatabase file.

### 6. User Interaction and Inputs

When running the script, users will be prompted to enter the paths for the pre-fire and post-fire Sentinel-2 image zip files and the study area shapefile.

- **Pre-fire Sentinel-2 image zip file:** Enter the full path to the zip file containing the pre-fire Sentinel-2 images.
- **Post-fire Sentinel-2 image zip file:** Enter the full path to the zip file containing the post-fire Sentinel-2 images.
- **Study area shapefile:** Enter the full path to the shapefile defining the study area.

The script will process these inputs, perform the necessary analysis, and provide intermediate results, including the Relativized Burn Ratio (RBR). The user will then be asked to provide a threshold value to reclassify the RBR, which helps in identifying burnt areas accurately.

- **Threshold input:** After analyzing the initial RBR results, enter the threshold value that eliminates false positives and correctly classifies the burnt areas.

The script will generate the final classified map and save it in the `C:\temp\fire_analysis\output` folder of your machine.

Example Interaction:

```
Enter the path to the pre-fire Sentinel-2 image zip file: C:\Data\Sentinel2_PreFire.zip
Enter the path to the post-fire Sentinel-2 image zip file: C:\Data\Sentinel2_PostFire.zip
Enter the path to the shapefile of the study area: C:\Data\StudyArea.shp
Enter the threshold to reclassify the RBR: 0.1
```

By following this manual, users will be able to set up their environment, run the script, and analyze the fire severity effectively.
