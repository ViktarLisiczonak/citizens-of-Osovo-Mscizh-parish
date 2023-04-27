import logging
import os
import hashlib
import subprocess
import re
from pathlib import Path

def sha1sum(file_path):
    with open(file_path, 'rb') as f:
        file_hash = hashlib.sha1()
        while chunk := f.read(8192):
            file_hash.update(chunk)
    return file_hash.hexdigest()

for root, _, files in os.walk('.'):
    for file in files:
        if file.endswith('.docx'):
            docx_path = Path(root) / file
            md_path = docx_path.with_suffix('.md')
            media_dir = Path(root) / 'media'
            
            try:
                # Convert docx to md
                subprocess.run(['pandoc', '-s', str(docx_path), '-t', 'markdown', '-o', str(md_path), '--track-changes=all', '--extract-media', str(root)], check=True)
            except subprocess.CalledProcessError:
                print(f"Error processing file: {docx_path}")
                continue

            if media_dir.exists() and media_dir.is_dir():
                with open(md_path, 'r', encoding='utf-8') as md_file:
                    content = md_file.read()

                for media_file in media_dir.glob('*'):
                    sha = sha1sum(media_file)
                    new_media_file = media_dir / f'{sha}{media_file.suffix}'
                    
                    # Extract the old media file name from the content using an improved regular expression
                    old_media_filename = re.search(r'(?<=!\[\]\()(.*?)(?=\))', content)

                    if old_media_filename:
                        old_media_path = old_media_filename.group()
                        # Print the old media path for debugging purposes

                        # Create the desired new media path using the media_dir variable
                        new_relative_media_path = f"./media/{sha}{media_file.suffix}"

                        # Replace the old media path with the new media path in the content
                        content = content.replace(old_media_path, new_relative_media_path)

                    media_file.rename(new_media_file)

                with open(md_path, 'w', encoding='utf-8') as md_file:
                    md_file.write(content)

