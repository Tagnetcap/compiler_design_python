"""
Compiler Design Practicals - Master Launcher
Run any practical easily from this interactive menu.
"""
import subprocess
import sys
import os

SCRIPTS = [
    ("1",  "FIRST and FOLLOW Set Computation",            "first_follow.py"),
    ("2",  "LL(1) Parser (Table & String Parse)",          "ll1_parser.py"),
    ("3",  "LR(0) Simple Grammar Check",                  "lr0_simple.py"),
    ("4",  "LR(0) Parsing Table Generator",               "lr0_parser.py"),
    ("5",  "LR(0) Parser with Input String Check",        "lr0_input_string_check.py"),
    ("6",  "SLR(1) Simple Grammar Check",                 "slr1_simple.py"),
    ("7",  "SLR(1) Parsing Table Generator",              "slr1_parser.py"),
    ("8",  "SLR(1) Parser with Input String Check",       "slr1_input_string_check.py"),
    ("9",  "CLR(1) Simple Grammar Check",                 "clr1_simple.py"),
    ("10", "CLR(1) Parsing Table Generator",              "clr1_parser.py"),
    ("11", "CLR(1) Parser with Input String Check",       "clr1_input_string_check.py"),
    ("12", "LALR(1) Simple Grammar Check",                "lalr1_simple.py"),
    ("13", "LALR(1) Parsing Table Generator",             "lalr1_parser.py"),
    ("14", "LALR(1) Parser with Input String Check",      "lalr1_input_string_check.py"),
]

def main():
    while True:
        print("\n" + "=" * 55)
        print("    COMPILER DESIGN PRACTICALS (PYTHON SUITE)    ")
        print("=" * 55)
        for num, desc, file in SCRIPTS:
            print(f" [{num:>2}] {desc:<40} ({file})")
        print(" [ 0] Exit")
        print("=" * 55)

        choice = input("Select practical number to run: ").strip()
        if choice in ("0", "exit", "q"):
            print("Exiting. Good luck with your practicals!")
            break

        selected = next((s for s in SCRIPTS if s[0] == choice), None)
        if selected:
            script_file = selected[2]
            print(f"\n--- Running {selected[1]} ({script_file}) ---\n")
            script_path = os.path.join(os.path.dirname(__file__), script_file)
            subprocess.run([sys.executable, script_path])
        else:
            print("Invalid choice! Please select a valid number from the menu.")

if __name__ == "__main__":
    main()

