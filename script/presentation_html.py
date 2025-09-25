#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate presentation HTML tables from text files.

Format of text file:
Presenters: names
Title: xxx
Event: xxx
Location: xxx
Dates: 1996-05-18; 2025-04-19
Type: Oral / Poster 
Memo: / Invited / Award / Other>
URL: <リンク>
"""
import argparse
import datetime
import matplotlib.pyplot as plt
from collections import Counter
import re


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <link rel="icon" type="image/x-icon" href="fig/favicon.ico">
    <link rel="stylesheet" href="common/css/beni.css">
    <title>Presentations</title>
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
  These are list of my presentations. Last updated on {last_update} 
  <img src="{fig_file}" alt="Presentations per Year" style="max-width:100%;height:auto;">

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

def parse_txt_file(txt_file):
    """Parse the presentation text file into a list of dicts."""
    entries = []
    current = {}
    with open(txt_file, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                if current:
                    entries.append(current)
                    current = {}
                continue
            if ':' not in line:
                continue
            key, val = line.split(':', 1)
            current[key.strip()] = val.strip()
    if current:
        entries.append(current)
    return entries

def make_table_html(entries, title):
    """Generate HTML table from entries."""
    rows = []
    for i, e in enumerate(entries, start=1):
        presenters = e.get('Presenters', 'Unknown')
        title_val = e.get('Title', 'No title')
        event = e.get('Event', '')
        location = e.get('Location', '')
        dates = e.get('Dates', '')
        type_val = e.get('Type', '')
        url = e.get('URL', '').strip()
        memo = e.get('Memo', '')

        if url:
            title_html = f'<a href="{url}" target="_blank">{title_val}</a>'
        else:
            title_html = title_val

        row_html = f"""        <tr>
          <td>{i}</td>
          <td class='authors'>{presenters}</td>
          <td>{title_html}</td>
          <td>{event}</td>
          <td>{location}</td>
          <td>{dates}</td>
          <td>{type_val}</td>
          <td>{memo}</td>
        </tr>"""
        rows.append(row_html)
    table_html = f"""      <h1>{title}</h1>
      <hr>
      <table class="pub-list">
        <tr>
          <th>#</th>
          <th>Presenters</th>
          <th>Title</th>
          <th>Event</th>
          <th>Location</th>
          <th>Dates</th>
          <th>Type</th>
          <th>Memo</th>
        </tr>
{chr(10).join(rows)}
      </table>
"""
    return table_html



def plot_yearly_counts_scatter(domestic_entries, international_entries, fig_file):
    """Plot number of presentations per year (scatter) for domestic, international, and total."""

    def count_per_year(entries):
        counts = Counter()
        for e in entries:
            dates = e.get('Dates', '')
            if dates:
                start_date = re.split(r'[;–]', dates)[0].strip()
                try:
                    year = int(start_date[:4])
                    counts[year] += 1
                except ValueError:
                    continue
        return counts

    domestic_counts = count_per_year(domestic_entries)
    international_counts = count_per_year(international_entries)

    # Combine all years
    all_years = sorted(set(domestic_counts.keys()) | set(international_counts.keys()))
    domestic_vals = [domestic_counts.get(y, 0) for y in all_years]
    international_vals = [international_counts.get(y, 0) for y in all_years]
    total_vals = [domestic_vals[i] + international_vals[i] for i in range(len(all_years))]

    plt.figure(figsize=(12, 6))
    plt.plot(all_years, domestic_vals, '-o', color='blue', label='Domestic')       
    plt.plot(all_years, international_vals, '-s', color='red', label='International')
    plt.plot(all_years, total_vals, '-^', color='green', label='Total') ー

    plt.xlabel('Year')
    plt.ylabel('Number of Presentations')
    plt.title('Presentations per Year')
    plt.xticks(all_years)
    plt.grid()
    plt.legend()
    plt.tight_layout()
    plt.savefig(fig_file, dpi=300)
    plt.close()



def main():
    parser = argparse.ArgumentParser(description="Generate presentation HTML")
    parser.add_argument("output_html", help="HTML output path")
    parser.add_argument("domestic", help="Domestic presentations text file")
    parser.add_argument("international", help="International presentations text file")
    parser.add_argument("--fig", help="Save figure of yearly counts")
    args = parser.parse_args()

    domestic_entries = parse_txt_file(args.domestic)
    international_entries = parse_txt_file(args.international)

    now = datetime.datetime.now()
    now = now.strftime("%Y-%m-%d")

    tables_html = ""
    tables_html += make_table_html(domestic_entries, "Domestic Presentations")
    tables_html += make_table_html(international_entries, "International Presentations")


    html_content = HTML_TEMPLATE.format(last_update=now, fig_file=args.fig, tables=tables_html)
    with open(args.output_html, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Generated HTML: {args.output_html}")

    if args.fig:
        plot_yearly_counts_scatter(domestic_entries, international_entries, args.fig)
        print(f"Saved figure: {args.fig}")

if __name__ == "__main__":
    main()

