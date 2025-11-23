## Table of Contents

- [Overview](#overview)
- [Front Matter](#front-matter)
- [Code and Data](#code-and-data)
- [Paper](#paper)
- [Journal](#journal)

## Overview

Production encompasses the steps we take before we circulate or submit a paper draft. By default everything we say below about _the paper_ applies similarly to the online appendix and any other document that we plan to circulate.

* We will initiate production by assigning someone (the _supervisor_) to an issue called "Supervise production". The supervisor will:
  * Open a _main production branch_ linked to the "Supervise production" issue. We will refer to this as the _main production branch_.
  * Create and assign one github subissue corresponding to each production task, with one assignee serving as _task lead_ on each task.
  * Keep in touch with everyone involved in production to help align timing and clear roadblocks.
  * Keep in mind that we expect production to take about one workweek with 3-4 people helping. 
  * When production is completed, compile the main production branch, create a PDF diff, and open a pull request with PI assigned as reviewer.

*  When working on individual production tasks, to keep things moving and minimize scope for branch conflict:
   * Note the default time estimate. If you expect a much longer time to completion, consult the PI.
   * Do not create a subissue branch until you are ready to make edits.
   * When creating a subissue branch, branch off of the main production branch.
   * Avoid compiling on subissue branches unless necessary.
   * When merging a subissue branch, merge back to the main production branch and update other open production branches.
   * Skip review of pulls for tasks where work has already been reviewed by multiple RAs, except where PI review is requested below.

* When producing task deliverables:
   * Post them in a comment in the relevant subissue and tag the PI.
   * Make them clear and readable but don't worry about making them pretty.
   * Use Adobe Acrobat commenting tools when commenting on a PDF.
   * If possible, ask the task lead to consolidate different sets of comments into a single list or PDF.

## Front Matter

### Task [PRESS]: Notify university communications office
 
   * Check with PIs whether this is needed

### Task [SOURCE]: Check acknowledgment of sources and review requirements

#### Work allocation
   
  | Expected Hours | 50% Confidence Interval | # of RAs |
  | -------------- | ----------------------- | -------- |
  | 1              | (0.5 - 5)               | 1        |

#### Goals 

  *  Data sources are acknowledged in a manner consistent with our agreement with the data provider.
  *  Data providers are provided with advanced notice when required by DUAs.
  *  Data sources and user agreements are clearly indicated in the readme and /docs of the raw data directories.

#### Deliverables 

  *  A single pdf document with proposed changes to acknowledgments, including information on the location of the relevant DUA in the corresponding raw data directory.
  *  A list for PI of updates to raw data documentation.
  *  A list for PI of any DUAs that require that we notify someone in advance of posting/submission, and the language giving the details of whom/how/when to notify.

### Task [THANK]: Check acknowledgment of comments and funding

#### Work allocation

  | Expected Hours | 50% Confidence Interval | # of RAs |
  | -------------- | ----------------------- | -------- |
  | 1              | (0.5 - 2)               | 1        |

#### Goals 

  *  Funding sources are acknowledged.
  *  Seminar participants and those who provided comments are acknowledged.
  *  Research assistants acknowledged.
      * Default language: "We thank our dedicated research assistants for their contributions to this project."

#### Deliverables

  *  A list of unacknowledged sources of funding and comments.
     *  To catch unacknowledged comments, check the project wiki.
     *  To catch unacknowledged funding sources, make a list of the funding sources acknowledged in each author's recent papers, excluding those already thanked here, and show each author this list to see if one or more of the sources should be thanked.

## Code and Data

### Task [NUMERICAL]: Check accuracy of numerical procedures

#### Work allocation

  | Expected Hours | 50% Confidence Interval | # of RAs |
  | -------------- | ----------------------- | -------- |
  | 2              | (0.5 - 4)               | 1        | 

#### Goals 

  *  Calculations have sufficient accuracy.

#### Deliverables

  * Check the below and notify the PI of any suggested changes.
     *  Randomization is controlled (e.g. by fixed seeds)
     *  Bootstraps and simulations run with sufficiently high number of draws
     *  Quadrature accuracy set sufficiently high
     *  Tolerances on solvers satisfactory
     *  Exit flags for solvers indicate convergence

### Task [COMPILE]: Check reproducibility of paper

#### Work allocation

  | Expected Hours | 50% Confidence Interval | # of RAs |
  | -------------- | ----------------------- | -------- |
  | 4              | (2 - 6)                 | 1        |

#### Goals

  *  Paper would be unchanged if recompiled from scratch.

#### Deliverables 

  * A list of any source/targets specified incorrectly and any directories that need to be recompiled.

### Task [DEF]: Check sample and variable definitions 

#### Work allocation

  | Expected Hours | 50% Confidence Interval | # of RAs |
  | -------------- | ----------------------- | -------- |
  | 6              | (4 - 8)                 | 1        |

#### Goals

  *  Main statements made in paper about definitions of samples and variables are consistent with code.
  *  Checking every variable and sample definition can for some projects take a large amount of time. By default, this task should be limited to a single person-day of work. Unless PI notes otherwise, you should focus on checking the definition of the main sample(s) in the paper and variables in the core specification(s), and either ignore or just spot-check robustness analyses, supplemental analyses in appendices, etc.

#### Deliverables 

  *  A list of any inconsistencies between text and code

## Paper

### Task [PROOF]: Proofread

#### Work allocation

  | Expected Hours | 50% Confidence Interval | # of RAs |
  | -------------- | ----------------------- | -------- |
  | 16             | (8 - 24)                | 2        |

#### Goals 

  *  There are no typos, spelling or grammatical errors, unclear wording, including in table notes, figure notes, footnotes, axis labels, appendices, etc.
     * We use a "conversational" rule to decide where to put commas. There is no need to flag commas to be added or subtracted unless there is a clear typo or a significant issue of clarity or ambiguity.
  *  Capitalization and other style choices are internally consistent. If not, please indicate which is the most common convention.
  *  Cross-references (e.g. to sections, tables, figures, etc.) check out, in the sense that the referenced object exists and seems to have the information promised by the reference.
  *  Titles of sections, tables, figures, etc. are clear and descriptive.
  *  Variable names, notation, and other concepts are used consistently; the same notation is never used to refer to two different things

#### Deliverables

  *  If you notice a recurring issue, let PI know immediately via comment thread, and provide examples in the thread. If it is an internal inconsistency, please indicate which style choice is most common.
  *  A single pdf document with all suggested changes / comments. Recurring issues are flagged individually only if requested by PI per the preceding.


### Task [REF]: Check/update references

#### Work allocation

  | Expected Hours | 50% Confidence Interval | # of RAs |
  | -------------- | ----------------------- | -------- |
  | 4              | (2 - 6)                 | 1        |

#### Goals  

  *  All citations in the text of the paper match references in the bibliography.
  *  All references in the bibliography are cited somewhere in the text of the paper.
  *  Citations and bibliography use a consistent style. (It is typically not important which style guide we follow, just that we are consistent.)
  *  Working papers cited have not been published and are not listed as forthcoming on the authors' homepages.
  *  Access dates are given for all URLs.
  *  URLs in the references list are stable or are saved in the [internet archive](https://web.archive.org/). (References list can still use the original URL rather than the archive URL, but in these cases it is good to include a hidden comment with a link to the internet archive version.)

#### Deliverables 

  *  Revised paper and bibliography file. (Edits can be made directly.)
  *  Open a pull request assigned to PI and include a link to a PDF diff.

### Task [FACT]: Check all factual claims made in the paper 

#### Work allocation

  | Expected Hours | 50% Confidence Interval | # of RAs |
  | -------------- | ----------------------- | -------- |
  | 6              | (4 - 8)                 | 2        |

#### Goals 

  *  Every quantitative/factual claim made in the paper is either autofilled or is supported by a citation or cross-reference within the paper.
      * Log files or other files external to the paper do not qualify.
      * If a fact is supported by a citation, it is not necessary to check the paper or book we are citing to verify that it contains the fact.
  *  All content (tables/figures/discussion) in the online appendix or main appendix is referenced at least once in the paper.
  *  Within each section (tables/figures/discussion) of the online appendix, content appears in the order in which it is referenced in the paper.

#### Deliverables

  *  A single pdf document that marks all unsupported claims and unreferenced content in the online appendix.

### Task [PLOT]: Check visual clarity of plots

#### Work allocation

  | Expected Hours | 50% Confidence Interval | # of RAs |
  | -------------- | ----------------------- | -------- |
  | 6              | (4 - 12)                | 1        |

#### Goals 

  *  Color plots print well in black and white; markers are sufficiently distinct
  *  Labels, legends, and axis titles are clearly readable and interpretable
  *  Plots adhere to [Schwabish (2014)](https://www.jstor.org/stable/43193723) principles.

#### Deliverables 

  *  An annotated PDF of the draft with suggested changes.
  *  (If it is easy to modify the plots) A side-by-side showing original and proposed modified plots.

### Task [MATH]: Check theoretical claims in the paper

#### Work allocation

  | Expected Hours | 50% Confidence Interval | # of RAs |
  | -------------- | ----------------------- | -------- |
  | 8              | (2 - 16)                | 2        |

#### Goals 

  *  All nontrivial mathematical claims in the paper are documented.
     * Check with PI whether it is necessary to check statements within proofs.

#### Deliverables 

  *  A list of all theoretical claims that are made in the text of the paper that are not supported by proofs in the paper, appendices, or claims.pdf.
      * For example, we may say, "It is easy to show that equations A, B, and C together imply equation D."
      * You can omit claims that are obvious. We are interested in those where, if somebody challenged the claim, we would need to do at least a few minutes of work (e.g., a few lines of algebra) to confirm that the claim is right.
   
## Journal

### Task [REPLY]: Check claims in responses to editor and referees

#### Work allocation

  | Expected Hours | 50% Confidence Interval | # of RAs |
  | -------------- | ----------------------- | -------- |
  | 8              | (4 - 12)                | 2        |

#### Goals

  *  Every question or comment by an editor or referee is addressed directly in the corresponding response letter.
  *  Every statement made in a cover letter to the editor or a reply to a referee is correct. If the statement refers to a change to the paper, the paper has changed as indicated since the previous submission. If the statement is a table or figure referenced but not shown in the paper, the table or figure presented to the editor/referee matches a supporting document.
  *  Proofread the cover letter and replies, with a focus on clear errors or issues that would cause confusion, rather than on things like consistency in style.

#### Deliverables

  *  A single pdf document combining the editor’s letter and all referee reports, with all unaddressed comments/questions clearly marked using Adobe Acrobat’s commenting tools.
  *  A single pdf document combining all responses to the editor/referees, with all unsupported/incorrect claims and the results from the PROOF clearly marked using Adobe Acrobat’s commenting tools. Please also note the specific table/figure/section number in which claims made in the responses are documented, unless these are already referenced by number.

### Task [TYPESETTING]: Prepare typesetting package

#### Work allocation

  | Expected Hours | 50% Confidence Interval | # of RAs |
  | -------------- | ----------------------- | -------- |
  | 8              | (4 - 12)                | 2        |

#### Goals

* We transmit typesetting files to the journal in a suitable format.

#### Deliverables

* Revised production files (e.g., `LyX` or `TeX`) for the paper draft that conform to journal style requirements.
  * If something seems prohibitively difficult to implement, note it for the PI and move on.
* Outputted ZIP archive suitable for transmission to the journal. How we want to do this will depend on the journal but here is a default approach.
  * `/source/typesetting` contains `typesetting.py` which outputs to `/output/typesetting/typesetting.zip`
  * `typesetting.zip` contains
    * `/source/` with `LyX` or `TeX` files
    * `/refs/` with `BIB` files or other bibliography files
    * `/graphics/` with graphics files (`EPS` or `PDF`)
    * `/output/` with compiled paper and appendix (`PDF`)
  * It's ideal (but not essential) if files in `/source` can be directly compiled to files in `/output`. For this it may be necessary to add `../graphics` to the [`graphicspath`](http://latexref.xyz/_005cgraphicspath.html) of files in `/source`.

### Task [REPLICATION]: Prepare replication package

#### Work allocation

  | Expected Hours | 50% Confidence Interval | # of RAs |
  | -------------- | ----------------------- | -------- |
  | 16             | (8 - 24)                | 2        |

#### Goals

* We transmit a replication archive to the journal in a suitable format.

#### Deliverables

* Readme for replicators suitable for transmission to the journal.
* Outputted ZIP archive suitable for transmission to the journal. How we want to do this will depend on the journal but here is a default approach.
  * `/source/replication` contains
    * `replication.py` which outputs to `/datastore/output/replication/replication.zip`
    * `readme_for_replication.md` which `replication.py` copies as `readme.md` into the root of `replication.zip`
    * `exclude.txt` which lists files/folders/patterns we want to exclude from `replication.zip` (e.g. because we are not permitted to share them)

### Task [GALLEY]: Check page proofs 

#### Work allocation

  | Expected Hours | 50% Confidence Interval | # of RAs |
  | -------------- | ----------------------- | -------- |
  | 8              | (4 - 12)                | 2        |

#### Goals 

  *  We have flagged all errors in translating our submitted manuscript into the journal’s typeset format.
     * The goal here is not to proofread the paper (i.e., not to perform the above-listed production steps), but rather to flag errors introduced in the typesetting process itself.
  *  We have a response to all Author Queries (AQs) raised by the journal's production team.

#### Deliverables 

  *  A single pdf document that lists all discrepancies between our original typeset manuscript as of the last submission to the journal and the page proofs.
     * Pay special attention to the formatting of tables, figures, and equations, as these are where most discrepancies tend to arise.
     * The pdf comments should be formatted in a manner suitable for direct transmission to the publisher.
     * If you happen to notice any typos or errors not introduced during typesetting, you can note these here too.
  *  A list of proposed replies to the AQs formatted in a manner suitable for direct transmission to the publisher. This can be included in the same pdf as above.
