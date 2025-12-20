#!/usr/bin/env python3
"""
Конвертирует markdown файлы в красивые HTML файлы
"""

import os
import re
import sys
from pathlib import Path
import markdown

# Установка кодировки для вывода в консоль
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def create_html_template(title, content):
    """Создает HTML шаблон с красивым стилем"""
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
            padding: 20px;
        }}

        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}

        header {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 40px;
            text-align: center;
        }}

        header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .breadcrumb {{
            background: #f8f9fa;
            padding: 15px 20px;
            border-bottom: 1px solid #ddd;
            font-size: 0.9em;
            color: #666;
        }}

        .breadcrumb a {{
            color: #667eea;
            text-decoration: none;
        }}

        .breadcrumb a:hover {{
            text-decoration: underline;
        }}

        .content {{
            padding: 40px;
        }}

        .content h1 {{
            color: #667eea;
            font-size: 2em;
            margin-bottom: 20px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}

        .content h2 {{
            color: #764ba2;
            font-size: 1.6em;
            margin-top: 30px;
            margin-bottom: 15px;
            border-left: 4px solid #667eea;
            padding-left: 15px;
        }}

        .content h3 {{
            color: #667eea;
            font-size: 1.3em;
            margin-top: 20px;
            margin-bottom: 10px;
        }}

        .content h4 {{
            color: #764ba2;
            font-size: 1.1em;
            margin-top: 15px;
            margin-bottom: 8px;
        }}

        .content p {{
            line-height: 1.8;
            margin: 15px 0;
            color: #444;
        }}

        .content ul, .content ol {{
            margin: 15px 0;
            margin-left: 30px;
            line-height: 1.8;
        }}

        .content li {{
            margin: 8px 0;
            color: #444;
        }}

        .content code {{
            background: #f8f9fa;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            color: #d63384;
            font-size: 0.95em;
        }}

        .content pre {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 15px 0;
            border-left: 4px solid #667eea;
        }}

        .content pre code {{
            color: #333;
            padding: 0;
            background: none;
            font-size: 0.9em;
        }}

        .content blockquote {{
            border-left: 4px solid #667eea;
            padding-left: 20px;
            margin: 20px 0;
            color: #666;
            font-style: italic;
        }}

        .content a {{
            color: #667eea;
            text-decoration: none;
            border-bottom: 1px solid transparent;
            transition: all 0.3s ease;
        }}

        .content a:hover {{
            border-bottom-color: #667eea;
        }}

        .content table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}

        .content table th {{
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
        }}

        .content table td {{
            border: 1px solid #ddd;
            padding: 12px;
        }}

        .content table tr:nth-child(even) {{
            background: #f8f9fa;
        }}

        .content hr {{
            border: none;
            border-top: 2px solid #667eea;
            margin: 30px 0;
        }}

        .content img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            margin: 20px 0;
        }}

        .nav-buttons {{
            display: flex;
            gap: 15px;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #ddd;
            justify-content: space-between;
        }}

        .nav-button {{
            display: inline-block;
            padding: 12px 24px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            transition: all 0.3s ease;
            font-weight: bold;
        }}

        .nav-button:hover {{
            background: #764ba2;
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }}

        .nav-button.prev {{
            margin-right: auto;
        }}

        footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            border-top: 1px solid #ddd;
            color: #666;
            font-size: 0.9em;
        }}

        footer a {{
            color: #667eea;
            text-decoration: none;
        }}

        footer a:hover {{
            text-decoration: underline;
        }}

        @media (max-width: 768px) {{
            header h1 {{
                font-size: 1.8em;
            }}

            .content {{
                padding: 20px;
            }}

            .nav-buttons {{
                flex-direction: column;
            }}

            .nav-button.prev {{
                margin-right: 0;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{title}</h1>
            <p style="opacity: 0.9; font-size: 1.1em;">Chat Manager Bot - Документация</p>
        </header>

        <div class="breadcrumb">
            <a href="../html/index.html">🏠 Главная</a> / 
            <a href="../html/index_site.html">📖 Документация</a> / 
            <span>{title}</span>
        </div>

        <div class="content">
            {content}
        </div>

        <div class="content">
            <div class="nav-buttons">
                <a href="../html/index_site.html" class="nav-button prev">← Вернуться к документации</a>
                <a href="../html/index.html" class="nav-button">На главную →</a>
            </div>
        </div>

        <footer>
            <p>Chat Manager Bot | Полная документация и структура проекта | Версия 2.0</p>
            <p style="margin-top: 10px;">
                <a href="../html/index.html">Главная</a> | 
                <a href="../html/index_site.html">Документация</a> | 
                <a href="../html/modules.html">Модули</a>
            </p>
        </footer>
    </div>
</body>
</html>
"""

def convert_markdown_to_html(md_file_path, html_output_dir):
    """Конвертирует один markdown файл в HTML"""
    
    # Читаем markdown файл
    with open(md_file_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Конвертируем markdown в HTML
    html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code', 'codehilite'])
    
    # Извлекаем заголовок из первого h1 или используем имя файла
    match = re.search(r'<h1[^>]*>([^<]+)</h1>', html_content)
    title = match.group(1) if match else Path(md_file_path).stem.replace('_', ' ').upper()
    
    # Удаляем первый h1, так как мы добавим его в header
    if match:
        html_content = re.sub(r'<h1[^>]*>[^<]+</h1>', '', html_content, count=1)
    
    # Создаем полный HTML
    full_html = create_html_template(title, html_content)
    
    # Определяем имя выходного файла
    output_filename = Path(md_file_path).stem + '.html'
    output_path = os.path.join(html_output_dir, output_filename)
    
    # Записываем HTML файл
    os.makedirs(html_output_dir, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    return output_path

def main():
    """Основная функция для конвертирования всех markdown файлов"""
    
    # Пути
    base_dir = Path(r'd:\chat_manager_bot')
    html_output_dir = base_dir / 'html'
    
    # Список markdown файлов для конвертирования
    md_files = [
        # Корневые файлы
        base_dir / 'CODE_REFERENCE.md',
        base_dir / 'README.md',
        
        # Из docs
        base_dir / 'docs' / 'USER_GUIDE.md',
        base_dir / 'docs' / 'BOOKMARKS_USER_SIMPLE.md',
        base_dir / 'docs' / 'admin_guide.md',
        
        # Из for_developers
        base_dir / 'for_developers' / 'START_HERE_DEVELOPERS.md',
        base_dir / 'for_developers' / 'DEVELOPERS_GUIDE_MAIN.md',
        base_dir / 'for_developers' / 'DEVELOPERS_GUIDE_INDEX.md',
        base_dir / 'for_developers' / 'DEVELOPERS_GUIDE_FARM.md',
        base_dir / 'for_developers' / 'DEVELOPERS_GUIDE_CUBES.md',
        base_dir / 'for_developers' / 'DEVELOPERS_GUIDE_KASIK.md',
        base_dir / 'for_developers' / 'DEVELOPERS_GUIDE_ROULETTES.md',
        base_dir / 'for_developers' / 'DEVELOPERS_GUIDE_HOTCOLD.md',
        base_dir / 'for_developers' / 'DEVELOPERS_GUIDE_MAFIA.md',
        base_dir / 'for_developers' / 'DEVELOPERS_GUIDE_TOURNAMENTS.md',
        base_dir / 'for_developers' / 'DEVELOPERS_GUIDE_UTILS.md',
        base_dir / 'for_developers' / 'BOOKMARKS_FOR_DEVELOPERS.md',
    ]
    
    # Конвертируем каждый файл
    converted_files = {}
    for md_file in md_files:
        if md_file.exists():
            try:
                html_path = convert_markdown_to_html(str(md_file), str(html_output_dir))
                # Сохраняем соответствие исходного пути и HTML файла
                converted_files[str(md_file)] = html_path
                print(f"OK: {Path(md_file).name}")
            except Exception as e:
                print(f"ERROR {Path(md_file).name}: {e}")
        else:
            print(f"NOTFOUND: {Path(md_file).name}")
    
    print(f"\nSuccess: {len(converted_files)} files converted")
    print("\nFile mapping:")
    for md_path, html_path in converted_files.items():
        print(f"  {Path(md_path).name} -> {Path(html_path).name}")
    
    return converted_files

if __name__ == '__main__':
    main()
