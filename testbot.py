
import markdown
with open('docs/USER_GUIDE.md', 'r', encoding='utf-8') as f:
    text = f.read()
    html = markdown.markdown(text)


with open('docs/USER_GUIDE.html', 'w', encoding='utf-8') as f:
    f.write(html)