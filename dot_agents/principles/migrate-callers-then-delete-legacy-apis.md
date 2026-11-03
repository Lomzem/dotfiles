# Migrate Callers Then Delete Legacy APIs

When replacing an internal API whose callers can migrate together, update every caller and delete the obsolete API in the same wave. Verify that no callers or references still depend on it before removing it; preserve compatibility where external users require it.

- Update tests to assert the new contract, and delete tests that only protect pre-refactor implementation details

**When this applies:**
- No external users depend on backward compatibility
- The project can absorb coordinated breaking changes
- The new API is part of a simplification or refactor initiative
