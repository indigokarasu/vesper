#!/bin/bash
# Wrapper to update ocas-vesper
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    echo "Usage: update.sh [--help]"
    echo "Update ocas-vesper from the upstream source."
    exit 0
fi
python3 ~/.hermes/scripts/skill_update.py ocas-vesper
