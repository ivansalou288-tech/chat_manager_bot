#!/usr/bin/env python3
"""
Более агрессивное обновление всех ссылок на .md файлы в HTML
"""

import re
from pathlib import Path

def fix_all_md_links(html_file_path):
    """Заменяет все .md ссылки на .html"""
    
    with open(html_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Заменяем относительные ссылки на .md внутри HTML файлов
    # Например: href="DEVELOPERS_GUIDE_FARM.md" -> href="DEVELOPERS_GUIDE_FARM.html"
    content = re.sub(
        r'href="([^"]+)\.md"',
        r'href="\1.html"',
        content
    )
    
    # Также заменяем ссылки с ../for_developers/, ../docs/, ../ и т.д.
    # Нужно убедиться что они указывают на правильные HTML файлы в папке html/
    # Если ссылка начинается с ../, то меняем на ../html/
    content = re.sub(
        r'href="\.\./(for_developers|docs)/([^"]+)\.md"',
        r'href="../html/\2.html"',
        content
    )
    
    content = re.sub(
        r'href="\.\.\/([^"]+)\.md"',
        r'href="../html/\1.html"',
        content
    )
    
    if content != original_content:
        with open(html_file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    """Обновляет все .md ссылки во всех HTML файлах в папке html/"""
    
    html_dir = Path(r'd:\chat_manager_bot\html')
    
    # Получаем все HTML файлы
    html_files = list(html_dir.glob('*.html'))
    
    updated_count = 0
    for html_file in sorted(html_files):
        if fix_all_md_links(str(html_file)):
            print(f"Updated: {html_file.name}")
            updated_count += 1
        else:
            print(f"No changes: {html_file.name}")
    
    print(f"\nTotal updated: {updated_count} files")

if __name__ == '__main__':
    main()
