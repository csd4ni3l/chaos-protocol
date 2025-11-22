from utils.constants import DO_RULES, IF_RULES, LOGICAL_OPERATORS, NON_COMPATIBLE_WHEN, NON_COMPATIBLE_DO_WHEN

import random

def generate_rule():
    when_a = random.choice(list(IF_RULES.keys()))
    when_b = None

    if random.random() < 0.5:
        when_b = random.choice(list(IF_RULES.keys()))
        while (when_a, when_b) in NON_COMPATIBLE_WHEN or (when_b, when_a) in NON_COMPATIBLE_WHEN or when_a == when_b:
            when_a = random.choice(list(IF_RULES.keys()))
            when_b = random.choice(list(IF_RULES.keys()))            

        logical_operation = random.choice(LOGICAL_OPERATORS)
    else:
        logical_operation = None

    do = random.choice(list(DO_RULES.keys()))
    while (when_a, do) in NON_COMPATIBLE_DO_WHEN or (do, when_a) in NON_COMPATIBLE_DO_WHEN or (when_b, do) in NON_COMPATIBLE_DO_WHEN or (do, when_b) in NON_COMPATIBLE_DO_WHEN:
        do = random.choice(list(DO_RULES.keys()))

    if logical_operation:
        return [IF_RULES[when_a], logical_operation, IF_RULES[when_b], DO_RULES[do]]
    else:
        return [IF_RULES[when_a], DO_RULES[do]]
    
def generate_rules(n):
    return [generate_rule() for _ in range(n)]