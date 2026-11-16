"""
Compiler Design Practical: SLR(1) Grammar Check.
Simplified Python implementation of SLR1_Simple.c
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


def compute_follow(productions, non_terminals, start_symbol, first):
    follow = {nt: set() for nt in non_terminals}
    follow[start_symbol].add('$')
    changed = True
    while changed:
        changed = False
        for lhs, rhs in productions:
            if rhs == '#' or rhs == '':
                continue
            for i, ch in enumerate(rhs):
                if ch.isupper():
                    before = len(follow[ch])
                    beta = rhs[i + 1:]
                    f_beta = first_of_string(beta, first)
                    follow[ch].update(f_beta - {'#'})
                    if '#' in f_beta or not beta:
                        follow[ch].update(follow[lhs])
                    if len(follow[ch]) > before:
                        changed = True
    return follow


def lr0_closure(items, productions):
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
    print("=== SLR(1) GRAMMAR CHECK ===")
    user_input = input("Enter number of productions (or press Enter for default example): ").strip()

    if not user_input:
        default_prods = ["E=E+T", "E=T", "T=i"]
        print("Using default grammar:")
        for p in default_prods:
            print("  ", p)
        raw_list = default_prods
    else:
        n = int(user_input)
        print("Enter productions (example E=E+T, use # for epsilon):")
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
    follow = compute_follow(productions, non_terminals, aug_start, first)

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

    print(f"\nCanonical Collection of Items ({len(states)} states):")
    for idx, st in enumerate(states):
        print(f"\nState I{idx}:")
        for item in sorted(st):
            print(f"  {format_item(item, productions)}")

    all_terms = terminals + ['$']
    has_conflict = False
    conflict_details = []

    # SLR(1) Conflict check: reduce actions apply ONLY on FOLLOW(A)
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
                    for t in follow[lhs]:
                        if t in all_terms:
                            actions[t].append(f"Reduce by {lhs}->{rhs if rhs else '#'}")

        for t in all_terms:
            if len(actions[t]) > 1:
                has_conflict = True
                conflict_details.append(f"State I{idx} on '{t}': {', '.join(actions[t])}")

    print("\n" + "=" * 40)
    if has_conflict:
        print("Grammar is NOT SLR(1).")
        print("Conflicts found:")
        for cd in conflict_details:
            print(" -", cd)
    else:
        print("Grammar is SLR(1).")
    print("=" * 40)


if __name__ == "__main__":
    main()
