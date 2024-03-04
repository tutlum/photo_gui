#!/bin/bash
path=$1
size=$2
targetfolder=$3
targetfile=$4
watermark=$5
target="$targetfolder/targetfile"
convert $path -resize ${size}x${size} -quality 89 "$target";
if [ -n "$watermark" ]; then
    convert "./$target" $watermark "$target"
fi
exiftool -overwrite_original -all= -tagsFromFile @ -Orientation -ICC_Profile -ColorSpace -DateTimeOriginal -Make -Model -ExposureTime -FNumber -ISOSpeedRatings -FocalLength -LensModel "$target";