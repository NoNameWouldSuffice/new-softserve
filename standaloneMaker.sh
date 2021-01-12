#!/bin/bash
echo "This is for linux only and is developmental. My way of saying I've just thrown this in here to make life easier for me without much thought for others"
echo "Please put in the version number for this version of standalone softserve (use hyphens '-' instead of dots '."
read versionNum
mkdir softserve-standalone-$versionNum
cp -r ./softserve/ ./softserve-standalone-$versionNum
cp -r ./deps ./softserve-standalone-$versionNum/softserve/
cd ./softserve-softserve-$versionNum
zip -r ../softserve-standalone-$versionNum ../softserve-standalone-$versionNum.zip *

