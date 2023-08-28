Our workflow is based on [Github flow](https://docs.github.com/en/get-started/quickstart/github-flow) and assumes you are familiar with the concepts described there.
* **Open** an _issue_.
  * **Summarize** the goals in the _title_.
  * **Describe** the _deliverables_ in the _issue description_.
    * _Production_ deliverables include modifications to the production pipeline.
    * _Ephemeral_ deliverables are confined to an _issue subfolder_ defined as `./issue` relative to the root of the repository.
  * **Assign** one or more _assignees_.
* **Work** on the _issue_.
  * **Open** a [_linked issue branch_](https://docs.github.com/en/issues/tracking-your-work-with-issues/creating-a-branch-for-an-issue)
  * **Comment** whenever
    * you have a question (tagging the person to whom the question is addressed)
    * you have completed a discrete chunk of work
    * you have devoted at least one day of work to the _issue_ since the last update
    * you have not worked on the _issue_ for at least 5 business days since the last update
    * you have a substantive interaction about the issue outside of github (e.g., in a meeting)
* **Open** a _pull request_ when the goals of the _issue_ are completed.
  * **Assign** one or more _reviewers_.
  * **Assign** one or more _assignees_.
    * These are usually the original _assignees_ on the _issue_.
  * _Reviewers_ **review** the deliverable.
    * Check for violations of our standards for code clarity and data integrity (production deliverables).
    * Check for clear errors or reasons reproducibility will fail (all deliverables.)
    * _Reviewers_ **approve** the pull when all pull threads are resolved.
  * _Assignees_ **close** the pull.
    * **Squash-merge** the issue branch back to the `main` branch (production deliverables).
    * **Delete** the issue branch (all deliverables).
    * **Comment** in the original issue summarizing what is accomplished and including [permanent links](https://docs.github.com/en/repositories/working-with-files/using-files/getting-permanent-links-to-files) to:
      * the latest version of the deliverable (all deliverables)
      * the issue subfolder (ephemeral deliverables)
      * the latest version of the issue branch prior to merging (all deliverables).
    * **Link** to the summary comment in the pull request.
* **Prioritize** work in the order older pull requests > newer pull requests > older issues > newer issues.
  * Age is defined by github numbering.