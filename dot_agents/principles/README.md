# Engineering principles

## Routing

Read this index before substantive implementation, debugging, refactoring, or verification work. On an explicit `principles` request, read it afresh against the current task, including work already done. Ordinary conversation does not require this index.

Match the current phase against every trigger below. Read each matching reference in full before making the decision it governs. Follow links between references when their triggers also apply. Reassess at phase changes and before declaring completion; load only the references relevant to that phase.

These references complement task skills, including upstream Matt Pocock skills. Keep upstream files intact. Existing model ownership, authorization, secrets, repository rules, and explicit user decisions govern application. If a task skill conflicts with a principle, follow the more specific applicable instruction and report any material unresolved conflict.

In the final report, briefly name the principles that materially changed a choice and the choice or evidence they changed. A citation requires reading the full reference; listing names alone is not application. For delegated work, include the relevant reference paths and require the delegate to read them, within existing delegation rules.

## Index

| When | Read |
| --- | --- |
| Planning a change, sizing its diff, or considering an abstraction | [Laziness Protocol](laziness-protocol.md) |
| Choosing core data shapes, access patterns, or shared scaffolding before logic | [Foundational Thinking](foundational-thinking.md) |
| A new requirement strains the inherited design | [Redesign from First Principles](redesign-from-first-principles.md) |
| Two fixes sharing an assumption fail the same check | [Attack the Premise](attack-the-premise.md) |
| Sequencing an addition or refactor around obsolete complexity | [Subtract Before You Add](subtract-before-you-add.md) |
| Shaping code with costly indirection or hidden mutable state | [Minimize Reader Load](minimize-reader-load.md) |
| Planning a rewrite or migration with explicit verification boundaries | [Outcome-Oriented Execution](outcome-oriented-execution.md) |
| Choosing product behavior, API usability, or feature scope | [Experience First](experience-first.md) |
| Nontrivial transformations, analyses, or verification need repeatable execution | [Build the Lever](build-the-lever.md) |
| Stateful logic, growing branches, or repeated domain assumptions | [Model the Domain](model-the-domain.md) |
| Wiring validation, error handling, or framework adapters | [Boundary Discipline](boundary-discipline.md) |
| Designing typed data or signatures, or parsing external data into types | [Type System Discipline](type-system-discipline.md) |
| Commands or lifecycle operations face retries or interruption | [Make Operations Idempotent](make-operations-idempotent.md) |
| Replacing an internal API whose callers can migrate together | [Migrate Callers Then Delete Legacy APIs](migrate-callers-then-delete-legacy-apis.md) |
| Concurrent actors may write the same mutable object | [Separate Before Serializing Shared State](separate-before-serializing-shared-state.md) |
| Verifying an output or preparing to declare completion | [Prove It Works](prove-it-works.md) |
| Diagnosing or fixing a reported defect | [Fix Root Causes](fix-root-causes.md) |
| Sequencing multiple edits, migration units, commits, or PRs | [Sequence Verifiable Units](sequence-verifiable-units.md) |
| Writing, changing, or evaluating tests | [Test Behavior, Not Implementation](test-behavior-not-implementation.md) |
| Planning a measurement or reporting a measured improvement or regression | [Explain the Number](explain-the-number.md) |
| Large outputs, repeated reads, or investigation fan-out threaten context | [Guard the Context Window](guard-the-context-window.md) |
| A correction recurs or the same instruction needs repeating | [Encode Lessons in Structure](encode-lessons-in-structure.md) |

Source attribution and local adaptations are recorded in [SOURCES.md](SOURCES.md).
