"""
Compiler Design Practical: CLR(1) Parsing Table Construction.
Simplified Python implementation of CLR1_Parser.c
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


def build_clr1_table(productions):
    non_terminals, terminals = get_symbols(productions)
    all_terms = terminals + ['$']
    goto_nts = [nt for nt in non_terminals if nt != productions[0][0]]
    all_symbols = goto_nts + terminals
    first = compute_first(productions, non_terminals)

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

    action_table = {i: {t: [] for t in all_terms} for i in range(len(states))}
    goto_table = {i: {nt: None for nt in goto_nts} for i in range(len(states))}

    for (s_idx, sym), target in transitions.items():
        if sym in goto_nts:
            goto_table[s_idx][sym] = target
        elif sym in all_terms:
            action_table[s_idx][sym].append(f"s{target}")

    for idx, st in enumerate(states):
        for p_idx, dot, look in st:
            lhs, rhs = productions[p_idx]
            if dot == len(rhs):
                if p_idx == 0:
                    action_table[idx]['$'].append("acc")
                else:
                    r_str = f"r{p_idx}"
                    if r_str not in action_table[idx][look]:
                        action_table[idx][look].append(r_str)

    return states, action_table, goto_table, all_terms, goto_nts


def display_table(states, action_table, goto_table, all_terms, goto_nts):
    w = 8
    act_width = len(all_terms) * w
    goto_width = len(goto_nts) * w
    total_w = 8 + act_width + 3 + goto_width

    print("\nCLR(1) PARSING TABLE:")
    print("=" * total_w)
    header1 = f"{'State':<8}|{'ACTION':^{act_width}}|{'GOTO':^{goto_width}}"
    print(header1)
    act_cols = "".join(f"{t:^{w}}" for t in all_terms)
    goto_cols = "".join(f"{nt:^{w}}" for nt in goto_nts)
    header2 = f"{'':<8}|{act_cols}|{goto_cols}"
    print(header2)
    print("-" * total_w)

    conflict = False
    for i in range(len(states)):
        row_act = ""
        for t in all_terms:
            cell = "/".join(action_table[i][t]) if action_table[i][t] else "-"
            if len(action_table[i][t]) > 1:
                conflict = True
            row_act += f"{cell:^{w}}"

        row_goto = ""
        for nt in goto_nts:
            cell = str(goto_table[i][nt]) if goto_table[i][nt] is not None else "-"
            row_goto += f"{cell:^{w}}"

        print(f"{i:<8}|{row_act}|{row_goto}")

    print("=" * total_w)
    return conflict


def main():
    print("=== CLR(1) PARSING TABLE GENERATOR ===")
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

    print("\nNumbered Productions:")
    for idx, (l, r) in enumerate(productions):
        print(f"  ({idx}) {l} -> {r if r else '#'}")

    states, action_table, goto_table, all_terms, goto_nts = build_clr1_table(productions)
    has_conflict = display_table(states, action_table, goto_table, all_terms, goto_nts)

    if has_conflict:
        print("\nGrammar is NOT CLR(1) due to table conflicts.")
    else:
        print("\nGrammar is CLR(1). No conflicts found.")


if __name__ == "__main__":
    main()

