#!/bin/bash
./venv/bin/pyinstaller -clean -F -i ./favicon.ico -n "CIS Benchmark Converter" ./main.py
cp "./dist/CIS Benchmark Converter" ./