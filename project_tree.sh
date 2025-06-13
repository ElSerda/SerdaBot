#!/bin/bash

echo "📂 Structure actuelle de ton projet :"

find . \
  -type f \
  ! -path "./.git/*" \
  ! -path "./venv/*" \
  ! -path "./.venv/*" \
  ! -path "*/__pycache__/*" \
  ! -path "*/.pytest_cache/*" \
  ! -path "*/.mypy_cache/*" \
  ! -name "*.pyc" \
  -exec du -h {} + | sort -h
