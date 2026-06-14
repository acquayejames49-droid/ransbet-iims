@echo off
REM Start ONLY the MySQL database (leave this window open while using the app).
title Ransbet MySQL
echo Starting MySQL on port 3306... (close this window to stop MySQL)
"C:\Users\USER\Desktop\Claude\mysql\mysql-8.0.40-winx64\bin\mysqld.exe" --basedir="C:\Users\USER\Desktop\Claude\mysql\mysql-8.0.40-winx64" --datadir="C:\Users\USER\Desktop\Claude\mysql\data" --port=3306 --console
pause
