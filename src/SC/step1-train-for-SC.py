#!/usr/bin/env python
# coding: utf-8

import os
import wandb
import torch
import gc
import subprocess
import shutil
from pathlib import Path

def setup_yolov9():
    """Setup YOLOv9 repository and copy required files"""
    
    # 1) Clone YOLOv9 repository if it does not exist
    if not Path('yolov9').exists():
        subprocess.run(['git', 'clone', 'https://github.com/WongKinYiu/yolov9.git'], check=True)
        
        # Install requirements only if it's a fresh clone
        os.chdir('yolov9')
        subprocess.run(['pip', 'install', '-qr', 'requirements.txt'], check=True)
        os.chdir('..')  # Return to original directory
    
    # 2) Change to yolov9 directory for the rest of the setup
    os.chdir('yolov9')
    
    # # 3) Download YOLOv9-e pre-trained weights if not exists
    # weights_path = Path('./yolov9-e.pt')
    # if not weights_path.exists():
    #     print("Downloading YOLOv9-e weights...")
    #     url = 'https://github.com/WongKinYiu/yolov9/releases/download/v0.1/yolov9-e.pt'
    #     response = requests.get(url, stream=True)
    #     response.raise_for_status()
        
    #     with open(weights_path, 'wb') as f:
    #         for chunk in response.iter_content(chunk_size=8192):
    #             if chunk:
    #                 f.write(chunk)
        
    #     print("YOLOv9-e weights downloaded successfully")
    
    # 4) Copy the split_for_yolo_detection folder into the yolov9 directory
    source_dir = Path('../split_for_yolo_detection')
    dest_dir   = Path('./split_for_yolo_detection')
    
    if source_dir.exists():
        try:
            if dest_dir.exists():
                shutil.rmtree(dest_dir)  
            shutil.copytree(source_dir, dest_dir)
            print("Copied split_for_yolo_detection to yolov9 directory")
            
        except PermissionError:
            print("Permission Error: Try running the script with administrator privileges")
            raise
        except Exception as e:
            print(f"Error copying directory: {e}")
            raise
    else:
        raise FileNotFoundError(
            "split_for_yolo_detection directory not found in the parent directory"
        )

def train_model(fold):
    """Train model for each fold
    
    Args:
        fold: Current fold number
    """
    cmd = [
        'python', 'train_dual.py',
        '--workers', '0',
        '--device', '0',
        '--batch', '4',
        '--data', f'./split_for_yolo_detection/fold_{fold}/custom.yaml',
        '--img', '1024',
        '--cfg', 'models/detect/yolov9-e.yaml',
        '--weights', f'../pretrainedmodel_weight_for_sc/test_fold_{fold}/weights/best.pt',
        '--name', f'test_fold_{fold}',
        '--project', 'Yolov9_finetunedmodel',
        '--hyp', 'hyp.scratch-high.yaml',
        '--min-items', '0',
        '--epochs', '100',        
        '--close-mosaic', '15'
    ]
    
    subprocess.run(cmd)
    torch.cuda.empty_cache()
    gc.collect()

def validate_model(fold):
    """Validate model for each fold
    
    Args:
        fold: Current fold number
    """
    cmd = [
        'python', 'val_dual.py',
        '--data', f'./split_for_yolo_detection/fold_{fold}/custom.yaml',
        '--img', '1024',
        '--batch', '4',
        '--conf', '0.001',
        '--iou', '0.7',
        '--device', '0',
        '--weights', f'./Yolov9_finetunedmodel/test_fold_{fold}/weights/best.pt',
        '--save-json',
        '--save-txt',
        '--name', f'test_fold_{fold}'
    ]
    
    subprocess.run(cmd)
    torch.cuda.empty_cache()
    gc.collect()

def main():
    # Setup WandB
    wandb.login(key="Your Key")    
    
    # Setup YOLOv9 and copy required files
    setup_yolov9()
    
    # Train and validate for each fold
    for fold in range(5):
        print(f"\nProcessing fold {fold}")
        
        print(f"Training fold {fold}...")
        train_model(fold)
        
        print(f"Validating fold {fold}...")
        validate_model(fold)        
        break  # "Only the 0th fold is executed. (If you want additional training, comment out this line)"

if __name__ == "__main__":
    main()