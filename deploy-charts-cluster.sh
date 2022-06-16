#!/usr/bin/env bash
kompose convert -o k8s/ --volumes hostPath
python3 k8s/adapt_manifest.py