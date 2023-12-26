## Overview

Production encompasses the steps we take before we circulate or submit a paper draft. By default everything we say below about _the paper_ applies similarly to the online appendix and any other document that we plan to circulate.

* We will initiate production by assigning someone to an issue called "Supervise production". This _supervisor_ will:
  * Open a _main production branch_ linked to the "Supervise production" issue. We will refer to this as the _main production branch_.
  * Create and assign one github issue corresponding to each production task, with one assignee serving as _task lead_ on each task.
  * Keep in touch with everyone involved in production to help align timing and clear roadblocks.
  * Keep in mind that we expect production to take about one workweek with 3-4 people helping. 
  * When production is completed, compile the main production branch, create a PDF diff, and open a pull request with PI(s) assigned as reviewers.

*  When working on individual production tasks, to keep things moving and minimize scope for branch conflict:
   * Note the default time estimate. If you expect a much longer time to completion, consult the PI(s).
   * Do not create an issue branch until you are ready to make edits.
   * When creating an issue branch, branch off of the main production branch.
   * Avoid compiling on issue branches unless necessary.
   * When merging an issue branch, merge back to the main production branch.
   * Skip review of pulls for tasks where work has already been reviewed by multiple RAs.
   * Avoid compiling on production issueWhen it can be avoided, we recommend not fully compiling production issue branches before merging back to the main production branch, so as to minimize scope for merge conflicts.

* When producing task deliverables:
   * Post them in the relevant issue branch and @ references the PI(s).
   * Make them clear and readable but don't worry about making them pretty.
   * If possible, ask the task lead to consolidate different sets of comments into a single list or PDF.

## Task [PRESS]: Notify university communications office
 
   * Check with PIs whether this is needed

## Task [DUA]: Check DUAs for review requirements

### Work allocation

  | Expected Hours | 50% Confidence Interval | # of RAs |
  | -------------- | ----------------------- | -------- |
  | 1              | (0 - 3)                 | 1        | 

  * Check DUAs. If any require notification in advance of posting/journal submission, flag for PIs.
  * May be efficient to combine with [[SOURCE]](https://github.com/gslab-econ/ra-manual/wiki/Production#task-source-check-acknowledgment-of-sources).

## Task [PRELIM]: Things to double-check in code & analysis

### Work allocation

  | Expected Hours | 50% Confidence Interval | # of RAs |
  | -------------- | ----------------------- | -------- |
  | 2              | (0.5 - 4)               | 1        | 


### Steps
  *  Bootstraps and simulations run with sufficiently high number of draws

  *  Quadrature accuracy set sufficiently high

  *  Tolerances on solvers satisfactory

  *  Exit flags for solvers indicate convergence

## Task [EXT]: Audit external calls

### Work allocation

  | Expected Hours | 50% Confidence Interval | # of RAs |
  | -------------- | ----------------------- | -------- |
  | 4              | (2 - 6)                 | 1        |

### Goals

  *  Confirm that results reported in paper would be unchanged if all externals calls to Google Drive, Dropbox, etc. are pointed to the most recent version.

  *  Confirm that scons run is up to date and sources/targets are defined appropriately.

### Deliverables 

  * A list of any external calls that are out of date and would impact the results.

  * A list of any source/targets specified incorrectly and any directories that need to be re-run via scons.

## Task [REF]: Check/update references

### Work allocation

  | Expected Hours | 50% Confidence Interval | # of RAs |
  | -------------- | ----------------------- | -------- |
  | 4              | (2 - 6)                 | 1        |

### Goals  

  *  All citations in the text match references in the bibliography. (Online appendix references should include only those citations not present in the main document.)

  *  All references in the bibliography are cited somewhere in the text.

  *  Author names and years in text citations are correct and in-text citations follow the formatting guidance in the [paper style guide](https://github.com/gslab-econ/ra-manual/wiki/Papers) including punctuation.

  *  If we are citing working papers, these have not in fact been published. If they have we should update the reference accordingly.

  *  The references list is correct and uses a consistent style. (It is not important which style guide we follow, just that we are consistent.)

  *  URLs in the references list are [saved in the internet archive](https://help.archive.org/help/save-pages-in-the-wayback-machine/#:~:text=Browser%20extensions%20and%20add%2Dons,give%20you%20a%20permanent%20URL.) if possible. (References list can still use the original URL rather than the archive URL.)

### Deliverables 

  *  An updated `draft.lyx/online.lyx` file with corrected in-text citations and references.

  *  A single pdf document that highlights (using Acrobat commenting tools) any changes that are substantive enough to require review by PIs.

  *  A list of URLs newly saved to the internet archive.

## Task [PROOF]: Proofread spelling, grammar, table references, math, etc. 

### Work allocation

  | Expected Hours | 50% Confidence Interval | # of RAs |
  | -------------- | ----------------------- | -------- |
  | 16             | (8 - 24)                | 2        |

### Goals 

  *  Typos, spelling/grammar errors, unclear wording, etc. corrected (don’t forget to include table notes, figure notes, footnotes, axis labels, appendices, etc.)

  *  Follow rules outlined in [paper style guide](https://github.com/gslab-econ/ra-manual/wiki/Papers)

  *  References to any sections of the paper or tables or figures check out, in the sense that the referenced object exists and seems to have the information promised by the reference

  *  Titles of sections, tables, figures, etc. are clear, descriptive

  *  Variable names, notation, and other concepts are used consistently; the same notation is never used to refer to two different things

  *  This task does not extend to (if extant) the cover letter and referee replies.  

### Deliverables

  *  If you notice a recurring issue, let PIs know immediately via comment thread, and provide examples in the thread. PIs will weigh in with instructions to (i) address the issue throughout; (ii) ignore; (iii) do not change but flag all instances in the final deliverable. MG/JMS will also instruct on whether the  [paper style guide](https://github.com/gslab-econ/ra-manual/wiki/Papers) should be updated to clarify the issue.

  *  A single pdf document with all changes/comments clearly marked using Adobe Acrobat’s commenting tools. Recurring issues are flagged individually only if requested by PIs per the preceding.

## Task [FACT]: Check all factual claims made in the paper 

### Work allocation

  | Expected Hours | 50% Confidence Interval | # of RAs |
  | -------------- | ----------------------- | -------- |
  | 6              | (4 - 8)                 | 2        |

### Goals 

  *  Every quantitative/factual claim made in the paper is either [autofilled](https://github.com/gslab-econ/ra-manual/wiki/Autofilling-Values) or is supported by (i) a citation, (ii) an entry in a table, (iii) a figure, or (iv) a result shown in a supporting pdf document within the drafts directory (e.g., text.pdf). Log files external to the drafts do not qualify as supporting documents.

  *  If a fact is supported by a citation, it is not necessary to check the paper or book we are citing to verify that it contains the fact.

  *  All tables/figures in text.pdf (or its analogues) are referenced at least once in the paper or online appendix. (If a table reports many numbers or a figure has many panels, it is sufficient that at least one number or one panel is referenced somewhere in the paper or online appendix.)

  *  All content (tables/figures/discussion) in the online appendix or main appendix is referenced at least once in the paper.

  *  Within each section (tables/figures/discussion) of the online appendix, content appears in the order in which it is referenced in the paper.

### Deliverables

  *  A single pdf document with all unsupported claims clearly marked using Adobe Acrobat’s commenting tools and all claims supported externally (e.g. in text.pdf or online.pdf) highlighted with a note stating where they are supported (e.g. “supported in online appendix table 6.”)

  *  A version of text.pdf with comments noting, for each table and figure, either (i) a place it is referenced in the paper or online appendix, or (ii) that the table or figure does not appear to be referenced.

  *  A version of the online appendix with comments noting, for each table and figure, either (i) a place it is referenced in the paper or online appendix, or (ii) that the table or figure does not appear to be referenced, as well as whether the object is in the correct position.
 
  * Versions of the preceding files labeled "for attention" that include only flags for items that need review.

## Task [DEF]: Check sample and variable definitions 

### Work allocation

  | Expected Hours | 50% Confidence Interval | # of RAs |
  | -------------- | ----------------------- | -------- |
  | 6              | (4 - 8)                 | 1        |

### Goals

  *  Main statements made in paper about definitions of samples and variables are consistent with code.

  *  Checking every variable and sample definition can for some projects take a large amount of time. By default, this task should be limited to a single person-day of work. Unless specifically directed otherwise, you should focus on checking the definition of the main sample(s) in the paper and variables in the core specification(s), and either ignore or just spot-check robustness analyses, supplemental analyses in appendices, etc.

### Deliverables 

  *  A list of any inconsistencies between text and code

## Task [SOURCE]: Check Acknowledgment of Sources 

### Work allocation
   
  | Expected Hours | 50% Confidence Interval | # of RAs |
  | -------------- | ----------------------- | -------- |
  | 1              | (0.5 - 2)               | 1        |

### Goals 

  *  Data sources are acknowledged in a manner consistent with our agreement with the data provider.

### Deliverables 

  *  A single pdf document with proposed changes to acknowledgments clearly marked using Adobe Acrobat’s commenting tools. Comments should identify acknowledgments that need to be added along with proposed wording, as well as proposed revisions to existing acknowledgments. Comments should identify the source in the repository of the relevant user agreement.

  *  Data sources and user agreements should be clearly indicated in the readme and /docs of the raw data directories used by the project. The raw data directories should be updated if this is not the case.

## Task [THANK]: Check acknowledgment of comments and funding

### Work allocation

  | Expected Hours | 50% Confidence Interval | # of RAs |
  | -------------- | ----------------------- | -------- |
  | 1              | (0.5 - 2)               | 1        |

### Goals 

  *  Funding sources are acknowledged.

  *  Seminar participants and those who provided comments are acknowledged.

  *  RAs / predocs are acknowledged (default language: "We thank our dedicated research assistants for their contributions to this project.")


### Deliverables

  *  A list of unacknowledged sources of funding and comments.

  *  Notes:

     *  To catch unacknowledged comments, check the project wiki.

     *  To catch unacknowledged funding sources, make a list of the funding sources acknowledged in each author's recent papers, excluding those already thanked here, and show each author this list to see if one or more of the sources should be thanked.

## Task [PLOT]: Check printing of plots in black and white 

### Work allocation

  | Expected Hours | 50% Confidence Interval | # of RAs |
  | -------------- | ----------------------- | -------- |
  | 6              | (4 - 12)                | 1        |

### Goals 

  *  Color plots print well in black and white; markers are sufficiently distinct
  *  Plots follow [our guidelines](https://github.com/gslab-econ/ra-manual/wiki/Papers-&-Slides#plots)

### Deliverables 

  *  A list of plots for which you think there are contrast issues in black and white, along with suggested fixes. (If it is easy to modify the plots, the ideal format for suggestions is graphics files attached to the relevant issue illustrating the proposed alternative coloring.)


## Task [MATH]: Check theoretical claims in the paper

### Work allocation

  | Expected Hours | 50% Confidence Interval | # of RAs |
  | -------------- | ----------------------- | -------- |
  | 8              | (2 - 16)                | 2        |

### Goals 

  *  All nontrivial mathematical claims in the paper are documented.

  *  By default, this does not include checking statements within proofs. However, PIs should be consulted at the beginning of this task to confirm the desired scope.

### Deliverables 

  *  A list of all theoretical claims that are made in the text of the paper that are not supported by proofs in the paper, appendices, or claims.pdf. For example, we may say, "It is easy to show that equations A, B, and C together imply equation D." You should not include claims that are completely obvious. We’re looking for things where if somebody came back and said, "I don’t believe this is true" we would need to go back and do at least a couple of lines of algebra to confirm that we’re right.

  *  A version of claims.pdf with comments noting, for each claim, either (i) a place it is referenced in the paper or online appendix, or (ii) that the claim does not appear to be referenced.

## Task [REPLY]: Check claims in responses to editor and referees [R&Rs only]

### Work allocation

  | Expected Hours | 50% Confidence Interval | # of RAs |
  | -------------- | ----------------------- | -------- |
  | 8              | (4 - 12)                | 2        |

### Goals

  *  Every question or comment by an editor or referee is addressed directly in the corresponding response letter.

  *  Every statement made in a cover letter to the editor or a reply to a referee is correct. If the statement refers to a change to the paper, the paper has changed as indicated since the previous submission. If the statement is a table or figure referenced but not shown in the paper, the table or figure presented to the editor/referee matches a supporting document.

  *  Conduct [PROOF](https://github.com/gslab-econ/ra-manual/wiki/Paper-Production#task-proof-proofread-spelling-grammar-table-references-math-etc) on the cover letter and replies, with a focus on clear errors or issues that would cause confusion. Consistency in style is not that key in replies since they will not be published and are intrinsically transient. 

### Deliverables

  *  A single pdf document combining the editor’s letter and all referee reports, with all unaddressed comments/questions clearly marked using Adobe Acrobat’s commenting tools.

  *  A single pdf document combining all responses to the editor/referees, with all unsupported/incorrect claims and the results from the PROOF clearly marked using Adobe Acrobat’s commenting tools. Please also note the specific table/figure/section number in which claims made in the responses are documented, unless these are already referenced by number.


## Task [GALLEY]: Checking galley proofs 

### Work allocation

   *  Consult PIs. 

### Goals 

  *  We have flagged all errors in translating our submitted manuscript into the journal’s typeset format.

  *  We have a response to all Author Queries (AQs) raised by the journal's production team.

  *  Note in particular that the goal here is not to proofread the paper (i.e., not to perform the above-listed production steps). We presume we will have done that as of the last submission, so the only possible remaining errors are those from typesetting.

### Deliverables 

  *  A single pdf document that lists all discrepancies between our original typeset manuscript as of the last submission to the journal and the galley proofs using Adobe Acrobat’s commenting tools. Pay special attention to the formatting of tables, figures, and equations, as these are where most discrepancies tend to arise. The pdf comments should be formatted in a manner suitable for direct transmission to the publisher.

  *  In the same pdf document, also comment on anything else that looks like a typo or error that you happen to come across. Note that you should be looking only for discrepancies with respect to the last submission, not doing any other form of proofreading. But if you do notice a probable error along the way it is best to flag it as it may still be possible to correct it.

  *  A list of proposed replies to the AQs formatted in a manner suitable for direct transmission to the publisher. This can be included in the same pdf as above.
