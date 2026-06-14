@echo off
REM ============================================================
REM  Ransbet IIMS - one-click launcher
REM  Starts the MySQL database, then the web app.
REM  Keep BOTH windows open while you use the system.
REM ============================================================
title Ransbet IIMS launcher

echo Starting MySQL database in a new window...
start "Ransbet MySQL (keep open)" "C:\Users\USER\Desktop\Claude\mysql\mysql-8.0.40-winx64\bin\mysqld.exe" --basedir="C:\Users\USER\Desktop\Claude\mysql\mysql-8.0.40-winx64" --datadir="C:\Users\USER\Desktop\Claude\mysql\data" --port=3306 --console

echo Waiting a few seconds for MySQL to be ready...
timeout /t 7 /nobreak >nul

echo Starting the Ransbet IIMS web app...
cd /d "C:\Users\USER\Desktop\Claude\ransbet-iims"
".venv\Scripts\python.exe" run.py

pause
