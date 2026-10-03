@echo off
cd /d "%~dp0.."
py -3 scripts\generate_bank.py
pause
