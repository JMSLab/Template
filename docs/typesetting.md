## Typesetting

Here is a default approach to preparing a paper for typesetting.
* `/source/typesetting` contains `typesetting.py` which outputs to `/output/typesetting/typesetting.zip`
* `typesetting.zip` contains
  * `/source/` with LyX or TeX files
  * `/refs/` with BIB files or other bibliography files
  * `/graphics/` with graphics files (EPS or PDF)
  * `/output/` with compiled paper and appendix (PDF)
* It's ideal (but not essential) if files in `/source` can be directly compiled to files in `/output`. For this it may be necessary to add `../graphics` to the [`graphicspath`](http://latexref.xyz/_005cgraphicspath.html) of files in `/source`.
