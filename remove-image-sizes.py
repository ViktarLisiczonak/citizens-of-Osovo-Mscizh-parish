import os
import re
from pathlib import Path

# Regular expression pattern to match the width and height attributes
attribute_pattern = r'{width="[\d\.]+[a-z]*"\s*height="[\d\.]+[a-z]*"}'

file_count = 0

for root, _, files in os.walk('.'):
    for file in files:
        if file.endswith('.md'):
            md_path = Path(root) / file

            with open(md_path, 'r', encoding='utf-8') as md_file:
                content = md_file.read()

            # Remove the width and height attributes from the content
            content = re.sub(attribute_pattern, '', content)

            with open(md_path, 'w', encoding='utf-8') as md_file:
                md_file.write(content)

            print(f"Processed: {md_path}")
            file_count += 1

print(f"Finished cleaning up width and height attributes in {file_count} .md files.")
