@echo off
echo =========================================
echo DHL Label Cropper v3.0 ROBUST - BUILD
echo =========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python nicht gefunden!
    echo Bitte Python 3.8+ installieren
    pause
    exit /b 1
)

echo [1/4] Installiere Dependencies...
pip install --upgrade pip
pip install PyMuPDF==1.23.8
pip install pyinstaller==6.3.0

echo.
echo [2/4] Baue EXE...
pyinstaller --onefile --windowed ^
    --name="DHL_Label_Cropper_ROBUST" ^
    --icon=NONE ^
    --add-data="requirements.txt;." ^
    --hidden-import=fitz ^
    --hidden-import=tkinter ^
    --clean ^
    --noconfirm ^
    dhl_label_cropper_robust.py

echo.
echo [3/4] Räume auf...
if exist build rmdir /s /q build
if exist __pycache__ rmdir /s /q __pycache__
if exist *.spec del *.spec

echo.
echo [4/4] FERTIG!
echo =========================================
echo EXE liegt in: dist\DHL_Label_Cropper_ROBUST.exe
echo =========================================
echo.

:: Open dist folder
explorer dist

pause
