# Compiler Design Practicals (Python Edition)

This directory contains simplified, easy-to-read, and beginner-friendly Python implementations of all 14 C practical programs from your Compiler Design lab.

---

## 📁 Directory Structure & Mapping

| # | Practical Name | Python Script | Original C File |
|---|----------------|---------------|-----------------|
| 1 | **FIRST & FOLLOW Computation** | `first_follow.py` | `First_Follow.c` |
| 2 | **LL(1) Parser** | `ll1_parser.py` | `LL1_Parser.c` |
| 3 | **LR(0) Simple Check** | `lr0_simple.py` | `LR0_Simple.c` |
| 4 | **LR(0) Parsing Table** | `lr0_parser.py` | `LR0_Parser.c` |
| 5 | **LR(0) Input String Check** | `lr0_input_string_check.py` | `LR0_Input_string_check.c` |
| 6 | **SLR(1) Simple Check** | `slr1_simple.py` | `SLR1_Simple.c` |
| 7 | **SLR(1) Parsing Table** | `slr1_parser.py` | `SLR1_Parser.c` |
| 8 | **SLR(1) Input String Check** | `slr1_input_string_check.py` | `SLR1_Input_string_check.c` |
| 9 | **CLR(1) Simple Check** | `clr1_simple.py` | `CLR1_Simple.c` |
| 10 | **CLR(1) Parsing Table** | `clr1_parser.py` | `CLR1_Parser.c` |
| 11 | **CLR(1) Input String Check** | `clr1_input_string_check.py` | `CLR1_Input_string_check.c` |
| 12 | **LALR(1) Simple Check** | `lalr1_simple.py` | `LALR1_Simple.c` |
| 13 | **LALR(1) Parsing Table** | `lalr1_parser.py` | `LALR1_Parser.c` |
| 14 | **LALR(1) Input String Check** | `lalr1_input_string_check.py` | `LALR1_Input_string_check.c` |
| - | **Interactive Master Menu** | `main_menu.py` | - |

---

## ⚡ Key Improvements & Simplifications Over the Original C Code

1. **No Static Memory / Buffer Overflow Limits**:
   - Replaced fixed `char[20][20]` arrays with dynamic Python lists and sets.
2. **Built-in Set Operations**:
   - Replaced manual `strchr` / loop union helpers with native Python `set()`, `update()`, and `- {'#'}` operations.
3. **No Pointers or Manual String Slicing**:
   - String slices like `rhs[dot:]` and `rhs[:dot] + '.' + rhs[dot:]` make item visualization immediate and readable.
4. **Clean Tabular Formats**:
   - Parsing tables and stack parsing traces are printed with aligned columns using Python f-strings.
5. **Zero-Configuration Quick Test**:
   - Every script allows you to simply press **Enter** to load a standard textbook grammar and test string automatically, avoiding typos during viva exams.

---

## 🚀 How to Run

### Option 1: Using the Master Menu
```bash
python main_menu.py
```
This lets you pick any practical by number from 1 to 14.

### Option 2: Running Individual Practicals
```bash
python first_follow.py
python ll1_parser.py
python lr0_input_string_check.py
python slr1_input_string_check.py
python clr1_input_string_check.py
python lalr1_input_string_check.py
```

---

## 📝 Input Conventions
- **Non-terminals**: Capital letters (`A`-`Z`).
- **Terminals**: Lowercase letters or symbols (e.g. `a`, `b`, `c`, `d`, `i`, `+`, `*`, `(`, `)`).
- **Epsilon**: Represented by `#`.
- **Endmarker**: Automatically handled as `$`.

