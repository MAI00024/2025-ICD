#!/usr/bin/env python
# coding: utf-8

import os
import glob
import shutil
import random
import yaml
from PIL import Image
from sklearn.model_selection import GroupKFold
from PIL import Image, ImageEnhance

def check_file_names_consistency(folders):
    """
    Check the consistency of filenames across different folders.
    
    Args:
        folders (list): List of folder paths to check
    """
    file_names = {}
    
    for folder in folders:
        file_names[folder] = set()
        for filename in os.listdir(folder):
            file_base_name, _ = os.path.splitext(filename)
            file_base_name_without_suffix = (
                file_base_name.replace('_DIC', '')
                .replace('_RFP', '')
                .replace('_GFP', '')
            )
            file_names[folder].add(file_base_name_without_suffix)
    
    is_all_same = all(file_names[folders[0]] == file_names[folder] for folder in folders)
    
    if is_all_same:
        print("All folders have consistent filenames.")
    else:
        print("Different filenames found across folders.")
        for i in range(len(folders)):
            for j in range(i + 1, len(folders)):
                different_files = file_names[folders[i]] ^ file_names[folders[j]]
                if different_files:
                    print(f"Different filenames between {folders[i]} and {folders[j]}: {different_files}")

def copy_images_to_destination(source_folders, destination_folder):
    """
    Copy images from multiple source folders to a destination folder.
    
    Args:
        source_folders (list): List of source folder paths
        destination_folder (str): Destination folder path
    """
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    
    for folder in source_folders:
        image_files = glob.glob(os.path.join(folder, "*.jpg")) + \
                     glob.glob(os.path.join(folder, "*.png"))
        
        for image_file in image_files:
            file_name = os.path.basename(image_file)
            destination_file_path = os.path.join(destination_folder, file_name)
            shutil.copy(image_file, destination_file_path)
    
    print(f"All images have been copied to {destination_folder}")

def process_labels(source_folder, destination_folder):
    """
    Process and copy label files, excluding classes 1 and 2.
    
    Args:
        source_folder (str): Source folder containing label files
        destination_folder (str): Destination folder for processed labels
    """
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    txt_files = glob.glob(os.path.join(source_folder, "*.txt"))
    
    for txt_file in txt_files:
        with open(txt_file, 'r') as file:
            lines = file.readlines()
        
        # Select only lines that don't start with class 1 or 2
        new_lines = [line for line in lines if not line.startswith(('1 ', '2 '))]
        
        file_name = os.path.basename(txt_file)
        destination_file_path = os.path.join(destination_folder, file_name)
        with open(destination_file_path, 'w') as file:
            file.writelines(new_lines)

def count_labels(folder):
    """
    Count the number of instances for each class in label files.
    
    Args:
        folder (str): Folder containing label files
    """
    class_counts = {0: 0, 1: 0, 2: 0}
    class_names = {0: 'S.C', 1: 'D.C', 2: 'M.C'}
    
    txt_files = glob.glob(os.path.join(folder, "*.txt"))
    
    for txt_file in txt_files:
        with open(txt_file, 'r') as file:
            lines = file.readlines()
            for line in lines:
                class_id = int(line.split()[0])
                if class_id in class_counts:
                    class_counts[class_id] += 1
    
    print("Class ID counts:")
    for class_id, count in class_counts.items():
        print(f"{class_names[class_id]}: {count}")

def move_and_convert_dic_images(source_folder, target_folder):
    """
    Select and convert DIC images to PNG format.
    
    Args:
        source_folder (str): Source folder containing DIC images
        target_folder (str): Target folder for converted PNG images
    """
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    for filename in os.listdir(source_folder):
        if filename.endswith(('DIC.jpg', 'DIC.jpeg', 'DIC.png', 'DIC.tif')):
            source_path = os.path.join(source_folder, filename)
            new_filename = filename.replace('_DIC', '').rsplit('.', 1)[0] + '.png'
            target_path = os.path.join(target_folder, new_filename)
            
            image = Image.open(source_path)
            image.save(target_path, 'PNG')

def extract_device_id(label_filename):
    """
    Extract device ID from label filename.
    
    Args:
        label_filename (str): Label filename
    
    Returns:
        str: Device ID or None if not found
    """
    parts = label_filename.split('_')
    return f"{parts[0]}_{parts[1]}" if len(parts) >= 3 else None

def get_image_filename(label_filename, image_type):
    """
    Generate image filename from label filename.
    
    Args:
        label_filename (str): Label filename
        image_type (str): Type of image (e.g., DIC, RFP, GFP)
    
    Returns:
        str: Generated image filename
    """
    return label_filename.replace(".txt", f"{image_type}.png")

def split_dataset_inter_device(images_path, labels_path, output_path, n_splits=5, random_state=42):
    """
    Split dataset into train and validation sets using GroupKFold with K=5 folds.
    
    Args:
        images_path (str): Path to image directory
        labels_path (str): Path to labels directory
        output_path (str): Output directory for split datasets
        n_splits (int): Number of folds for cross-validation (default: 5)
        random_state (int): Random state for reproducibility
    """
    random.seed(random_state)

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    all_labels = glob.glob(os.path.join(labels_path, "*.txt"))
    random.shuffle(all_labels)
    
    device_ids = [extract_device_id(os.path.basename(label)) for label in all_labels]

    # Split using GroupKFold with K=5
    gkf = GroupKFold(n_splits=n_splits)
    
    # Create K different train/valid splits
    for fold, (train_indices, valid_indices) in enumerate(gkf.split(all_labels, groups=device_ids)):
        train_labels = [all_labels[i] for i in train_indices]
        valid_labels = [all_labels[i] for i in valid_indices]

        # Create fold-specific directory
        fold_output_path = os.path.join(output_path, f"fold_{fold}")
        os.makedirs(fold_output_path, exist_ok=True)

        # Process each set (train and valid)
        for set_name, labels in [("train", train_labels), ("valid", valid_labels)]:
            set_images_path = os.path.join(fold_output_path, set_name, "images")
            set_labels_path = os.path.join(fold_output_path, set_name, "labels")
            
            os.makedirs(set_images_path, exist_ok=True)
            os.makedirs(set_labels_path, exist_ok=True)

            file_list_output_file = os.path.join(fold_output_path, f"{set_name}.txt")
            with open(file_list_output_file, 'w') as file_list_f:
                for label_path in labels:
                    label_filename = os.path.basename(label_path)
                    image_filename = get_image_filename(label_filename, "")
                    image_path = os.path.join(images_path, image_filename)
                    
                    shutil.copy(image_path, os.path.join(set_images_path, image_filename))
                    shutil.copy(label_path, os.path.join(set_labels_path, label_filename))
                    file_list_f.write(os.path.join(set_images_path, image_filename) + '\n')

        # Create YAML configuration file for each fold
        yaml_data = {
            "names": ['S.C'],
            "nc": 1,
            "path": fold_output_path,
            "train": "train.txt",
            "val": "valid.txt"
        }

        with open(os.path.join(fold_output_path, "custom.yaml"), "w") as f:
            yaml.dump(yaml_data, f)

        print(f"Created fold {fold} with train: {len(train_labels)}, "
              f"valid: {len(valid_labels)} images.")


def enhance_fluorescence(image_path, transparency, enhance_factor=1.5, threshold=50, background_alpha=50):
    """
    Enhance fluorescence images and adjust transparency.
    
    Args:
        image_path (str): Path to fluorescence image
        transparency (int): Transparency level for enhanced areas
        enhance_factor (float): Contrast enhancement factor
        threshold (int): Threshold for pixel enhancement
        background_alpha (int): Background transparency level
        
    Returns:
        PIL.Image: Enhanced image
    """
    image = Image.open(image_path).convert("RGBA")
    enhancer = ImageEnhance.Contrast(image)
    image_enhanced = enhancer.enhance(enhance_factor)
    
    datas = image_enhanced.getdata()
    new_data = []
    for item in datas:
        if item[0] > threshold or item[1] > threshold or item[2] > threshold:
            new_data.append((item[0], item[1], item[2], transparency))
        else:
            new_data.append((item[0], item[1], item[2], background_alpha))
    image_enhanced.putdata(new_data)
    return image_enhanced

def process_merged_images(images_folder, output_folder, brightness_factor=0.9, final_contrast_factor=1.5):
    """
    Merge and process DIC, RFP, and GFP images.
    
    Args:
        images_folder (str): Source folder containing all images
        output_folder (str): Output folder for merged images
        brightness_factor (float): Final brightness adjustment factor
        final_contrast_factor (float): Final contrast adjustment factor
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    image_groups = {}
    for filename in os.listdir(images_folder):
        if filename.endswith(('.jpg', '.jpeg', '.png', '.tif')):
            parts = filename.split('_')
            base_name = '_'.join(parts[:-1])  # Remove the last part (DIC/RFP/GFP)
            image_type = parts[-1].split('.')[0]
            image_groups.setdefault(base_name, {})[image_type] = os.path.join(images_folder, filename)

    for base_name, image_paths in image_groups.items():
        dic_path = image_paths.get('DIC')
        rfp_path = image_paths.get('RFP')
        gfp_path = image_paths.get('GFP')

        if not (dic_path and rfp_path and gfp_path):
            print(f"Missing images for {base_name}, skipping...")
            continue

        output_path = os.path.join(output_folder, base_name + '.png')

        # Process images
        dic_image = Image.open(dic_path).convert("RGBA")
        rfp_enhanced = enhance_fluorescence(rfp_path, 110)
        gfp_enhanced = enhance_fluorescence(gfp_path, 110)
        
        # Enhance DIC image
        dic_image_contrasted = ImageEnhance.Contrast(dic_image).enhance(1)
        dic_image_sharpened = ImageEnhance.Sharpness(dic_image_contrasted).enhance(5)

        # Merge images
        combined_image = Image.alpha_composite(dic_image_sharpened, rfp_enhanced)
        combined_image = Image.alpha_composite(combined_image, gfp_enhanced)

        # Final adjustments
        combined_image = ImageEnhance.Contrast(combined_image).enhance(final_contrast_factor)
        adjusted_image = ImageEnhance.Brightness(combined_image).enhance(brightness_factor)
        adjusted_image.save(output_path)


def main():
    # Set base paths
    base_folders = [
        '../../../data/images/images_DIC',
        '../../../data/images/images_RFP',
        '../../../data/images/images_GFP',
        '../../../data/labels'
    ]
    
    processed_data_path = './processed_data'
    images_origin_all = os.path.join(processed_data_path, 'images_origin_all')
    labels_all = os.path.join(processed_data_path, 'labels_all')
    merged_images = os.path.join(processed_data_path, 'merged_processed_images_for_SC')
    split_output_dir = 'split_for_yolo_detection'

    # 1. Check filename consistency
    check_file_names_consistency(base_folders)

    # 2. Copy images
    copy_images_to_destination(base_folders[:3], images_origin_all)
    
    # 3. Process labels
    process_labels(base_folders[3], labels_all)
    
    # 4. Count labels
    count_labels(labels_all)
    
    # 5. Process and merge images
    process_merged_images(images_origin_all, merged_images)
    
    # 6. Split dataset
    split_dataset_inter_device(merged_images, labels_all, split_output_dir)

if __name__ == "__main__":
    main()