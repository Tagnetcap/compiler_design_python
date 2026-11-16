# Compiler Design & Parser Suite (Python)

A modular, standalone Python toolkit implementing core syntax analysis algorithms, context-free grammar analysis, canonical item collection generation, parsing table construction, and shift-reduce execution engines.

---

## Features

- **Grammar Analysis**: Automated computation of FIRST and FOLLOW sets with epsilon (`#`) propagation.
- **Top-Down Parsing**: LL(1) parsing table construction and deterministic predictive stack parsing.
- **Bottom-Up LR Parsing Suites**:
  - **LR(0)**: Canonical collection of item sets, transition diagrams, and table generation.
  - **SLR(1)**: Follow-directed reduce conflict resolution and parsing.
  - **CLR(1) / Canonical LR(1)**: Full LR(1) items with lookahead tracking and minimal conflict surface.
  - **LALR(1)**: State merging on identical LR(1) cores with merged transition mapping.
- **Trace & Simulation**: Step-by-step stack, input buffer, and action tracing (Shift, Reduce, Accept, Reject).

---

## File Overview

```
compiler_design_python/
├── main_menu.py                 # Interactive master CLI launcher
├── first_follow.py              # FIRST and FOLLOW set computation
├── ll1_parser.py                # LL(1) table generator & predictive parser
├── lr0_simple.py                # LR(0) canonical items & grammar check
├── lr0_parser.py                # LR(0) parsing table generator
├── lr0_input_string_check.py    # LR(0) shift-reduce parsing engine
├── slr1_simple.py               # SLR(1) items & grammar check
├── slr1_parser.py               # SLR(1) parsing table generator
├── slr1_input_string_check.py   # SLR(1) shift-reduce parsing engine
├── clr1_simple.py               # CLR(1) LR(1) items & grammar check
├── clr1_parser.py               # CLR(1) parsing table generator
├── clr1_input_string_check.py   # CLR(1) shift-reduce parsing engine
├── lalr1_simple.py              # LALR(1) core-merged items & grammar check
├── lalr1_parser.py              # LALR(1) parsing table generator
└── lalr1_input_string_check.py  # LALR(1) shift-reduce parsing engine
```

---

## Grammar Specification Conventions

| Symbol Type | Notation | Examples |
|---|---|---|
| **Non-Terminals** | Uppercase ASCII letters | `E`, `T`, `F`, `S`, `C` |
| **Terminals** | Lowercase letters & ASCII operators | `a`, `b`, `c`, `d`, `i`, `+`, `*`, `(`, `)` |
| **Epsilon ($\epsilon$)** | Hash character | `#` |
| **Endmarker** | Dollar character | `$` (handled automatically) |
| **Production Format** | `LHS=RHS` or `LHS->RHS` | `E=E+T`, `T=i`, `S=CC` |

> **Note**: Pressing **Enter** at the prompt automatically runs a canonical benchmark grammar for that parser type.

---

## Quick Start

### 1. Interactive Master Menu
Launch the interactive launcher to select and run any algorithm:
```bash
python main_menu.py
```

### 2. Standalone Execution
Every script is completely self-contained with no external dependencies:

```bash
# Compute FIRST & FOLLOW sets
python first_follow.py

# Run LL(1) Parser
python ll1_parser.py

# Run SLR(1) String Parser
python slr1_input_string_check.py

# Run CLR(1) String Parser
python clr1_input_string_check.py

# Run LALR(1) String Parser
python lalr1_input_string_check.py
```

---

## Requirements

- Python 3.8+
- Standard Library only (no third-party dependencies required)
