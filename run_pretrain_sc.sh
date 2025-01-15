#!/usr/bin/env bash
echo "==========================================="
echo "Step 0: Preprocessing for SC..."
echo "==========================================="
python src/pretrain/SC/step0-preprocess-for-SC.py
if [ $? -ne 0 ]; then
  echo "Error: SC data preprocessing failed!"
  exit 1
fi

echo "==========================================="
echo "Step 1: Pretraining for SC..."
echo "==========================================="
python src/pretrain/SC/step1-pretrain-for-SC.py
if [ $? -ne 0 ]; then
  echo "Error: SC pretraining failed!"
  exit 1
fi

echo "==========================================="
echo "SC Pretraining Completed!"
echo "==========================================="