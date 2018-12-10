#! /bin/bash

for file in ./dump_files/*; do
		../mediawiki_dump_tools/wikiq "$file" -o ./tsv_files/
done
