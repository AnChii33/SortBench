@echo off
echo ====================================
echo Building Sorting Benchmark Tool Installer
echo ====================================
echo.

REM Check if the executable exists
if not exist "dist\SortingBenchmarkTool.exe" (
    echo ERROR: SortingBenchmarkTool.exe not found in dist folder!
    echo Please run build.bat first to create the executable.
    pause
    exit /b 1
)

REM Create installer output directory
if not exist "installer_output" mkdir installer_output

echo Choose installer type:
echo 1. EXE Installer (using Inno Setup) - Recommended  
echo 2. MSI Installer (using WiX Toolset)
echo 3. EXE Installer (using NSIS) - Alternative
echo 4. All installers
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto inno_setup
if "%choice%"=="2" goto wix_setup  
if "%choice%"=="3" goto nsis_setup
if "%choice%"=="4" goto all_setup
echo Invalid choice!
pause
exit /b 1

:inno_setup
echo.
echo Building EXE Installer with Inno Setup...
echo ==========================================

REM Check if Inno Setup is installed
where iscc >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Inno Setup is not installed or not in PATH!
    echo.
    echo Please download and install Inno Setup from:
    echo https://jrsoftware.org/isinfo.php
    echo.
    echo After installation, make sure 'iscc.exe' is in your PATH
    echo or located at: C:\Program Files ^(x86^)\Inno Setup 6\iscc.exe
    pause
    exit /b 1
)

echo Compiling installer with Inno Setup...
iscc installer_setup.iss
if %errorlevel% equ 0 (
    echo.
    echo ✓ EXE Installer created successfully!
    echo Location: installer_output\SortingBenchmarkTool_Setup.exe
) else (
    echo.
    echo ✗ Error creating EXE installer!
)
goto end

:wix_setup
echo.
echo Building MSI Installer with WiX Toolset...
echo ==========================================

REM Check if WiX is installed
where candle >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: WiX Toolset is not installed or not in PATH!
    echo.
    echo Please download and install WiX Toolset from:
    echo https://wixtoolset.org/releases/
    echo.
    echo After installation, make sure WiX tools are in your PATH
    pause
    exit /b 1
)

echo Compiling WiX source...
candle installer_setup.wxs -o installer_output\installer_setup.wixobj
if %errorlevel% neq 0 (
    echo Error compiling WiX source!
    pause
    exit /b 1
)

echo Linking MSI installer...
light installer_output\installer_setup.wixobj -o installer_output\SortingBenchmarkTool.msi -ext WixUIExtension
if %errorlevel% equ 0 (
    echo.
    echo ✓ MSI Installer created successfully!
    echo Location: installer_output\SortingBenchmarkTool.msi
    
    REM Clean up temporary files
    del installer_output\installer_setup.wixobj 2>nul
    del installer_output\SortingBenchmarkTool.wixpdb 2>nul
) else (
    echo.
    echo ✗ Error creating MSI installer!
)
goto end

:nsis_setup
echo.
echo Building EXE Installer with NSIS...
echo ===================================

REM Check if NSIS is installed
where makensis >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: NSIS is not installed or not in PATH!
    echo.
    echo Please download and install NSIS from:
    echo https://nsis.sourceforge.io/Download
    echo.
    echo After installation, make sure 'makensis.exe' is in your PATH
    pause
    exit /b 1
)

echo Compiling installer with NSIS...
makensis installer_setup.nsi
if %errorlevel% equ 0 (
    echo.
    echo ✓ NSIS EXE Installer created successfully!
    echo Location: installer_output\SortingBenchmarkTool_Setup.exe
) else (
    echo.
    echo ✗ Error creating NSIS installer!
)
goto end

:all_setup
echo.
echo Building all installers...
echo =========================
call :inno_setup
call :wix_setup
call :nsis_setup
goto end

:end
echo.
echo ====================================
echo Build process completed!
echo ====================================
echo.
if exist "installer_output\SortingBenchmarkTool_Setup.exe" (
    echo EXE Installer: installer_output\SortingBenchmarkTool_Setup.exe
)
if exist "installer_output\SortingBenchmarkTool.msi" (
    echo MSI Installer: installer_output\SortingBenchmarkTool.msi
)
echo.
echo You can now distribute these installer files!
echo.
pause
