@echo off
cd /d "%~dp0app"
echo Néphro QCM Coach — http://localhost:8080
echo Ouvrir dans le navigateur (PC ou telephone sur le meme reseau).
py -3 -m http.server 8080
pause
