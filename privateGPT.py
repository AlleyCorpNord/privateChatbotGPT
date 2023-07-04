#!/usr/bin/env python3
from st_pages import Page, show_pages
from pages import english

show_pages(
    [
        Page("pages/english.py", "Ask your questions in English"),
        Page("pages/french.py", "Posez vos questions en français"),
    ]
)

english.main()