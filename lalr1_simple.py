"""
Compiler Design Practical: LALR(1) Grammar Check.
Simplified Python implementation of LALR1_Simple.c
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


def get_core(state):
    return frozenset((p, d) for p, d, l in state)


def merge_lr1_states(clr_states, clr_transitions):
    # Group CLR(1) states by identical core
    core_groups = {}
    for idx, st in enumerate(clr_states):
        core = get_core(st)
        if core not in core_groups:
            core_groups[core] = []
        core_groups[core].append(idx)

    lalr_states = []
    state_remap = {}  # old_idx -> new_idx
    merged_state_names = {}

    for new_idx, (core, group) in enumerate(core_groups.items()):
        # Union all items across states with same core
        merged_items = set()
        for old_idx in group:
            state_remap[old_idx] = new_idx
            merged_items.update(clr_states[old_idx])
        lalr_states.append(frozenset(merged_items))
        merged_state_names[new_idx] = "I" + "".join(str(i) for i in group)

    # Remap transitions
    lalr_transitions = {}
    for (old_s, sym), old_target in clr_transitions.items():
        new_s = state_remap[old_s]
        new_target = state_remap[old_target]
        lalr_transitions[(new_s, sym)] = new_target

    return lalr_states, lalr_transitions, merged_state_names, state_remap


def format_grouped_items(state, productions):
    # Group lookaheads for display: [A -> alpha.beta, c/d]
    item_map = {}
    for p_idx, dot, look in state:
        key = (p_idx, dot)
        if key not in item_map:
            item_map[key] = set()
        item_map[key].add(look)

    lines = []
    for (p_idx, dot), looks in sorted(item_map.items()):
        lhs, rhs = productions[p_idx]
        rhs_str = f"{rhs[:dot]}.{rhs[dot:]}" if rhs else "."
        look_str = "/".join(sorted(list(looks)))
        lines.append(f"[{lhs} -> {rhs_str}, {look_str}]")
    return lines


def main():
    print("=== LALR(1) GRAMMAR CHECK ===")
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

    # 1. Build CLR(1) States
    initial_items = frozenset([(0, 0, '$')])
    i0 = clr1_closure(initial_items, productions, first)

    clr_states = [i0]
    clr_state_map = {i0: 0}
    clr_transitions = {}

    queue = [i0]
    while queue:
        curr_state = queue.pop(0)
        curr_idx = clr_state_map[curr_state]

        for sym in all_symbols:
            nxt = clr1_goto(curr_state, sym, productions, first)
            if nxt is not None:
                if nxt not in clr_state_map:
                    new_idx = len(clr_states)
                    clr_state_map[nxt] = new_idx
                    clr_states.append(nxt)
                    queue.append(nxt)
                clr_transitions[(curr_idx, sym)] = clr_state_map[nxt]

    # 2. Merge states with same core into LALR(1) states
    lalr_states, lalr_transitions, merged_names, state_remap = merge_lr1_states(clr_states, clr_transitions)

    print(f"\nMerged {len(clr_states)} CLR(1) states into {len(lalr_states)} LALR(1) states:")
    for idx, st in enumerate(lalr_states):
        print(f"\nState {merged_names[idx]} (Index {idx}):")
        for line in format_grouped_items(st, productions):
            print(f"  {line}")

    all_terms = terminals + ['$']
    has_conflict = False
    conflict_details = []

    # 3. Check for conflicts in merged states
    for idx, st in enumerate(lalr_states):
        actions = {t: [] for t in all_terms}

        for t in terminals:
            if (idx, t) in lalr_transitions:
                actions[t].append(f"s{lalr_transitions[(idx, t)]}")

        for p_idx, dot, look in st:
            lhs, rhs = productions[p_idx]
            if dot == len(rhs):
                if p_idx == 0:
                    actions['$'].append("acc")
                else:
                    r_act = f"r{p_idx}"
                    if r_act not in actions[look]:
                        actions[look].append(r_act)

        for t in all_terms:
            if len(actions[t]) > 1:
                has_conflict = True
                conflict_details.append(f"State {merged_names[idx]} on '{t}': {', '.join(actions[t])}")

    print("\n" + "=" * 40)
    if has_conflict:
        print("Grammar is NOT LALR(1).")
        print("Conflicts found:")
        for cd in conflict_details:
            print(" -", cd)
    else:
        print("Grammar is LALR(1). No conflicts found.")
    print("=" * 40)


if __name__ == "__main__":
    main()

