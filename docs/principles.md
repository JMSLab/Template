When writing or reviewing new code, by default, we follow the principles below, hierarchically from top to bottom.
* **Architecture**: We follow the architecture outlined [here](https://github.com/JMSLab/Template/).
* **Concepts**: We follow the concepts outlined [here](https://shapiro.scholars.harvard.edu/sites/g/files/omnuum7731/files/shapiro/files/codeanddata.pdf), available also in [markdown](https://shapiro.scholars.harvard.edu/sites/g/files/omnuum7731/files/2026-03/CodeAndData.md_.txt) and [TeX](https://shapiro.scholars.harvard.edu/sites/g/files/omnuum7731/files/2026-03/CodeAndData_flat.tex_.txt). For a human in a hurry, or an LLM with a limited context window, key takeaways are:
  * Automate everything.
  * Separate directories by function and clearly separate inputs (code) and outputs (produced by code).
  * Store cleaned data in tables with unique, non-missing keys, and keep data normalized as far into the code pipeline as possible.
  * Abstract to eliminate redundancy or improve clarity; otherwise, don't abstract.
  * Make code self-documenting by using descriptive naming for functions and other objects; use comments sparingly to disambiguate.
  * Keep scripts and functions short and readable.
  * Separate slow code from fast code.
* **Language**: We use Python except in these circumstances:
  * we are using someone else's code (e.g., a replication package)
  * we need a package (e.g., a statistical function) only available in another language, and we have verified that we cannot easily port the package into Python. We prefer R for these use cases.
  * we have a working Python implementation and after profiling we find that we need to move some components into a lower-level language. We prefer C for these use cases.
* **Style**: We use function encapsulation, with a `Main()` function at the top of the script, and subsequent functions written in order of use.
* **Abstraction**: In any of the circumstances below, we create an object-oriented library with extensive unit-testing:
  * we are preparing a package (e.g., an econometric toolkit) that could, or will, be used by others
  * we are preparing a library of functions that we will use extensively and repeatedly throughout the project
