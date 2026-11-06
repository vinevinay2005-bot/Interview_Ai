@echo off
title AI-Driven Virtual Interview and Skill Assessment Platform
echo =====================================================================
echo  AI-Driven Virtual Interview and Skill Assessment Platform
echo =====================================================================
echo Starting Streamlit Application...
echo.

if exist "%LOCALAPPDATA%\Python\bin\python.exe" (
    "%LOCALAPPDATA%\Python\bin\python.exe" -m streamlit run app.py --server.port 8501 --server.address 0.0.0.0
) else if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" -m streamlit run app.py --server.port 8501 --server.address 0.0.0.0
) else (
    py -m streamlit run app.py --server.port 8501 --server.address 0.0.0.0
)

pause
