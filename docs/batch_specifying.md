### Batch-specifying targets and sources

There are many instances where we have numerous targets and/or sources to be specified.

Here we'll consider a hypothetical example where:

- A script named `inflation_plots.R` in `source/analysis/plots` takes monthly inflation data 
for Germany, France, and Turkey for the years 1980, 1990, 2000, 2010, and 2020 from 
`datastore/raw/inflation`, and outputs monthly time-series plots for each country-year to `output/analsis/plots`.
- Assume that the names of the raw files have the form `countrycode_year.csv` (e.g. `FR_1990.csv`) and
output files have the form `countrycode_year.png` and `countrycode_year.eps`. 

### Batch-specifying sources

For source files, we suggest using `Glob()`, as in:

```
source = ['#source/analysis/plots/inflation_plots.R',          
          Glob('#datastore/raw/inflation/*.csv')]
```

### Batch-specifying targets

For target files, we suggest using one of the following:

1. Loops

An example:

```
target = []
for country in ['FR', 'DE', 'TR']:
    for year in ['1980', '1990', '2000', '2010', '2020']:    
        target += [
            '#output/analysis/plots/%s_%s.eps' % (country, year),
            '#output/analysis/plots/%s_%s.png' % (country, year),
        ]
```

2. `list_files.py`

Alternatively, you can use `source/lib/list_files.py`.

- Using a terminal, to get a list of the files in `output/analysis/plots`, you can write:

`python source/lib/list_files.py output/analysis/plots`

- To get a list of files in the same folder with `.eps` extension, you can write:

`python source/lib/list_files.py output/analysis/plots --patterns "*.eps"`

- By default, this script follows `gitignore` rules, i.e. it doesn't return files that are ignored by Git. To override this, use:

`python source/lib/list_files.py output/analysis/plots --no-git --patterns "*.eps" `
