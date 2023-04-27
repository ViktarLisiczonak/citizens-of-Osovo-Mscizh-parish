#!/bin/bash

sha1sum() {
  openssl sha1 "$1" | awk '{print $2}'
}

find . -name "*.docx" -print0 | while IFS= read -r -d '' file; do
    filename=$(basename "$file")
    extension="${filename##*.}"
    basename="${filename%.*}"
    output_dir=$(dirname "$file")
    pandoc -s "$file" -t markdown -o "$output_dir/$basename.md" --track-changes=all --extract-media="$output_dir"
    media_dir="$output_dir/media"
    if [ -d "$media_dir" ]; then
        for media_file in "$media_dir/"*; do
            sha=$(sha1sum "$media_file")
            media_filename=$(basename "$media_file")
            media_extension="${media_filename##*.}"
            mv "$media_file" "$media_dir/$sha.$media_extension"
            sed -i "s/$media_filename/$sha.$media_extension/g" "$output_dir/$basename.md"
        done
    fi
done
