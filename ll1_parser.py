"""
Compiler Design Practical: LL(1) Parser.
Simplified Python implementation of LL1_Parser.c
"""

def first_of_string(s, first_sets):
    res = set()
    if not s or s == '#':
        res.add('#')
        return res

    nullable = True
    for char in s:
        if char == '#':
            res.add('#')
            nullable = False
            break
        elif not char.isupper():
            res.add(char)
            nullable = False
            break
        else:
            res.update(first_sets[char] - {'#'})
            if '#' not in first_sets[char]:
                nullable = False
                break
    if nullable:
        res.add('#')
    return res


def compute_first(productions, non_terminals):
    first = {nt: set() for nt in non_terminals}
    changed = True
    while changed:
        changed = False
        for lhs, rhs in productions:
            before = len(first[lhs])
            first[lhs].update(first_of_string(rhs, first))
            if len(first[lhs]) > before:
                changed = True
    return first


def compute_follow(productions, non_terminals, start_symbol, first):
    follow = {nt: set() for nt in non_terminals}
    follow[start_symbol].add('$')
    
    changed = True
    while changed:
        changed = False
        for lhs, rhs in productions:
            if rhs == '#':
                continue
            for i, char in enumerate(rhs):
                if char.isupper():
                    before = len(follow[char])
                    beta = rhs[i + 1:]
                    first_beta = first_of_string(beta, first)
                    
                    follow[char].update(first_beta - {'#'})
                    if '#' in first_beta or not beta:
                        follow[char].update(follow[lhs])
                    if len(follow[char]) > before:
                        changed = True
    return follow


def construct_table(productions, non_terminals, terminals, first, follow):
    table = {nt: {t: [] for t in terminals} for nt in non_terminals}
    
    for lhs, rhs in productions:
        first_rhs = first_of_string(rhs, first)
        
        for t in first_rhs:
            if t != '#' and t in terminals:
                table[lhs][t].append(f"{lhs}={rhs}")
                
        if '#' in first_rhs:
            for f in follow[lhs]:
                if f in terminals:
                    prod_str = f"{lhs}={rhs}"
                    if prod_str not in table[lhs][f]:
                        table[lhs][f].append(prod_str)
                        
    return table


def display_table(table, non_terminals, terminals):
    col_width = 14
    header = f"{'NT':<8}" + "".join(f"{t:<{col_width}}" for t in terminals)
    print("\nLL(1) PARSING TABLE:")
    print("-" * len(header))
    print(header)
    print("-" * len(header))
    
    for nt in non_terminals:
        row = f"{nt:<8}"
        for t in terminals:
            entries = table[nt][t]
            if len(entries) == 0:
                cell = "-"
            elif len(entries) > 1:
                cell = "CONFLICT"
            else:
                cell = entries[0]
            row += f"{cell:<{col_width}}"
        print(row)
    print("-" * len(header))


def parse_string(input_str, start_symbol, table, terminals):
    stack = ['$', start_symbol]
    if input_str == '#' or input_str == '':
        tokens = ['$']
    else:
        tokens = list(input_str) + ['$']
        
    ip = 0
    print(f"\n{'STEP':<6}{'STACK':<25}{'INPUT':<20}{'ACTION'}")
    print("-" * 65)
    
    step = 1
    while len(stack) > 0:
        top = stack[-1]
        curr_token = tokens[ip] if ip < len(tokens) else '$'
        
        stack_str = "".join(stack)
        input_str_rem = "".join(tokens[ip:])
        
        if top == '$' and curr_token == '$':
            print(f"{step:<6}{stack_str:<25}{input_str_rem:<20}ACCEPT")
            print("\nString Accepted!")
            return True
            
        if not top.isupper():  # Terminal on stack
            if top == curr_token:
                stack.pop()
                ip += 1
                print(f"{step:<6}{stack_str:<25}{input_str_rem:<20}Match {curr_token}")
            else:
                print(f"{step:<6}{stack_str:<25}{input_str_rem:<20}REJECT (Mismatch)")
                print("\nString Rejected.")
                return False
        else:  # Non-terminal on stack
            if curr_token not in terminals or len(table[top][curr_token]) == 0:
                print(f"{step:<6}{stack_str:<25}{input_str_rem:<20}REJECT (No rule in table)")
                print("\nString Rejected.")
                return False
                
            entries = table[top][curr_token]
            if len(entries) > 1:
                print(f"{step:<6}{stack_str:<25}{input_str_rem:<20}REJECT (Conflict)")
                print("\nString Rejected.")
                return False
                
            prod = entries[0]
            lhs, rhs = prod.split('=', 1)
            stack.pop()
            if rhs != '#':
                for char in reversed(rhs):
                    stack.append(char)
            print(f"{step:<6}{stack_str:<25}{input_str_rem:<20}Apply {prod}")
            
        step += 1
        
    print(f"{step:<6}{stack_str:<25}{input_str_rem:<20}REJECT")
    print("\nString Rejected.")
    return False


def main():
    print("=== LL(1) PARSER ===")
    user_input = input("Enter number of productions (or press Enter for default example): ").strip()
    
    productions = []
    non_terminals = []
    
    if not user_input:
        default_prods = ["E=TR", "R=+TR", "R=#", "T=FY", "Y=*FY", "Y=#", "F=(E)", "F=i"]
        print("Using default grammar:")
        for p in default_prods:
            print("  ", p)
        raw_list = default_prods
    else:
        n = int(user_input)
        print("Enter productions (example S=AB, use # for epsilon):")
        raw_list = [input(f"P{i+1}: ").strip() for i in range(n)]

    terminals_set = set()
    for p in raw_list:
        lhs, rhs = p.split('=', 1) if '=' in p else (p[0], p[1:])
        lhs = lhs.strip()
        rhs = rhs.strip()
        productions.append((lhs, rhs))
        if lhs not in non_terminals:
            non_terminals.append(lhs)
        for char in rhs:
            if not char.isupper() and char != '#':
                terminals_set.add(char)
                
    terminals = sorted(list(terminals_set)) + ['$']
    start_symbol = non_terminals[0]

    first = compute_first(productions, non_terminals)
    follow = compute_follow(productions, non_terminals, start_symbol, first)
    table = construct_table(productions, non_terminals, terminals, first, follow)

    display_table(table, non_terminals, terminals)

    # Check for conflicts
    conflict = False
    for nt in non_terminals:
        for t in terminals:
            if len(table[nt][t]) > 1:
                conflict = True
                break

    if conflict:
        print("\nGrammar is NOT LL(1) (Contains table conflicts).")
        return

    print("\nGrammar is LL(1).")

    inp = input("\nEnter input string to parse (e.g., i+i*i or # for empty, or press Enter for 'i+i*i'): ").strip()
    if not inp:
        inp = "i+i*i"
        print(f"Using default input string: {inp}")

    parse_string(inp, start_symbol, table, terminals)


if __name__ == "__main__":
    main()

