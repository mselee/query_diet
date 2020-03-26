#!/bin/bash
PYTHON_VERSIONS="cp36-cp36m cp37-cp37m cp38-cp38"

cd /io
/opt/python/cp37-cp37m/bin/pip install pip -U
/opt/python/cp37-cp37m/bin/pip install poetry -U --pre
/opt/python/cp37-cp37m/bin/poetry config virtualenvs.create false
/opt/python/cp37-cp37m/bin/poetry install --no-dev
cd -
