# Website of J.B.


## TODO
- Add general background
- Add details of research topics in `research.html`
- Add presentation material in `presentation.html`
- Summarize (research) budget used in the past
- Add JB's whole life

## Update html files 
```
# Make `publication.html`
python script/bibtex2html.py publication.html --first ~/research/paper/bib/Beniyama* --Nth ~/research/paper/bib/Jiang2021.bib ~/research/paper/bib/Geem2022b.bib ~/research/paper/bib/Nishino2022.bib ~/research/paper/bib/Bolin2025_KY26.bib

# Make `presentation.html`
python script/presentation_html.py presentation.html doc/JB_domestic.txt doc/JB_international.txt --fig fig/presentation.png
```
