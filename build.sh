#!/bin/bash
name="CIS-Benchmark-Converter"
./venv/bin/pyinstaller --clean -F -i ./favicon.ico -n "$name" ./main.py
cp "./dist/$name" ./
rm "$name.spec"