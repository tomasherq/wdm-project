#!/usr/bin/env bash

rm k8s/*.yaml
kompose convert -o k8s/ --volumes hostPath
python3 k8s/adapt_manifest.py