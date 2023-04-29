import logging
import os
import hashlib
import subprocess
import re
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def sha1sum(file_path):
    with open(file_path, 'rb') as f:
        file_hash = hashlib.sha1()
        while chunk := f.read(8192):
            file_hash.update(chunk)
    return file_hash.hexdigest()

# Get the current working directory
current_working_dir = Path.cwd()

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
                logging.error(f"Error processing file: {docx_path}")
                continue

            if media_dir.exists() and media_dir.is_dir():
                with open(md_path, 'r', encoding='utf-8') as md_file:
                    content = md_file.read()

                # Find all image links in the content using a regular expression with named capturing groups
                image_links = re.finditer(r'!\[\]\((?P<path>.*?)\)', content)

                for match in image_links:
                    old_media_path = match.group('path')
                    # Make the old media path relative to the current working directory
                    old_media_path_abs = current_working_dir / old_media_path.lstrip('./')

                    # Check if the old media file exists
                    if old_media_path_abs.exists():
                        # Calculate the SHA1 hash of the old media file
                        sha = sha1sum(old_media_path_abs)
                        # Determine the new media file name and path
                        new_media_file = media_dir / f'{sha}{old_media_path_abs.suffix}'
                        # Rename the old media file to the new media file
                        old_media_path_abs.rename(new_media_file)
                        # Create the desired new media path using the media_dir variable
                        new_relative_media_path = f"./media/{sha}{old_media_path_abs.suffix}"
                        # Replace the old media path with the new media path in the content
                        content = content.replace(old_media_path, new_relative_media_path)
                        # Log the replacement
                        logging.info(f"Replaced '{old_media_path}' with '{new_relative_media_path}'")

                with open(md_path, 'w', encoding='utf-8') as md_file:
                    md_file.write(content)

