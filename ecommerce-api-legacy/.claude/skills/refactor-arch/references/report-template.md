# Reference — Audit Report Template (Phase 2)

The Phase-2 audit report MUST follow this exact structure. Save it to `./reports/audit.md` and also print it to the console.

````
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <project folder name>
Stack:   <language> + <framework>
Files:   <N> analyzed | ~<lines> lines of code

## Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>

## Findings

### [CRITICAL] <Anti-pattern name (AP-id)>
File: <path:line-start-line-end>
Description: <what is wrong, concretely, referencing the code>
Impact: <what breaks / what risk this creates>
Recommendation: <the fix, pointing at the playbook transformation>

### [CRITICAL] <next finding>
...

### [HIGH] <...>
...

### [MEDIUM] <...>
...

### [LOW] <...>
...

================================
Total: <N> findings
================================
````

## Rules

1. **Order findings by severity:** all CRITICAL first, then HIGH, then MEDIUM, then LOW.
2. **Every finding cites file + exact line range.** If an issue recurs, cite a representative range and add "(and N other occurrences)".
3. The `Summary` counts must equal the number of findings listed for each severity.
4. `Total` must equal the sum of the summary counts.
5. Use the anti-pattern names and IDs from `anti-patterns-catalog.md` so findings map to playbook transformations.
6. Keep `Description / Impact / Recommendation` on each finding — they justify severity and tell Phase 3 what to do.
7. Include a deprecated-API finding when applicable (AP-13); if none exist, you may add a single line under Summary: "Deprecated APIs: none detected".

After printing and saving the report, the skill prints the confirmation gate (see `SKILL.md`) and stops.
