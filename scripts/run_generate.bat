@echo off
cd /d "%~dp0.."
echo Banque DEMS (cours uniquement)...
py -3 scripts\build_dems_bank.py
pause
