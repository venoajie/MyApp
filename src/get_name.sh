#!/bin/bash
for i in $(find $pwd -name "*.bak")
do 
  flnm=$(basename $i)
  extnm="${flnm##*.}"
  flnmnoext="${flnm%.*}"
  echo "FileName is : " $flnm " Extension is : " $extnm " File Name without extension is $flnmnoext"
done