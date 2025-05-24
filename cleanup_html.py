#!/usr/bin/env python3
"""
HTML Cleanup Script
Removes comments, fixes whitespace, and ensures proper formatting
"""

import os
import re
import glob

def clean_html_file(file_path):
    """Clean a single HTML file"""
    print(f"Cleaning {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
    
    lines = content.split('\n')
    cleaned_lines = []
    
    for i, line in enumerate(lines):
        if line.strip() == '':
            if i > 0 and i < len(lines) - 1:
                prev_line = lines[i-1].strip()
                next_line = lines[i+1].strip()
                
                if (prev_line.startswith('</') and next_line.startswith('<div') or
                    prev_line.startswith('</div>') and next_line.startswith('<div') or
                    prev_line.startswith('</nav>') or
                    prev_line.startswith('</header>') or
                    prev_line.startswith('</footer>') or
                    prev_line.startswith('</script>') and next_line.startswith('<')):
                    cleaned_lines.append('')
            continue
        
        cleaned_line = line.rstrip()
        cleaned_lines.append(cleaned_line)
    
    content = '\n'.join(cleaned_lines)
    
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    content = content.rstrip() + '\n'
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Cleaned {file_path}")

def main():
    """Clean all HTML files in the project"""
    
    html_files = []
    
    templates_files = glob.glob('templates/*.html')
    html_files.extend(templates_files)
    
    project_files = glob.glob('project_learn_track/*.html')
    html_files.extend(project_files)
    
    print(f"Found {len(html_files)} HTML files to clean:")
    for file in html_files:
        print(f"  - {file}")
    
    print("\nCleaning files...")
    for file_path in html_files:
        if os.path.exists(file_path):
            clean_html_file(file_path)
    
    print(f"\n✅ Successfully cleaned {len(html_files)} HTML files!")
    print("Fixed issues:")
    print("  - Removed all HTML comments")
    print("  - Removed trailing whitespace")
    print("  - Fixed empty lines and formatting")
    print("  - Ensured files end with newline")

if __name__ == "__main__":
    main() 