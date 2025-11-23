from utils.constants import DO_RULES, IF_RULES, LOGICAL_OPERATORS, NON_COMPATIBLE_WHEN, NON_COMPATIBLE_DO_WHEN

import random

IF_KEYS = tuple(IF_RULES.keys())
DO_KEYS = tuple(DO_RULES.keys())

BAD_WHEN = {tuple(sorted(pair)) for pair in NON_COMPATIBLE_WHEN}
BAD_DO_WHEN = {tuple(pair) for pair in NON_COMPATIBLE_DO_WHEN}

def generate_ruleset(ruleset_type):
    when_a = random.choice(IF_KEYS)

    if ruleset_type == "advanced":
        valid_b = [
            b for b in IF_KEYS
            if b != when_a and tuple(sorted((when_a, b))) not in BAD_WHEN
        ]

        if not valid_b:
            return [when_a, random.choice(DO_KEYS)]

        when_b = random.choice(valid_b)
        logical = random.choice(LOGICAL_OPERATORS)
    else:
        when_b = None
        logical = None

    if when_b:
        valid_do = [
            d for d in DO_KEYS
            if (when_a, d) not in BAD_DO_WHEN
            and (when_b, d) not in BAD_DO_WHEN
            and (d, when_a) not in BAD_DO_WHEN
            and (d, when_b) not in BAD_DO_WHEN
        ]
    else:
        valid_do = [
            d for d in DO_KEYS
            if (when_a, d) not in BAD_DO_WHEN
            and (d, when_a) not in BAD_DO_WHEN
        ]

    do = random.choice(valid_do)

    if logical:
        return [when_a, logical, when_b, do]
    else:
        return [when_a, do]