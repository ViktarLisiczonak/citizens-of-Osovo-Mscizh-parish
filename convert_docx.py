import os
import hashlib
import subprocess
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
                for media_file in media_dir.glob('*'):
                    sha = sha1sum(media_file)
                    new_media_file = media_dir / f'{sha}{media_file.suffix}'
                    media_file.rename(new_media_file)

                    with open(md_path, 'r', encoding='utf-8') as md_file:
                        content = md_file.read()

                    content = content.replace(str(media_file.name), str(new_media_file.name))

                    with open(md_path, 'w', encoding='utf-8') as md_file:
                        md_file.write(content)

