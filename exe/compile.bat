rm AdChargerUploader -r
copy ..\app.py input\
python C:\Users\Tonny\Documents\VBshare\RPi_display_with_bluepill\exe\Intensio-Obfuscator\intensio\intensio_obfuscator.py --input input --output AdChargerUploader -rth
copy AdChargerUploader.py AdChargerUploader\
cd AdChargerUploader
pyinstaller AdChargerUploader.py app.py --windowed
rm AdChargerUploader.py app.py
cd..
C:\Users\Tonny\Documents\VBshare\RPi_display_with_bluepill\exe\AdChargerUploader\dist\AdChargerUploader\AdChargerUploader.exe