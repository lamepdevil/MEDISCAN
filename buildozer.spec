[app]
title = MediScan
package.name = mediscan
package.domain = org.mediscan
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 1.0.0
orientation = portrait
fullscreen = 1

# Permissions
android.permissions = INTERNET,READ_MEDIA_IMAGES,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE

# Minimum and target Android API
android.minapi = 21
android.api = 33
android.ndk = 25b

# Architecture for most Android devices
android.archs = armeabi-v7a

# Include this only if you're using legacy support
android.gradle_dependencies = com.android.support:appcompat-v7:28.0.0

# Include OCR/data/image libraries
requirements = python3,kivy,requests,pytesseract,Pillow,matplotlib,opencv-python-headless

# Optional icons
icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/presplash.png

# Include Tesseract training data (if used)
# android.add_src = assets/tessdata
# Use custom asset path if needed
# (Make sure to copy traineddata files there and reference in your app)

# Entry point (main app file)
entrypoint = main.py

# Copy data
android.add_assets_
