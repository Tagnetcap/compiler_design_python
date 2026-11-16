"""
Compiler Design Practical: LALR(1) Parser with Input String Check.
Simplified Python implementation of LALR1_Input_string_check.c
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
    core_groups = {}
    for idx, st in enumerate(clr_states):
        core = get_core(st)
        if core not in core_groups:
            core_groups[core] = []
        core_groups[core].append(idx)

    lalr_states = []
    state_remap = {}
    merged_state_names = {}

    for new_idx, (core, group) in enumerate(core_groups.items()):
        merged_items = set()
        for old_idx in group:
            state_remap[old_idx] = new_idx
            merged_items.update(clr_states[old_idx])
        lalr_states.append(frozenset(merged_items))
        merged_state_names[new_idx] = "I" + "".join(str(i) for i in group)

    lalr_transitions = {}
    for (old_s, sym), old_target in clr_transitions.items():
        new_s = state_remap[old_s]
        new_target = state_remap[old_target]
        lalr_transitions[(new_s, sym)] = new_target

    return lalr_states, lalr_transitions, merged_state_names, state_remap


def build_lalr1_table(productions):
    non_terminals, terminals = get_symbols(productions)
    all_terms = terminals + ['$']
    goto_nts = [nt for nt in non_terminals if nt != productions[0][0]]
    all_symbols = goto_nts + terminals
    first = compute_first(productions, non_terminals)

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

    lalr_states, lalr_transitions, merged_names, state_remap = merge_lr1_states(clr_states, clr_transitions)

    action_table = {i: {t: [] for t in all_terms} for i in range(len(lalr_states))}
    goto_table = {i: {nt: None for nt in goto_nts} for i in range(len(lalr_states))}

    for (s_idx, sym), target in lalr_transitions.items():
        if sym in goto_nts:
            goto_table[s_idx][sym] = target
        elif sym in all_terms:
            action_table[s_idx][sym].append(f"s{target}")

    for idx, st in enumerate(lalr_states):
        for p_idx, dot, look in st:
            lhs, rhs = productions[p_idx]
            if dot == len(rhs):
                if p_idx == 0:
                    action_table[idx]['$'].append("acc")
                else:
                    r_str = f"r{p_idx}"
                    if r_str not in action_table[idx][look]:
                        action_table[idx][look].append(r_str)

    return lalr_states, action_table, goto_table, all_terms, goto_nts, merged_names


def display_table(states, action_table, goto_table, all_terms, goto_nts, merged_names):
    w = 8
    act_width = len(all_terms) * w
    goto_width = len(goto_nts) * w
    total_w = 12 + act_width + 3 + goto_width

    print("\nLALR(1) PARSING TABLE:")
    print("=" * total_w)
    header1 = f"{'State':<12}|{'ACTION':^{act_width}}|{'GOTO':^{goto_width}}"
    print(header1)
    act_cols = "".join(f"{t:^{w}}" for t in all_terms)
    goto_cols = "".join(f"{nt:^{w}}" for nt in goto_nts)
    header2 = f"{'':<12}|{act_cols}|{goto_cols}"
    print(header2)
    print("-" * total_w)

    conflict = False
    for i in range(len(states)):
        st_label = f"{i} ({merged_names[i]})"
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

        print(f"{st_label:<12}|{row_act}|{row_goto}")

    print("=" * total_w)
    return conflict


def parse_string(input_str, productions, action_table, goto_table, all_terms):
    tokens = list(input_str)
    if not tokens or tokens[-1] != '$':
        tokens.append('$')

    state_stack = [0]
    symbol_stack = ['$']
    ip = 0

    print(f"\n{'STEP':<6}{'STATE STACK':<20}{'SYMBOL STACK':<15}{'INPUT':<15}{'ACTION'}")
    print("-" * 75)

    step = 1
    max_steps = 100
    while step < max_steps:
        curr_state = state_stack[-1]
        a = tokens[ip]

        if a not in all_terms:
            print(f"{step:<6}{str(state_stack):<20}{''.join(symbol_stack):<15}{''.join(tokens[ip:]):<15}REJECT (Unknown symbol)")
            print("\nString Rejected.")
            return False

        actions = action_table[curr_state][a]
        if not actions:
            print(f"{step:<6}{str(state_stack):<20}{''.join(symbol_stack):<15}{''.join(tokens[ip:]):<15}REJECT (No action)")
            print("\nString Rejected.")
            return False

        act = actions[0]
        state_str = " ".join(str(s) for s in state_stack)
        sym_str = "".join(symbol_stack)
        inp_str = "".join(tokens[ip:])

        if act == "acc":
            print(f"{step:<6}{state_str:<20}{sym_str:<15}{inp_str:<15}ACCEPT")
            print("\nString Accepted!")
            return True

        elif act.startswith('s'):
            target_state = int(act[1:])
            print(f"{step:<6}{state_str:<20}{sym_str:<15}{inp_str:<15}Shift {target_state}")
            state_stack.append(target_state)
            symbol_stack.append(a)
            ip += 1

        elif act.startswith('r'):
            p_idx = int(act[1:])
            lhs, rhs = productions[p_idx]
            prod_disp = f"{lhs}->{rhs if rhs else '#'}"
            print(f"{step:<6}{state_str:<20}{sym_str:<15}{inp_str:<15}Reduce by {prod_disp}")

            pop_len = len(rhs)
            for _ in range(pop_len):
                state_stack.pop()
                symbol_stack.pop()

            top_state = state_stack[-1]
            goto_state = goto_table[top_state][lhs]
            if goto_state is None:
                print("\nString Rejected (Invalid GOTO).")
                return False

            symbol_stack.append(lhs)
            state_stack.append(goto_state)

        step += 1

    print("\nParsing stopped: exceeded step limit.")
    return False


def main():
    print("=== LALR(1) INPUT STRING PARSER ===")
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

    states, action_table, goto_table, all_terms, goto_nts, merged_names = build_lalr1_table(productions)
    has_conflict = display_table(states, action_table, goto_table, all_terms, goto_nts, merged_names)

    if has_conflict:
        print("\nGrammar is NOT LALR(1). Cannot parse using LALR(1) table.")
        return

    print("\nGrammar is LALR(1).")
    inp = input("\nEnter input string to check (e.g. cdd, or press Enter for 'cdd'): ").strip()
    if not inp:
        inp = "cdd"
        print(f"Using default input: {inp}")

    parse_string(inp, productions, action_table, goto_table, all_terms)


if __name__ == "__main__":
    main()

