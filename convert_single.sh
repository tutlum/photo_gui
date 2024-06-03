#!/bin/bash
path=$1
size=$2
targetfolder=$3
targetfile=$4
#crop='-crop +200 +repage -crop -200'
os="$(($size / 200))"
if [ -n "$5" ]; then
    watermark="$5 -geometry +$os+$os -gravity southwest -composite"
fi
target="$targetfolder/$targetfile"
if [ -n "$crop" ]; then
    convert "$path" $crop "$target"
    convert "$target" -resize ${size}x${size} -quality 89 "$target";
else
    convert "$path" -resize ${size}x${size} -quality 89 "$target";
fi
if [ -n "$watermark" ]; then
    convert "$target" $watermark "$target"
fi
exiftool -overwrite_original -all= -tagsFromFile @ -Orientation -ICC_Profile -ColorSpace -DateTimeOriginal -Make -Model -ExposureTime -FNumber -ISOSpeedRatings -FocalLength -LensModel "$target";