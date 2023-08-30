
### Layers

`/raw/`: Used for data obtained externally. Each subdirectory should have the following elements.
  * `readme.md`: Completion of [`raw_directory_readme_template.md`](./raw_directory_readme_template.md).
  * `/docs`: Self-contained documentation sufficient (along with `readme.md`) to fully describe and document the data even without access to the original source.
  * `/orig`: Original form of data files.
  * `/data`: Lightly processed files in `orig`, with means of processing carefully described in `readme.md`.

`/derived/`: Used for data processed in the repository, saved using `save_data`.

### File types and sizes

* Store small ($\le$ 1MB) ASCII files (e.g. scripts) in git
* Store small ($\le$ 1MB) binary files (e.g. bitmap graphics) in git-lfs
* Store large ($>$ 1MB) files in the `datastore`
* Keep the git repository as small as possible, and no larger than 1GB (including version history and lfs)
* Export graphics in two formats:
  * EPS (or PDF if EPS is not available)
  * PNG (or SVG if PNG is not available)

### Working with the datastore

Make a juncture link from the local copy of datastore a 'datastore' folder under the git repository, e.g. in Windows:

`mklink /J <repository location>\datastore\ <datastore location>`

We typically work with an unsynced local copy of the datastore and then sync back up when we are ready to merge the issue.

### Warning

_Once something is committed to the repository, it cannot readily be uncommitted. Committing large or sensitive files can therefore permanently degrade the repository. Be careful with such commits._
