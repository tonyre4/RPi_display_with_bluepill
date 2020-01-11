rd /S /Q output 
rd /S /Q input
mkdir input

copy ..\app.py input\
Rem python Intensio-Obfuscator\intensio\intensio_obfuscator.py --input input --output output -rth
mkdir output

copy input\app.py output\
copy AdChargerUploader.py output\
cd output

pyinstaller AdChargerUploader.py app.py
del AdChargerUploader.py app.py
cd..
output\dist\AdChargerUploader\AdChargerUploader.exe