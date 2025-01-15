# 2025-ICD
## How to run
### 1. Provide execution permissions to the shell script files
```
chmod +x run_pretrain_sc.sh
chmod +x run_pretrain_dc.sh
chmod +x run_sc.sh
chmod +x run_dc.sh
```

### 2. Execute the shell scripts
#### 2-1. Pretraining
* SC Pretraining
```
./run_pretrain_sc.sh
```

* DC Pretraining
```
./run_pretrain_sc.sh
```

#### 2-2. Finetuning
* SC Finetuning
```
./run_sc.sh
```

* DC Finetuning
```
./run_dc.sh
```


## File Description
```
├── src/
│   ├── pretrain/
│   │   ├── SC/
│   │   │   ├── step0-preprocess-for-SC.py    # Merge and preprocess three channels (SC)
│   │   │   └── step1-pretrain-for-SC.py      # Three-channel pretraining (SC) 
│   │   │
│   │   └── DC/
│   │       ├── step0-preprocess-for-DC.py     # Merge and preprocess three channels (DC)
│   │       └── step1-pretrain-for-DC.py       # Three-channel pretraining (DC)
│   │
│   ├── SC/                                    # SC finetuning
│   │   ├── step0-preprocess-for-SC.py   
│   │   ├── step1-train-for-SC.py        
│   │   └── pretrainedmodel_weight_for_sc/     # Pretrained weights for SC
│   │
│   └── DC/                                    # DC finetuning 
│       ├── step0-preprocess-for-DC.py
│       ├── step1-train-for-DC.py
│       └── pretrainedmodel_weight_for_dc/     # Pretrained weights for DC
│
├── data/
│   ├── images/                                # Original image data
│   │   ├── images_DIC/                
│   │   ├── images_RFP/
│   │   ├── images_GFP/
│   ├── labels_DC/                             # DC class labels in YOLO format
│   ├── labels_SC/                             # SC class labels in YOLO format 
│   └── labels/                                # All class labels
│
├── run_pretrain_sc.sh                         # Run SC pretraining
├── run_pretrain_dc.sh                         # Run DC pretraining
├── run_sc.sh                                  # Run SC finetuning
├── run_dc.sh                                  # Run DC finetuning
└── README.md
```

* **src/pretrain**: Contains scripts for SC and DC pretraining.
  * `SC/`: Pretraining for SC (three-channel input)
  * `DC/`: Pretraining for DC (three-channel input)
* **src/SC**, **src/DC**: Contains scripts for SC and DC finetuning along with pretrained weights.
* **data**: Holds original images (images) and annotation files (labels_XXX).
* **run_pretrain_sc.sh**, **run_pretrain_dc.sh**: Shell scripts to run SC or DC pretraining.
* **run_sc.sh**, **run_dc.sh**: Shell scripts to run SC or DC finetuning.
