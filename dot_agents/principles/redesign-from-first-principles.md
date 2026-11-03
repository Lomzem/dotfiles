# Redesign From First Principles

When a new requirement strains the existing design, reason about the design as if the requirement had been foundational from the start. Use that target to choose the smallest coherent implementation within the authorized scope.

- Read all affected files and understand the current design
- Ask: "if we were writing this from scratch with this new requirement, what would we build?"
- Propagate the change through every reference: types, docs, examples, rationale sections
- Think about the whole redesign, then deliver it incrementally

This is the method for preserving option value when integrating changes into an existing design.
