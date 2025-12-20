
import markdown
with open('docs/admin_guide.md', 'r', encoding='utf-8') as f:
    text = f.read()
    html = markdown.markdown(text)


with open('docs/admin_guide.html', 'w', encoding='utf-8') as f:
    f.write(html)