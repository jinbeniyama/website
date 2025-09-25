#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
from pybtex.database import parse_file
import re

# Journal mapping
JOURNAL_MAP = {
    r"\pasj": "Publications of the Astronomical Society of Japan",
    r"\nat": "Nature",
    r"\icarus": "Icarus",
    r"\aj": "Astronomical Journal",
    r"\apj": "Astrophysical Journal",
    r"\apjl": "ApJL",
    r"\apjs": "ApJS",
    r"\pasp": "PASP",
    r"\mnras": "MNRAS",
    r"\aap": "A&A",
    r"\grl": "GRL",
    r"\psj": "PSJ",
    r"\araa": "ARAA",
    r"\gca": "GCA",
    r"\aap": "Astronomy & Astrophysics",
}

LATEX_ACCENTS = {
    r"\"a": "ä", r"\"o": "ö", r"\"u": "ü",
    r"\"A": "Ä", r"\"O": "Ö", r"\"U": "Ü",
    r"\'a": "á", r"\'e": "é", r"\'i": "í", r"\'o": "ó", r"\'u": "ú",
    r"\`a": "à", r"\`e": "è", r"\`i": "ì", r"\`o": "ò", r"\`u": "ù",
    r"\~n": "ñ", r"\ss": "ß",
    r"\^a": "â", r"\^e": "ê", r"\^i": "î", r"\^o": "ô", r"\^u": "û",
}


def latex_to_unicode(text):
    for latex_seq, char in LATEX_ACCENTS.items():
        text = text.replace(latex_seq, char)
    return text.replace("{", "").replace("}", "")


def normalize_journal(journal):
    journal = journal.strip()
    return JOURNAL_MAP.get(journal, journal)


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
  <head>
    <!-- Global site tag (gtag.js) - Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=UA-143048532-1"></script>
    <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'UA-143048532-1');
    </script> 
    <meta charset="utf-8">
    <link rel="icon" type="image/x-icon" href="fig/favicon.ico">
    <link rel="stylesheet" href="common/css/beni.css">
    <title>Publications</title>
    <style>
      table.pub-list {{
        border-collapse: collapse;
        width: 100%;
      }}
      table.pub-list th, table.pub-list td {{
        border: 1px solid #ddd;
        padding: 8px;
        vertical-align: top;
      }}
      table.pub-list th {{
        background-color: #f2f2f2;
        text-align: left;
      }}
      .authors {{
        white-space: pre-line;
      }}
    </style>
  </head>
  <body>
    <div id="page">
{tables}

      <h1>Links</h1>
      <hr>
      <ul>
        <li><a href="index.html">Back to home</a></li>
      </ul>

      <footer id="pageFoot">
        <p id="copyright"><small>Copyright &copy; Jin BENIYAMA</small></p>
      </footer>
    </div>
  </body>
</html>
"""

def bib_to_table_rows(bib_files, first_author_table=True):
    """Convert BibTeX entries to HTML table rows.

    Parameters
    ----------
    bib_files : list of str
        BibTeX file paths.
    first_author_table : bool
        If True, bold first author and truncate to 3 + et al. 
        If False (Nth author), show all authors, no bold.
    """
    all_entries = []

    for bib_path in bib_files:
        bib_data = parse_file(bib_path)
        for entry in bib_data.entries.values():
            year_str = entry.fields.get("year", "9999")
            try:
                year_int = int(year_str)
            except ValueError:
                year_int = 9999
            all_entries.append((year_int, entry))

    all_entries.sort(key=lambda x: x[0])
    rows = []

    for i, (year, entry) in enumerate(all_entries, start=1):
        authors_list = [latex_to_unicode(str(person)) for person in entry.persons.get("author", [])]

        if first_author_table and authors_list:
            authors_list[0] = f"<b>{authors_list[0]}</b>"
            if len(authors_list) > 3:
                authors_html = ", ".join(authors_list[:3]) + ", et al."
            else:
                authors_html = ", ".join(authors_list) if authors_list else "Unknown"
        else:
            # Nth author table: show all authors, no bold
            authors_html = ", ".join(authors_list) if authors_list else "Unknown"

        # Title + link
        title = latex_to_unicode(entry.fields.get("title", "No title"))
        doi = entry.fields.get("doi", "")
        url = f"https://doi.org/{doi}" if doi else entry.fields.get("url", "#")
        title_html = f'<a href="{url}" target="_blank">{title}</a>'

        # Journal info
        raw_journal = entry.fields.get("journal", "")
        journal = normalize_journal(raw_journal)
        volume = entry.fields.get("volume", "")
        pages = entry.fields.get("pages", "")
        journal_info = ", ".join(filter(None, [journal, volume, pages, str(year)]))

        row_html = f"""        <tr>
          <td>{i}</td>
          <td class='authors'>{authors_html}</td>
          <td>{title_html}</td>
          <td>{journal_info}</td>
        </tr>"""
        rows.append(row_html)
    return rows


def generate_table(title, bib_files, first_author_table=True):
    if not bib_files:
        return ""
    rows = bib_to_table_rows(bib_files, first_author_table=first_author_table)
    table_html = f"""      <h1>{title}</h1>
      <hr>
      <table class="pub-list">
        <tr>
          <th>#</th>
          <th>Authors</th>
          <th>Title</th>
          <th>Journal / Year</th>
        </tr>
{chr(10).join(rows)}
      </table>
"""
    return table_html


def main():
    parser = argparse.ArgumentParser(
        description="Generate HTML publication table from BibTeX files.")
    parser.add_argument(
        "output_html", 
        help="Path to save the generated HTML file")
    parser.add_argument(
        "--first", nargs='+', 
        help="BibTeX files for first-author publications")
    parser.add_argument(
        "--Nth", nargs='+', 
        help="BibTeX files for N-th author publications")
    args = parser.parse_args()

    tables = ""
    if args.first:
        tables += generate_table(
            "Refereed Articles (First author)", args.first, 
            first_author_table=True)
    if args.Nth:
        tables += generate_table(
            "Refereed Articles (Nth author)", args.Nth, 
            first_author_table=False)
    
    html_content = HTML_TEMPLATE.format(tables=tables)

    with open(args.output_html, "w", encoding="utf-8") as f:
        f.write(html_content)

    total_entries = (len(args.first) if args.first else 0) + (len(args.Nth) if args.Nth else 0)
    print(f"Generated HTML file: {args.output_html}")

if __name__ == "__main__":
    main()

