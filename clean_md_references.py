#!/usr/bin/env python3
"""
Полное очищение всех ссылок и текстов, связанных с .md файлами
"""

import re
from pathlib import Path

def clean_all_md_references(html_file_path):
    """Полностью очищает все ссылки и текст, связанные с .md"""
    
    with open(html_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 1. Заменяем href атрибуты - переводим .md на .html
    content = re.sub(
        r'href="([^"]+)\.md"',
        r'href="\1.html"',
        content
    )
    
    # 2. Заменяем относительные пути с ../for_developers и ../docs на ../html/
    content = re.sub(
        r'href="\.\./for_developers/([^"]+)\.html"',
        r'href="../html/\1.html"',
        content
    )
    content = re.sub(
        r'href="\.\./docs/([^"]+)\.html"',
        r'href="../html/\1.html"',
        content
    )
    
    # 3. Заменяем в тексте внутри ссылок:
    # <a href="...">DEVELOPERS_GUIDE_FARM.md</a> -> <a href="...">DEVELOPERS_GUIDE_FARM.html</a>
    content = re.sub(
        r'([^>]*)\.md</a>',
        r'\1.html</a>',
        content
    )
    
    # 4. Заменяем пути внутри текста: "for_developers/DEVELOPERS_GUIDE_FARM.md" -> "DEVELOPERS_GUIDE_FARM.html"
    content = re.sub(
        r'>for_developers/([^<]+)\.md',
        r'>\1.html',
        content
    )
    content = re.sub(
        r'>docs/([^<]+)\.md',
        r'>\1.html',
        content
    )
    content = re.sub(
        r'>\.\./([^<]+)\.md',
        r'>\1.html',
        content
    )
    
    # 5. Заменяем ../CODE_REFERENCE.md на ../html/CODE_REFERENCE.html и т.д.
    content = re.sub(
        r'>(\.\./)?([^<]+)\.md',
        r'>html/\2.html',
        content
    )
    
    if content != original_content:
        with open(html_file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    """Очищает все .md ссылки во всех HTML файлах"""
    
    html_dir = Path(r'd:\chat_manager_bot\html')
    
    # Получаем все HTML файлы
    html_files = list(html_dir.glob('*.html'))
    
    updated_count = 0
    for html_file in sorted(html_files):
        if clean_all_md_references(str(html_file)):
            print(f"Cleaned: {html_file.name}")
            updated_count += 1
        else:
            print(f"OK: {html_file.name}")
    
    print(f"\nTotal cleaned: {updated_count} files")

if __name__ == '__main__':
    main()
