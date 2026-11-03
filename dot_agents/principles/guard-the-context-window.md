# Guard the Context Window

**Why:** Context overflow degrades reasoning quality, creates compression artifacts, and halts progress.

**Pattern:**
- **Size phases and cap scope.** Limit files per phase, set turn budgets, account for mechanism costs.
- Start with targeted files and bounded output; retain evidence paths and concise findings instead of bulk payloads.
- Delegate independent bulk investigation when it benefits from a separate context, following the existing model ownership and delegation rules.
