import sys

import markdown
from bs4 import BeautifulSoup

def convert_md_to_email_html(text):
    raw_html = markdown.markdown(text)
    
    soup = BeautifulSoup(raw_html, 'html.parser')
    
    for p in soup.find_all('p'):
        p['style'] = "margin-bottom: 10px;"
        
    for a in soup.find_all('a'):
        a['clicktracking'] = "off"
        
    return str(soup)

md_input = sys.stdin.read().strip()
print(convert_md_to_email_html(md_input))
