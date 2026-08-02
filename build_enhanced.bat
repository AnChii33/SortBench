@echo off
REM Enhanced Sorting Benchmark Tool - Build Script
REM This script builds the executable using PyInstaller

echo ==========================================
echo  Building Sorting Benchmark Tool (Enhanced)
echo ==========================================
echo.

REM Check if PyInstaller is installed
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: PyInstaller is not installed!
    echo Please install it with: pip install pyinstaller
    pause
    exit /b 1
)

echo Cleaning previous build artifacts...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.pyc" del /q "*.pyc"

echo.
echo Building executable with PyInstaller...
pyinstaller SORTER-GUI.spec

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    echo Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo  Build completed successfully!
echo ==========================================
echo.
echo Executable location: dist\SortingBenchmarkTool-Enhanced.exe
echo.
echo You can now run the application from the dist folder.
echo.

pause
