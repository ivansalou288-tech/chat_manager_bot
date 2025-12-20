#!/usr/bin/env python3
"""
Обновляет все ссылки на markdown файлы в HTML на HTML файлы
"""

import re
import os
from pathlib import Path

def update_links_in_html_file(html_file_path):
    """Обновляет ссылки на markdown файлы в HTML файле"""
    
    with open(html_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Словарь соответствия markdown файлов HTML файлам
    # Меняем .md на .html
    replacements = [
        # Абсолютные пути к файлам
        (r'href="\.\./(CODE_REFERENCE)\.md"', r'href="../html/\1.html"'),
        (r'href="\.\./(README)\.md"', r'href="../html/\1.html"'),
        (r'href="\.\./docs/(USER_GUIDE)\.md"', r'href="../html/\1.html"'),
        (r'href="\.\./docs/(BOOKMARKS_USER_SIMPLE)\.md"', r'href="../html/\1.html"'),
        (r'href="\.\./docs/(admin_guide)\.md"', r'href="../html/\1.html"'),
        (r'href="\.\./for_developers/(START_HERE_DEVELOPERS)\.md"', r'href="../html/\1.html"'),
        (r'href="\.\./for_developers/(DEVELOPERS_GUIDE_MAIN)\.md"', r'href="../html/\1.html"'),
        (r'href="\.\./for_developers/(DEVELOPERS_GUIDE_INDEX)\.md"', r'href="../html/\1.html"'),
        (r'href="\.\./for_developers/(DEVELOPERS_GUIDE_FARM)\.md"', r'href="../html/\1.html"'),
        (r'href="\.\./for_developers/(DEVELOPERS_GUIDE_CUBES)\.md"', r'href="../html/\1.html"'),
        (r'href="\.\./for_developers/(DEVELOPERS_GUIDE_KASIK)\.md"', r'href="../html/\1.html"'),
        (r'href="\.\./for_developers/(DEVELOPERS_GUIDE_ROULETTES)\.md"', r'href="../html/\1.html"'),
        (r'href="\.\./for_developers/(DEVELOPERS_GUIDE_HOTCOLD)\.md"', r'href="../html/\1.html"'),
        (r'href="\.\./for_developers/(DEVELOPERS_GUIDE_MAFIA)\.md"', r'href="../html/\1.html"'),
        (r'href="\.\./for_developers/(DEVELOPERS_GUIDE_TOURNAMENTS)\.md"', r'href="../html/\1.html"'),
        (r'href="\.\./for_developers/(DEVELOPERS_GUIDE_UTILS)\.md"', r'href="../html/\1.html"'),
        (r'href="\.\./for_developers/(BOOKMARKS_FOR_DEVELOPERS)\.md"', r'href="../html/\1.html"'),
    ]
    
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    # Также обновляем простые .md ссылки
    content = re.sub(r'href="([^"]+)\.md"', lambda m: f'href="{m.group(1)}.html"', content)
    
    # Если что-то изменилось, записываем файл
    if content != original_content:
        with open(html_file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    """Обновляет ссылки во всех HTML файлах"""
    
    html_dir = Path(r'd:\chat_manager_bot\html')
    
    # Список HTML файлов для обновления
    html_files = [
        html_dir / 'index.html',
        html_dir / 'index_site.html',
        html_dir / 'modules.html',
        html_dir / 'documentation.html',
    ]
    
    # Обновляем ссылки в каждом HTML файле
    updated_count = 0
    for html_file in html_files:
        if html_file.exists():
            if update_links_in_html_file(str(html_file)):
                print(f"Updated: {html_file.name}")
                updated_count += 1
            else:
                print(f"No changes: {html_file.name}")
        else:
            print(f"Not found: {html_file.name}")
    
    print(f"\nTotal updated: {updated_count} files")

if __name__ == '__main__':
    main()
