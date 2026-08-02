@echo off
echo ====================================
echo Testing Sorting Benchmark Tool
echo ====================================
echo.

REM Check if the executable exists
if not exist "dist\SortingBenchmarkTool.exe" (
    echo ERROR: SortingBenchmarkTool.exe not found in dist folder!
    echo Please run build.bat first to create the executable.
    pause
    exit /b 1
)

echo Testing executable portability...
echo.

REM Create a test directory in a different location
set test_dir=%TEMP%\SortingBenchmarkTool_Test
if exist "%test_dir%" rmdir /s /q "%test_dir%"
mkdir "%test_dir%"

echo Copying executable to test directory: %test_dir%
copy "dist\SortingBenchmarkTool.exe" "%test_dir%\"

echo.
echo ====================================
echo PORTABLE TEST
echo ====================================
echo.
echo The executable has been copied to:
echo %test_dir%\SortingBenchmarkTool.exe
echo.
echo This test will verify that the exe works independently
echo without needing the original source files.
echo.
echo 1. The application should start without errors
echo 2. All sorting algorithms should be available
echo 3. All default datasets should be accessible
echo 4. Benchmarking should work properly
echo.
pause

echo Starting portable test...
cd /d "%test_dir%"
start SortingBenchmarkTool.exe

echo.
echo ====================================
echo Test launched!
echo ====================================
echo.
echo Please verify the following:
echo ✓ Application starts without errors
echo ✓ All sorting algorithms are listed in the left panel
echo ✓ All datasets are listed in the right panel  
echo ✓ You can run a quick benchmark test
echo.
echo If everything works correctly, the executable is properly portable!
echo.
echo Test directory: %test_dir%
echo You can delete this directory after testing.
echo.
pause
