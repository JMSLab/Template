When conducting an LLM pull review, we use the prompt below as a starting point and adapt it to suit the issue.

* Prepare
  * Read the discussion threads for the issue, all subissues, and the pull request.
  * Review the git diff to understand what changed.
  * Summarize the goals of the issue and the main changes associated with each. Flag any unmet goal.
* Review
   * Carefully review the changes to the code for compliance with our [coding principles](./principles.md).
   * Carefully review the changes to the code for errors, ambiguities, or inconsistencies.
   * Carefully review the changes to the draft, slides, or other documents for errors, ambiguities, or inconsistencies.
   * Carefully review the changes to file locations for compliance with our [storage principles](./storage.md).
   * Carefully review the changes to smaller ASCII-formatted output files for evidence of errors or unexpected changes. Ask me if you need to also review changes to larger or binary files.
* Deliver
   * Deliver your findings in a single markdown.
   * Separate comments by file and note which line they apply to.
   * Do not repeat comments that have already been made.
   * Suggest a solution for every error or problem that you find.
 
