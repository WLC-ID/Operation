import os
from PIL import Image
import time
import filecmp

current_time_unix = int(time.time())

def compress_image_1(input_path, output_path):
    # with Image.open(input_path) as image:
    #     image.save(output_path, format="PNG")
    try:
        with Image.open(input_path) as image:
            image.save(output_path, optimize=True, quality=75)
    except Exception as e:
        print(f"Error: {e}")

def compress_image_2(input_path, output_path):
    with Image.open(input_path) as image:
        image.save(output_path, format="PNG")

def overwrite_files(fromfile, tofile):
    file1 = fromfile
    file2 = tofile
    with open(file1, "rb") as f1:
        content = f1.read()
    with open(file2, "wb") as f2:
        f2.write(content)

def compress_images_recursively(input_dir, output_dir, callback):
    for dirpath, dirnames, filenames in os.walk(input_dir):

        insizeDir = {}
        outsizeDir = {}
        for dirname in dirnames:
            input_path = os.path.join(dirpath, dirname)
            output_path = input_path.replace(input_dir, output_dir)
            os.makedirs(output_path, exist_ok=True)
        for filename in filenames:
            if filename.lower().endswith(('.png')):
                input_path = os.path.join(dirpath, filename)
                output_path = input_path.replace(input_dir, output_dir)
                callback(input_path, output_path)
                insize = os.path.getsize(input_path)/1024
                outsize = os.path.getsize(output_path)/1024
                
                if insize < outsize:
                    overwrite_files(input_path, output_path)
                    # print(f"\tExcluded {filename}, IN: {insize:.2f} KB, OUT: {outsize:.2f} KB")
                    outsize = insize
                
                key = os.path.normpath(dirpath)
                if (key not in insizeDir.keys()):
                    insizeDir[key] = 0
                    outsizeDir[key] = 0
                insizeDir[key] += insize
                outsizeDir[key] += outsize
            else:
                input_path = os.path.join(dirpath, filename)
                output_path = input_path.replace(input_dir, output_dir)
                overwrite_files(input_path, output_path)
                insize = os.path.getsize(input_path)/1024
                outsize = os.path.getsize(output_path)/1024
                insizeDir[key] += insize
                outsizeDir[key] += outsize
        for each in insizeDir.keys():
            if insizeDir[each]-outsizeDir[each] < 0.01:
                continue
            print(f"{each}: {insizeDir[each]:.2f} KB -> {outsizeDir[each]:.2f} KB ({100*((outsizeDir[each]/insizeDir[each])-1):.2f}%)")

def get_folder_size(folder_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for file in filenames:
            file_path = os.path.join(dirpath, file)
            total_size += os.path.getsize(file_path)
    return total_size/1024

input_dir = "./textures-compressed-639430"
output_dir = "./textures-compressed-" + str(current_time_unix % 1000000)
before = get_folder_size(input_dir)
print(f"Before: {before:.2f} KB.")
compress_images_recursively(input_dir, output_dir, compress_image_1)
after = get_folder_size(output_dir)
print(f"After: {after:.2f} KB.")
if (after == before):
    print(f"Percentage: 0%")
    exit(0)
print(f"Percentage: {(((after/before)-1)*100):.2f}%")