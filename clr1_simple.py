"""
Compiler Design Practical: CLR(1) Grammar Check.
Simplified Python implementation of CLR1_Simple.c
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


def compute_first(productions, non_terminals):
    first = {nt: set() for nt in non_terminals}
    changed = True
    while changed:
        changed = False
        for lhs, rhs in productions:
            before = len(first[lhs])
            if rhs == '' or rhs == '#':
                first[lhs].add('#')
            else:
                nullable = True
                for ch in rhs:
                    if ch == '#':
                        first[lhs].add('#')
                        nullable = False
                        break
                    elif not ch.isupper():
                        first[lhs].add(ch)
                        nullable = False
                        break
                    else:
                        first[lhs].update(first[ch] - {'#'})
                        if '#' not in first[ch]:
                            nullable = False
                            break
                if nullable:
                    first[lhs].add('#')
            if len(first[lhs]) > before:
                changed = True
    return first


def first_of_string(s, first):
    res = set()
    if not s or s == '#':
        res.add('#')
        return res
    nullable = True
    for ch in s:
        if ch == '#':
            res.add('#')
            nullable = False
            break
        elif not ch.isupper():
            res.add(ch)
            nullable = False
            break
        else:
            res.update(first[ch] - {'#'})
            if '#' not in first[ch]:
                nullable = False
                break
    if nullable:
        res.add('#')
    return res


def clr1_closure(items, productions, first):
    # An item is a tuple: (prod_index, dot_position, lookahead)
    closure_set = set(items)
    changed = True
    while changed:
        changed = False
        new_items = set()
        for p_idx, dot, look in closure_set:
            lhs, rhs = productions[p_idx]
            if dot < len(rhs):
                next_sym = rhs[dot]
                if next_sym.isupper():
                    beta = rhs[dot + 1:]
                    lookaheads = first_of_string(beta + look, first)
                    for i, (p_lhs, p_rhs) in enumerate(productions):
                        if p_lhs == next_sym:
                            for b in lookaheads:
                                if b != '#':
                                    item = (i, 0, b)
                                    if item not in closure_set:
                                        new_items.add(item)
        if new_items:
            closure_set.update(new_items)
            changed = True
    return frozenset(closure_set)


def clr1_goto(items, symbol, productions, first):
    moved = set()
    for p_idx, dot, look in items:
        lhs, rhs = productions[p_idx]
        if dot < len(rhs) and rhs[dot] == symbol:
            moved.add((p_idx, dot + 1, look))
    if not moved:
        return None
    return clr1_closure(moved, productions, first)


def format_item(item, productions):
    p_idx, dot, look = item
    lhs, rhs = productions[p_idx]
    if rhs == '' or rhs == '#':
        return f"[{lhs} -> ., {look}]"
    return f"[{lhs} -> {rhs[:dot]}.{rhs[dot:]}, {look}]"


def main():
    print("=== CLR(1) GRAMMAR CHECK ===")
    user_input = input("Enter number of productions (or press Enter for default example): ").strip()

    if not user_input:
        default_prods = ["S=CC", "C=cC", "C=d"]
        print("Using default grammar:")
        for p in default_prods:
            print("  ", p)
        raw_list = default_prods
    else:
        n = int(user_input)
        print("Enter productions (example S=CC, use # for epsilon):")
        raw_list = [input(f"P{i+1}: ").strip() for i in range(n)]

    user_productions = []
    for p in raw_list:
        lhs, rhs = p.split('=', 1) if '=' in p else (p[0], p[1:])
        lhs = lhs.strip()
        rhs = "" if rhs.strip() == '#' else rhs.strip()
        user_productions.append((lhs, rhs))

    start_symbol = user_productions[0][0]
    aug_start = 'Z'
    productions = [(aug_start, start_symbol)] + user_productions

    non_terminals, terminals = get_symbols(productions)
    all_symbols = [nt for nt in non_terminals if nt != aug_start] + terminals
    first = compute_first(productions, non_terminals)

    # Initial item: [Z -> . S, $]
    initial_items = frozenset([(0, 0, '$')])
    i0 = clr1_closure(initial_items, productions, first)

    states = [i0]
    state_map = {i0: 0}
    transitions = {}

    queue = [i0]
    while queue:
        curr_state = queue.pop(0)
        curr_idx = state_map[curr_state]

        for sym in all_symbols:
            nxt = clr1_goto(curr_state, sym, productions, first)
            if nxt is not None:
                if nxt not in state_map:
                    new_idx = len(states)
                    state_map[nxt] = new_idx
                    states.append(nxt)
                    queue.append(nxt)
                transitions[(curr_idx, sym)] = state_map[nxt]

    print(f"\nCanonical Collection of LR(1) Items ({len(states)} states):")
    for idx, st in enumerate(states):
        print(f"\nState I{idx}:")
        for item in sorted(st):
            print(f"  {format_item(item, productions)}")

    all_terms = terminals + ['$']
    has_conflict = False
    conflict_details = []

    # CLR(1) conflict check:
    # Shift actions are uniquely determined by transitions on terminals.
    # Reduce actions are added for items with dot at end on their specific lookaheads.
    for idx, st in enumerate(states):
        actions = {t: [] for t in all_terms}

        # Shifts
        for t in terminals:
            if (idx, t) in transitions:
                actions[t].append(f"s{transitions[(idx, t)]}")

        # Reduces and Accept
        for p_idx, dot, look in st:
            lhs, rhs = productions[p_idx]
            if dot == len(rhs):
                if p_idx == 0:
                    actions['$'].append("acc")
                else:
                    r_action = f"r{p_idx}"
                    if r_action not in actions[look]:
                        actions[look].append(r_action)

        for t in all_terms:
            if len(actions[t]) > 1:
                has_conflict = True
                conflict_details.append(f"State I{idx} on '{t}': {', '.join(actions[t])}")

    print("\n" + "=" * 40)
    if has_conflict:
        print("Grammar is NOT CLR(1).")
        print("Conflicts found:")
        for cd in conflict_details:
            print(" -", cd)
    else:
        print("Grammar is CLR(1). No conflicts found.")
    print("=" * 40)


if __name__ == "__main__":
    main()
