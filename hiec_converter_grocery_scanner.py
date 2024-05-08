from PIL import Image
import pillow_heif
import os


def convert_heic_to_png(heic_file, output_folder):
    """For each .HEIC photo file convert the photo to a .PNG and save it with the same name"""
    base_name = os.path.splitext(os.path.basename(heic_file))[0]
    new_file_name = f"{base_name}.png"
    output_file_path = os.path.join(output_folder, new_file_name)

    heif_file = pillow_heif.read_heif(heic_file)
    image = Image.frombytes(
        heif_file.mode,
        heif_file.size,
        heif_file.data,
        "raw",
    )
    image.save(output_file_path, format="png")


def get_files_in_folder(folder_path, extension=None):
    """ for the designated folder_path, grab a list of which photos already exist in that folder """
    files = []
    for file in os.listdir(folder_path):
        if extension:
            if file.upper().endswith(extension.upper()):
                files.append(file)
        else:
            files.append(file)
    return files


# Paths
heic_folder_path = r"C:\Users\Jacob Shughrue\Dropbox\Coding\Python\grocery_scanner\images\heic_dump"
output_folder_path = r"C:\Users\Jacob Shughrue\Dropbox\Coding\Python\grocery_scanner\images\unprocessed"

# Grab a list of the HEIC photos that need to be converted to PNG vs those already converted to PNG previously
heic_files = get_files_in_folder(heic_folder_path, extension=".HEIC")
existing_output_files = get_files_in_folder(output_folder_path, extension=".png")

# Initialize counter
converted_count = 0

# Convert each HEIC file to PNG, if it hasn't been converted already
for heic_file in heic_files:
    base_name = os.path.splitext(heic_file)[0]
    png_file = f"{base_name}.png"
    if png_file not in existing_output_files:
        full_heic_path = os.path.join(heic_folder_path, heic_file)
        convert_heic_to_png(full_heic_path, output_folder_path)
        converted_count += 1

print(f"Number of HEIC photos converted to PNG: {converted_count}")
