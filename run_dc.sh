#!/usr/bin/env bash
echo "==========================================="
echo "Step 0: Preprocessing for DC..."
echo "==========================================="
python src/DC/step0-preprocess-for-DC.py
if [ $? -ne 0 ]; then
  echo "Error: DC data preprocessing failed!"
  exit 1
fi

echo "==========================================="
echo "Step 1: Finetuning for DC..."
echo "==========================================="
python src/DC/step1-pretrain-for-DC.py
if [ $? -ne 0 ]; then
  echo "Error: DC finetuning failed!"
  exit 1
fi

echo "==========================================="
echo "DC Finetuning Completed!"
echo "==========================================="