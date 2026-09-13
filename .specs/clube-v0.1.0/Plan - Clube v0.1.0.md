# Plan - Clube v0.1.0

## Execution Architecture

```mermaid
flowchart TD
    subgraph Wave1["Wave 1 (Async Implementation)"]
        T1["T1: Translate 4 Skills (EN)"]
        T2["T2: Create clube-architecture Skill"]
        T3["T3: Implement ui.py & audit-*.py runlog"]
    end

    subgraph Wave2["Wave 2 (Manifests & Docs)"]
        T4["T4: SemVer 0.1.0 Alignment"]
        T5["T5: Bilingual Documentation (PT/EN)"]
    end

    subgraph Wave3["Wave 3 (Review & Verification)"]
        T6["T6: Gates (make check, make audit) & PR"]
    end

    Wave1 --> Wave2 --> Wave3
```

## Review & Security Strategy
- Code review performed via `review` subagent verifying contract adherence and SemVer parity.
- Security review performed via `expert-security` auditing file paths, scripts, and inputs for no command injections or unvetted privilege escalation.
- Zero-token verification gate: `make check` and `make audit` must pass 100%.
