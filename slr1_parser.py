"""
Compiler Design Practical: SLR(1) Parsing Table Construction.
Simplified Python implementation of SLR1_Parser.c
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


def build_slr1_table(productions):
    non_terminals, terminals = get_symbols(productions)
    all_terms = terminals + ['$']
    goto_nts = [nt for nt in non_terminals if nt != productions[0][0]]
    all_symbols = goto_nts + terminals

    first = compute_first(productions, non_terminals)
    follow = compute_follow(productions, non_terminals, productions[0][0], first)

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

    action_table = {i: {t: [] for t in all_terms} for i in range(len(states))}
    goto_table = {i: {nt: None for nt in goto_nts} for i in range(len(states))}

    for (s_idx, sym), target in transitions.items():
        if sym in goto_nts:
            goto_table[s_idx][sym] = target
        elif sym in all_terms:
            action_table[s_idx][sym].append(f"s{target}")

    # SLR(1) reduction: reduce ONLY in FOLLOW(lhs)
    for idx, st in enumerate(states):
        for p_idx, dot in st:
            lhs, rhs = productions[p_idx]
            if dot == len(rhs):
                if p_idx == 0:
                    action_table[idx]['$'].append("acc")
                else:
                    r_str = f"r{p_idx}"
                    for t in follow[lhs]:
                        if t in all_terms and r_str not in action_table[idx][t]:
                            action_table[idx][t].append(r_str)

    return states, action_table, goto_table, all_terms, goto_nts, follow


def display_table(states, action_table, goto_table, all_terms, goto_nts):
    w = 8
    act_width = len(all_terms) * w
    goto_width = len(goto_nts) * w
    total_w = 8 + act_width + 3 + goto_width

    print("\nSLR(1) PARSING TABLE:")
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
    print("=== SLR(1) PARSING TABLE GENERATOR ===")
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

    print("\nNumbered Productions:")
    for idx, (l, r) in enumerate(productions):
        print(f"  ({idx}) {l} -> {r if r else '#'}")

    states, action_table, goto_table, all_terms, goto_nts, follow = build_slr1_table(productions)

    print("\nFOLLOW sets used for SLR(1) reductions:")
    for nt in goto_nts:
        print(f"  FOLLOW({nt}) = {{ {', '.join(sorted(list(follow[nt])))} }}")

    has_conflict = display_table(states, action_table, goto_table, all_terms, goto_nts)

    if has_conflict:
        print("\nGrammar is NOT SLR(1) due to table conflicts.")
    else:
        print("\nGrammar is SLR(1). No conflicts found.")


if __name__ == "__main__":
    main()

