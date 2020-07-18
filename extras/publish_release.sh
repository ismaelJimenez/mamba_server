#!/bin/bash

cd ..
twine check dist/*
twine upload dist/*
