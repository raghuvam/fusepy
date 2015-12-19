#!/bin/bash

            
            
cd $1


# creates file1 file2

echo "Creating file1"  
echo "This is file1" > file1


echo "Creating file2"  
echo "This is file2" > file2

# prints file2 and file1 contents
t1=$(date +%s%N)
cat file2
  
echo "CAT file2 runtime: $(echo "scale=3;($(date +%s%N) - ${t1})/(1*10^03)" | bc) us"


t1=$(date +%s%N)
cat file1
  
echo "CAT file1 runtime: $(echo "scale=3;($(date +%s%N) - ${t1})/(1*10^03)" | bc) us"
