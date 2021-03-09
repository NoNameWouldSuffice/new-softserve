#!/bin/bash
echo "This is for linux only and is developmental. My way of saying I've just thrown this in here to make life easier for me without much thought for others"

python3 setup.py bdist_wheel
mv ./dist/* .
rm -rf dist
rm -rf softserve.egg-info
rm -rf build

echo "Pip distro complete"
echo "Please put in the version number for this version of standalone softserve (use hyphens '-' instead of dots '.)"
read versionNum

echo versionNum
mkdir softserve-standalone-$versionNum
cp -r ./softserve/ ./softserve-standalone-$versionNum
cp -r ./deps ./softserve-standalone-$versionNum/softserve/
#cd ./softserve-standalone-$versionNum
#zip -r ./softserve-standalone-$versionNum.zip . -i ./softserve-standalone-$versionNum/*

cd softserve-standalone-$versionNum
zip -r -q softserve-standalone-$versionNum.zip softserve
mv softserve-standalone-$versionNum.zip ../
cd ..
rm -rf ./softserve-standalone-$versionNum
echo "Standalone distro complete"
