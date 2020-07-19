#!/bin/bash

if [ $# -gt 0 ]; then
    rm $1
else
    return 1
fi