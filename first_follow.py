"""
Compiler Design Practical: FIRST and FOLLOW computation.
Simplified Python implementation of First_Follow.c
"""

def compute_first(productions, non_terminals):
    first = {nt: set() for nt in non_terminals}
    
    changed = True
    while changed:
        changed = False
        for lhs, rhs in productions:
            before_size = len(first[lhs])
            
            if rhs == '#' or rhs == '':
                first[lhs].add('#')
            else:
                nullable = True
                for char in rhs:
                    if char == '#':
                        first[lhs].add('#')
                        nullable = False
                        break
                    elif not char.isupper():  # Terminal
                        first[lhs].add(char)
                        nullable = False
                        break
                    else:  # Non-terminal
                        first[lhs].update(first[char] - {'#'})
                        if '#' not in first[char]:
                            nullable = False
                            break
                if nullable:
                    first[lhs].add('#')
            
            if len(first[lhs]) > before_size:
                changed = True
                
    return first


def first_of_string(s, first):
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
            res.update(first[char] - {'#'})
            if '#' not in first[char]:
                nullable = False
                break
    if nullable:
        res.add('#')
    return res


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
                    before_size = len(follow[char])
                    beta = rhs[i + 1:]
                    first_beta = first_of_string(beta, first)
                    
                    # Follow(char) gets FIRST(beta) - {#}
                    follow[char].update(first_beta - {'#'})
                    
                    # If beta can derive # (or beta is empty), Follow(char) gets FOLLOW(lhs)
                    if '#' in first_beta or not beta:
                        follow[char].update(follow[lhs])
                        
                    if len(follow[char]) > before_size:
                        changed = True
    return follow


def main():
    print("=== FIRST AND FOLLOW SET COMPUTATION ===")
    user_input = input("Enter number of productions (or press Enter for default example): ").strip()
    
    productions = []
    non_terminals = []
    
    if not user_input:
        # Default classic grammar: E -> TR, R -> +TR | #, T -> FY, Y -> *FY | #, F -> (E) | i
        default_prods = ["E=TR", "R=+TR", "R=#", "T=FY", "Y=*FY", "Y=#", "F=(E)", "F=i"]
        print("Using default grammar:")
        for p in default_prods:
            print("  ", p)
        raw_list = default_prods
    else:
        n = int(user_input)
        print("Enter productions (format A=alpha, use # for epsilon):")
        raw_list = [input(f"P{i+1}: ").strip() for i in range(n)]

    for p in raw_list:
        if '=' in p:
            lhs, rhs = p.split('=', 1)
        elif '->' in p:
            lhs, rhs = p.split('->', 1)
        else:
            lhs, rhs = p[0], p[1:]
        lhs = lhs.strip()
        rhs = rhs.strip()
        productions.append((lhs, rhs))
        if lhs not in non_terminals:
            non_terminals.append(lhs)

    start_symbol = non_terminals[0]
    first = compute_first(productions, non_terminals)
    follow = compute_follow(productions, non_terminals, start_symbol, first)

    print("\nFIRST sets:")
    for nt in non_terminals:
        items = sorted(list(first[nt]))
        print(f"FIRST({nt}) = {{ {', '.join(items)} }}")

    print("\nFOLLOW sets:")
    for nt in non_terminals:
        items = sorted(list(follow[nt]))
        print(f"FOLLOW({nt}) = {{ {', '.join(items)} }}")


if __name__ == "__main__":
    main()

