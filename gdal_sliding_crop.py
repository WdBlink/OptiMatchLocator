from osgeo import gdal
import numpy as np
import os
from tqdm.auto import tqdm

def crop_tif_images_with_gdal(input_directory, output_directory, window_size, step_size):
    """
    Crop .tif images in the given directory and its subdirectories using GDAL,
    with a sliding window approach. The cropped images' names reflect the original
    image's name, path, and cropping position. A progress bar displays the process.
    
    Parameters:
    - input_directory: The directory to search for .tif images.
    - output_directory: The directory where cropped images will be saved.
    - window_size: A tuple of (width, height) for the crop window size.
    - step_size: The step size to move the window across and down the images.
    """
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    # Supported image format
    supported_format = 'tif'
    
    # Collect all .tif images first to initialize the progress bar
    tif_paths = []
    for subdir, _, files in os.walk(input_directory):
        for file in files:
            if file.lower().endswith('.' + supported_format):
                tif_paths.append(os.path.join(subdir, file))
                
    progress_bar = tqdm(total=len(tif_paths), desc="Cropping TIF Images")
    
    for tif_path in tif_paths:
        try:
            dataset = gdal.Open(tif_path, gdal.GA_ReadOnly)
            if dataset is None:
                continue
            
            img_width, img_height = dataset.RasterXSize, dataset.RasterYSize
            for top in range(0, img_height - window_size[1] + 1, step_size):
                for left in range(0, img_width - window_size[0] + 1, step_size):
                    # Calculate the bottom right corner of the cropping box
                    bottom = top + window_size[1]
                    right = left + window_size[0]
                    
                    # Generate cropped image name based on the original path and crop position
                    relative_path = os.path.relpath(tif_path, input_directory)
                    base_name, ext = os.path.splitext(relative_path)
                    cropped_img_name = f"{base_name.replace(os.sep, '_')}_{left}_{top}_{right}_{bottom}{ext}"
                    cropped_img_path = os.path.join(output_directory, cropped_img_name)
                    
                    # Read and crop the image
                    srcwin = (left, top, window_size[0], window_size[1])
                    gdal.Translate(cropped_img_path, dataset, srcWin=srcwin, format='GTiff')
        except Exception as e:
            print(f"Error processing {tif_path}: {e}")
        finally:
            progress_bar.update(1)
    
    progress_bar.close()

# Example usage with progress bar and updated naming convention for .tif images
# Note: Adjust 'input_dir' and 'output_dir' as per your directory structure
input_dir = '/home/user/data/Xijiang-0602/'
output_dir = '/home/user/data/cropped_images/XiJiang-0602/'
window_size = (1000, 1000)  # Window size (width, height)
step_size = 1000  # Step size for the sliding window

crop_tif_images_with_gdal(input_dir, output_dir, window_size, step_size)
