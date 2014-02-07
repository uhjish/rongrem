#!/bin/bash

for i in `seq 1 42`;
do
  echo $i
  sh curl.sh | grep -o -e 'lnkPopupReview\d\+' >> hotel_ids.txt
done
