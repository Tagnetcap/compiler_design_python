"""
Compiler Design Practical: LR(0) Item Generation and Grammar Check.
Simplified Python implementation of LR0_Simple.c
"""

def get_symbols(productions):
    non_terminals = []
    terminals = []
    for lhs, rhs in productions:
        if lhs not in non_terminals:
            non_terminals.append(lhs)
    for lhs, rhs in productions:
        for ch in rhs:
            if ch != '#' and not ch.isupper() and ch not in terminals:
                terminals.append(ch)
    return non_terminals, terminals


def lr0_closure(items, productions):
    # An item is a tuple: (prod_index, dot_position)
    closure_set = set(items)
    changed = True
    while changed:
        changed = False
        new_items = set()
        for p_idx, dot in closure_set:
            lhs, rhs = productions[p_idx]
            if dot < len(rhs):
                next_sym = rhs[dot]
                if next_sym.isupper():
                    # Non-terminal after dot, add B -> . gamma
                    for i, (p_lhs, p_rhs) in enumerate(productions):
                        if p_lhs == next_sym:
                            item = (i, 0)
                            if item not in closure_set:
                                new_items.add(item)
        if new_items:
            closure_set.update(new_items)
            changed = True
    return frozenset(closure_set)


def lr0_goto(items, symbol, productions):
    moved = set()
    for p_idx, dot in items:
        lhs, rhs = productions[p_idx]
        if dot < len(rhs) and rhs[dot] == symbol:
            moved.add((p_idx, dot + 1))
    if not moved:
        return None
    return lr0_closure(moved, productions)


def format_item(item, productions):
    p_idx, dot = item
    lhs, rhs = productions[p_idx]
    if rhs == '' or rhs == '#':
        return f"{lhs} -> ."
    return f"{lhs} -> {rhs[:dot]}.{rhs[dot:]}"


def main():
    print("=== LR(0) GRAMMAR CHECK ===")
    user_input = input("Enter number of productions (or press Enter for default example): ").strip()

    if not user_input:
        default_prods = ["S=aA", "S=b", "A=a"]
        print("Using default grammar:")
        for p in default_prods:
            print("  ", p)
        raw_list = default_prods
    else:
        n = int(user_input)
        print("Enter productions (example S=aA, use # for epsilon):")
        raw_list = [input(f"P{i+1}: ").strip() for i in range(n)]

    # Parse productions (P1 to Pn)
    user_productions = []
    for p in raw_list:
        lhs, rhs = p.split('=', 1) if '=' in p else (p[0], p[1:])
        lhs = lhs.strip()
        rhs = "" if rhs.strip() == '#' else rhs.strip()
        user_productions.append((lhs, rhs))

    # Augmented start symbol: Z -> S
    start_symbol = user_productions[0][0]
    aug_start = 'Z'
    productions = [(aug_start, start_symbol)] + user_productions

    non_terminals, terminals = get_symbols(productions)
    all_symbols = [nt for nt in non_terminals if nt != aug_start] + terminals

    # Build canonical collection of LR(0) items
    initial_item = frozenset([(0, 0)])
    i0 = lr0_closure(initial_item, productions)

    states = [i0]
    state_map = {i0: 0}
    transitions = {}

    queue = [i0]
    while queue:
        curr_state = queue.pop(0)
        curr_idx = state_map[curr_state]

        for sym in all_symbols:
            nxt = lr0_goto(curr_state, sym, productions)
            if nxt is not None:
                if nxt not in state_map:
                    new_idx = len(states)
                    state_map[nxt] = new_idx
                    states.append(nxt)
                    queue.append(nxt)
                transitions[(curr_idx, sym)] = state_map[nxt]

    # Print canonical collection of states
    print(f"\nCanonical Collection of LR(0) Items ({len(states)} states):")
    for idx, st in enumerate(states):
        print(f"\nState I{idx}:")
        for item in sorted(st):
            print(f"  {format_item(item, productions)}")

    # Check for LR(0) conflicts
    all_terms = terminals + ['$']
    has_conflict = False
    conflict_details = []

    for idx, st in enumerate(states):
        actions = {t: [] for t in all_terms}

        # Shift actions from transitions
        for t in terminals:
            if (idx, t) in transitions:
                actions[t].append(f"Shift on '{t}'")

        # Reduce & Accept actions
        for p_idx, dot in st:
            lhs, rhs = productions[p_idx]
            if dot == len(rhs):
                if p_idx == 0:
                    actions['$'].append("Accept")
                else:
                    for t in all_terms:
                        actions[t].append(f"Reduce by {lhs}->{rhs if rhs else '#'}")

        for t in all_terms:
            if len(actions[t]) > 1:
                has_conflict = True
                conflict_details.append(f"State I{idx} on '{t}': {', '.join(actions[t])}")

    print("\n" + "=" * 40)
    if has_conflict:
        print("Grammar is NOT LR(0).")
        print("Conflicts found:")
        for cd in conflict_details:
            print(" -", cd)
    else:
        print("Grammar is LR(0).")
    print("=" * 40)


if __name__ == "__main__":
    main()
