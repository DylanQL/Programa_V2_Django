#!/usr/bin/env bash
# Salir si hay algún error
set -o errexit

# Instalar dependencias de Python
pip install -r requirements.txt

# Instalar Tesseract OCR en el servidor de Render
apt-get update && apt-get install -y tesseract-ocr tesseract-ocr-spa
