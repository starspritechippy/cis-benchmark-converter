@echo off
set name=CIS Benchmark Converter
.\venv\Scripts\pyinstaller.exe --clean -F -i .\favicon.ico -n "%name%" .\main.py
DEL "%name%.spec"