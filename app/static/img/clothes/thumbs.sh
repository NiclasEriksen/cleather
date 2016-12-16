#! /bin/bash

for i in *.png; do
    if [ "$i" -nt "./thumbs/$i" ]; then
        convert "$i" -thumbnail 32 "./thumbs/$i";
    fi
done;
