.PHONY: docs

docs:
	find docs -name "*.html" -delete
	echo "notes.eatonphil.com" > docs/CNAME
	python3 -m venv .env
	.env/bin/pip install mistune==0.8.4 feedgen pygments==2.15.1
	.env/bin/python ./scripts/build.py
	.env/bin/python -c "from pygments.formatters import HtmlFormatter; print(HtmlFormatter().get_style_defs('.highlight'))" > out.css
	cat out.css | cat - docs/style.css > combined.css && mv combined.css docs/style.css
	rm out.css
