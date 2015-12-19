#!/bin/bash


cd $1

rm -r dir1
t1=$(date +%s%N)


## creates directory
mkdir dir1
  
echo "MKDIR runtime: $(echo "scale=3;($(date +%s%N) - ${t1})/(1*10^03)" | bc) us"

t1=$(date +%s%N)

## prints run time for accessing dir1
cd dir1
  
echo "CD runtime: $(echo "scale=3;($(date +%s%N) - ${t1})/(1*10^03)" | bc) us"

t1=$(date +%s%N)

cd ..
  
echo "CD runtime: $(echo "scale=3;($(date +%s%N) - ${t1})/(1*10^03)" | bc) us"

cd ..

