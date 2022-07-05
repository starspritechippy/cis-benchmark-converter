@echo off
venv\Scripts\pyinstaller.exe --clean -F -i .\favicon.ico -n "CIS Benchmark Converter" .\main.py
xcopy.exe '.\dist\CIS Benchmark Converter.exe' .\