@echo off
echo Building Sorting Benchmark Tool...
echo.

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt
pip install pyinstaller

echo.
echo Cleaning previous build...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

echo.
echo Building executable...
pyinstaller SORTER-GUI.spec

echo.
echo Build complete! Check the 'dist' folder for your executable.
echo.
pause
