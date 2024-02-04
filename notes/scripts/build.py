import glob
import os
import shutil
from datetime import datetime, timezone

import mistune
from feedgen.feed import FeedGenerator
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import guess_lexer, get_lexer_by_name

STATIC = [
    'style.css',
]

POST_SUMMARY = """
<div class="summary">
  <div class="summary-subtitle">{}</div>
  <a href="/{}">{}</a>
  {}
</div>
"""
TAG_SUMMARY = """
<div class="summary">
  <a href="/{}">{}</a>
  <div class="summary-subtitle">{}</div>
</div>
"""
TAG_PAGE = """
<div class="summary">
  <h1>{}</h1>
  <div class="summary-subtitle">Tag</div>
</div>
"""
HOME_PAGE = """
<div class="fp-section fp-section--tags">
  <h2 class="fp-h2">Frequent</h2>
  <div class="tags">
    {tags}
  </div>
  <small><a href="/tags/">View all</a></small>
</div>

<div class="fp-section fp-section--notes">
  {notes}
</div>
"""
MAIL = open("mail.html").read()
TEMPLATE = open('template.html').read()
TAG = "Notes on software development"

class Renderer(mistune.Renderer):
    def __init__(self):
        mistune.Renderer.__init__(self)
        self.title = {}

    def header(self, text, level, *args, **kwargs):
        if level not in self.title:
            self.title[level] = text
            return ""
        if level == 6:
            return ""
        return "<h{level} id=\"{id}\">{text}</h{level}>".format(**{
            "id": text.lower().replace(' ', '-'),
            "text": text,
            "level": level,
        })

    def block_code(self, code, lang=""):
        code = code.rstrip('\n')
        if lang == "assembly":
            lang = "nasm"
        l = get_lexer_by_name(lang) if lang else guess_lexer(code)
        return highlight(code, l, HtmlFormatter())


def get_posts():
    for post in glob.glob('posts/**'):
        if post.endswith('.html'):
            yield post


def get_post_data(in_file):
    with open(in_file) as f:
        markdown = mistune.Markdown(renderer=Renderer())
        output = markdown(f.read())
        return output, markdown.renderer.title


def get_html_tags(all_tags):
    tags = ''

    for i, tag in enumerate(all_tags):
        if not tag:
            continue
        #if i < 3:
        tags += '<a href="/tags/{}.html" class="tag">{}</a>'.format(tag.replace(' ', '-').replace('/', '-'), tag)
        #else:
        #    tags += '<span style="display: none;">{}</span>'.format(tag)
    if tags:
        return '<div class="tags">{}</div>'.format(tags)

    return ''


showfeedback = "<style>.feedback{display:initial;}</style>"

def main():
    all_tags = {}
    post_data = []
    tags_with_counts = {}
    for post in get_posts():
        print('Processing ' + post)
        out_file = post[len('posts/'):]
        output, title = get_post_data(post)
        try:
            header, real_subtitle, date, tags_raw = title[1], title.get(3, ""), title[2], title.get(6, "")
        except:
            t = out_file.split('.')[0].title()
            with open('docs/' + out_file, 'w') as f:
                f.write(TEMPLATE.format(post=output, meta="", tag=t, subtitle="", real_subtitle="", title="", tags="", frequent_tags="", full_url="https://notes.eatonphil.com/"+out_file, mail=MAIL, hide_on_index=""))
            continue

        tags = tags_raw.split(",")
        tags_html = get_html_tags(tags)
        # Ignore drafts for all but the page itself.
        if "draft" in tags:
            t = out_file.split('.')[0].title()
            with open('docs/' + out_file, 'w') as f:
                f.write(TEMPLATE.format(post=output, meta="", tag=header, subtitle=date, real_subtitle=real_subtitle, title=header, tags=tags, frequent_tags=tags_html, full_url="https://notes.eatonphil.com/"+out_file, mail=MAIL, hide_on_index=""))
            continue

        if real_subtitle != "":
            real_subtitle = f"<div class='realsubtitle'>{real_subtitle}</div>"
        post_data.append((out_file, title[1], title[2], post, output, tags_html, real_subtitle))
        for tag in tags:
            if tag not in all_tags:
                all_tags[tag] = []
            if tag not in tags_with_counts:
                tags_with_counts[tag] = 0
            tags_with_counts[tag] += 1

            all_tags[tag].append((out_file, title[1], title[2]))

    frequent_tags_data = sorted(tags_with_counts.items(), key=lambda x: (x[1], x[0]), reverse=True)
    frequent_tags = []
    for tag, count in [t for t in frequent_tags_data if t[0] != 'external'][:20]:
        if tag == "draft":
            continue
        frequent_tags.append(f'<a href="/tags/{tag.replace(" ", "-").replace("/", "-")}.html" class="tag">{tag} ({count})</a>')
    frequent_tags = "".join(frequent_tags)

    for (out_file, title, date, _, output, tags_html, real_subtitle) in post_data:
        with open('docs/' + out_file, 'w') as f:
            f.write(TEMPLATE.format(post=output+showfeedback, title=title, subtitle=date, tag=title, tags=tags_html, meta="", frequent_tags=frequent_tags, full_url="https://notes.eatonphil.com/"+out_file, mail=MAIL, hide_on_index="", real_subtitle=real_subtitle))

    post_data.sort(key=lambda post: datetime.strptime(post[2], '%B %d, %Y'))
    post_data.reverse()
    notes = []
    for i, args in enumerate(post_data):
        year = args[2].split(' ')[-1]
        prev_post_year = str(datetime.today().year + 1) if i == 0 else post_data[i-1][2].split(' ')[-1]
        if year != prev_post_year:
            notes.append('<h3>{}</h3>'.format(year))
        note = POST_SUMMARY.format(*args[2:3], *args[:2], args[5])
        notes.append(note)

    home_page = HOME_PAGE.format(
        notes="\n".join(notes),
        tags=frequent_tags)
    with open('docs/index.html', 'w') as f:
        meta = '<meta name="google-site-verification" content="s-Odt0Dj7WZzEk6hLV28wLyR5LeGQFoopUV3IDNO6bM" />\n    '
        f.write(TEMPLATE.format(post=home_page, title="", tag=TAG, subtitle="", tags="", meta=meta, frequent_tags="", full_url="https://notes.eatonphil.com", mail=MAIL, hide_on_index="hide-on-index", real_subtitle=""))

    for f in STATIC:
        shutil.copy(f, os.path.join('docs', f))

        if f == "style.css":
            for other_folder in ['lists', 'letters', 'home']:
                shutil.copy(f, os.path.join('../', other_folder, 'style.css'))

    fg = FeedGenerator()
    for url, title, date, post, content, _, _ in reversed(post_data):
        fe = fg.add_entry()
        fe.id('http://notes.eatonphil.com/' + url)
        fe.title(title)
        fe.link(href='http://notes.eatonphil.com/' + url)
        fe.pubDate(datetime.strptime(date, '%B %d, %Y').replace(tzinfo=timezone.utc))
        fe.content(content)

    fg.id('http://notes.eatonphil.com/')
    fg.link(href='http://notes.eatonphil.com/')
    fg.title(TAG)
    fg.description(TAG)
    fg.author(name='Phil Eaton', email='me@eatonphil.com')
    fg.language('en')
    fg.rss_file('docs/rss.xml')

    with open('docs/sitemap.xml', 'w') as f:
        urls = []
        for url, _, date, _, _, _, _ in reversed(post_data):
            urls.append("""  <url>
    <loc>https://notes.eatonphil.com/{url}</loc>
    <lastmod>{date}</lastmod>
 </url>""".format(url=url, date=datetime.strptime(date, '%B %d, %Y').strftime('%Y-%m-%d')))
        f.write("""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}
</urlset>""".format(urls='\n'.join(urls)))

    with open('docs/robots.txt', 'w') as f:
        f.write("""User-agent: *
Allow: /

Sitemap: https://notes.eatonphil.com/sitemap.xml""")

    if not os.path.exists('docs/tags'):
        os.makedirs('docs/tags')
    # Write tag index
    tag_index_data = sorted(tags_with_counts.items(), key=lambda x: x[1], reverse=True)
    tag_index = []
    for tag, count in tag_index_data:
        if tag == "draft":
            continue
        tag_index.append(f'<a href="/tags/{tag.replace(" ", "-").replace("/", "-")}.html" class="tag {"tag--common" if i < 20 else ""}">{tag} ({count})</a>')
    with open('docs/tags/index.html', 'w') as f:
        index_page = f'<div class="tags">{"".join(tag_index)}</div>'
        f.write(TEMPLATE.format(post=index_page, title="All Topics", tag="All Topics", subtitle="", tags="", meta="", frequent_tags="", full_url="https://notes.eatonphil.com/tags/", mail=MAIL, hide_on_index='hide-on-index', real_subtitle=""))

    # Write each individual tag page
    for tag in all_tags:
        if tag == "draft":
            continue
        posts = all_tags[tag]
        file_name = '%s.html' % tag.replace(' ', '-').replace('/', '-')
        with open('docs/tags/'+file_name, 'w') as f:
            posts.sort(key=lambda post: datetime.strptime(post[2], '%B %d, %Y'))
            posts.reverse()
            tag_page = TAG_PAGE.format(tag)
            tag_page += "\n".join([TAG_SUMMARY.format(*args) for args in posts])
            f.write(TEMPLATE.format(post=tag_page, title="", tag=TAG, subtitle="", tags="", meta="", frequent_tags="", full_url="https://notes.eatonphil.com/tags/"+file_name, mail=MAIL, hide_on_index="", real_subtitle=""))


if __name__ == '__main__':
    main()
