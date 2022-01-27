"""
Given the 21 pairwise sums of 7 numbers in arbitrary order, find the 7 numbers
"""

import math
import sys

from fractions import Fraction
from numbers   import Rational
from typing    import List, Optional


_a, _b, _c, _d, _e, _f, _g = range(7)

def debug(x):
    pass


class UnderconstrainedError(Exception):
    def __init__(self, sol1, sol2):
        self.sol1 = sol1
        self.sol2 = sol2

    def __str__(self):
        return f"""Multiple solutions exist:
                   solution 1: {self.sol1}
                   solution 2: {self.sol2}"""


def check(x, solutions, *indices):
    """
    if solutions is not None, check that x = sum([solutions[i] for i in indices])
    @return x
    """
    if solutions is not None:
        correct = sum([solutions[i] for i in indices])
        assert x == correct, f"incorrect step: computed {'+'.join(str(solutions[i]) for i in indices)} == {x} != expected {correct}"

    return x


def solve(k : int, sums : List[int], nums : Optional[List[int]] = None):
    """
    Given the pairwise sums of k numbers in unknown order, try to compute the
    original numbers

    @param sums: the pairwise sums
    @param nums: if present, the original numbers (used for testing)
    @return the original numbers, sorted from smallest to largest

    @raise AssertionError if nums is given and one of the calculations is incorrect
    @raise UnderconstrainedError if there are multiple solutions
    """
    solutions = [
        solve0,
        solve1,
        solve2,
        solve3,
        solve4,
        solve5,
        solve6,
        solve7_alt,
    ]
    if k > 7:
        raise NotImplemented()

    n = math.comb(k,2)
    if len(sums) != n:
        raise ValueError(f"expected {n} sums, found {len(sums)}")
    if nums != None and len(nums) != k:
        raise ValueError(f"expected {k} numbers, found {len(nums)}")

    sums.sort()
    if nums is not None:
        nums.sort()

    return solutions[k](sums,nums)


def solve0(sums, nums = None):
    """@see solve()"""
    return []


def solve1(sums, nums = None):
    """@see solve()"""
    raise UnderconstrainedError([0], [1])


def solve2(sums, nums = None):
    """@see solve()"""
    raise UnderconstrainedError([0, sums[0]], [1, sums[0] - 1])


def solve3(sums, nums = None):
    """@see solve()"""
    ab = check(sums[0], nums, _a, _b)
    ac = check(sums[1], nums, _a, _c)
    bc = check(sums[2], nums, _b, _c)

    a = check((ab + ac - bc)//2, nums, _a)
    b = check((ab + bc - ac)//2, nums, _b)
    c = check((ac + bc - ab)//2, nums, _c)
    return [a,b,c]


def solve4(sums, nums = None):
    """@see solve()"""
    ab = check(sums[0], nums, _a, _b)
    ac = check(sums[1], nums, _a, _c)
    cd = check(sums[5], nums, _c, _d)
    bd = check(sums[4], nums, _b, _d)

    def solve(bc, ad):
        a,b,c = solve3([ab, bc, ac])
        d = (ad - a)
        return [a,b,c,d]

    sol1 = solve(sums[2],sums[3])
    sol2 = solve(sums[3],sums[2])

    assert sol1 != sol2

    raise UnderconstrainedError(sol1, sol2)


def solve5(sums, nums = None):
    """@see solve()"""
    ab = check(sums[0],   nums, _a, _b)
    ac = check(sums[1],   nums, _a, _c)
    de = check(sums[-1],  nums, _d, _e)
    ce = check(sums[-2],  nums, _c, _e)
    abcde = check(sum(sums)//4,  nums, _a, _b, _c, _d, _e)
    bd = check(2*abcde - (ab + ac + ce + de), nums, _b, _d)
    e = check(abcde - bd - ac, nums, _e)
    d = check(de - e, nums, _d)
    c = check(ce - e, nums, _c)
    a = check(abcde - bd - ce, nums, _a)
    b = check(ab - a, nums, _b)
    return [a,b,c,d,e]


def normalize(sums, nums):
    """
    Translate and scale sums so that sums[0] == 0 and sums[1] == 1
    If nums is not None, also translate and scale nums

    @return normalized sums, normalized nums, translation, scale
    """
    translation = sums[0]
    sums = [x - translation for x in sums]
    if nums is not None:
        nums = [x - Fraction(translation,2) for x in nums]

    scale = Fraction(1,sums[1])
    sums = [x * scale for x in sums]
    if nums is not None:
        nums = [x * scale for x in nums]

    return sums, nums, translation, scale


def unnormalize(nums, translation, scale):
    return [int(x/scale + Fraction(translation,2)) for x in nums]


def solve6(sums, nums = None):
    """@see solve()"""

    ab = check(sums[0],  nums, _a, _b)
    ac = check(sums[1],  nums, _a, _c)
    ef = check(sums[-1], nums, _e, _f)
    df = check(sums[-2], nums, _d, _f)
    
    abcdef = check(sum(sums)//5, nums, _a, _b, _c, _d, _e, _f)

    af = check((ab + ac + ef + df - abcdef), nums, _a, _f)

    bd = check(ab + df - af, nums, _b, _d)
    be = check(ab + ef - af, nums, _b, _e)
    ce = check(ac + ef - af, nums, _c, _e)
    cd = check(ac + df - af, nums, _c, _d)

    #*ab  *ac   ad   ae  *af
    #      bc  *bd  *be   bf
    #          *cd  *ce   cf
    #                de  *df
    #                    *ef

    for x in [ab, ac, af, bd, be, cd, ce, df, ef]:
        sums.remove(x)

    # sums[:3] is {bc, ad, ae}
    aabcde = check(sum(sums[:3]), nums, _a, _a, _b, _c, _d, _e)
    a = check((aabcde - abcdef + af)//2, nums, _a)
    b = check(ab - a, nums, _b)
    c = check(ac - a, nums, _c)
    d = check(bd - b, nums, _d)
    e = check(be - b, nums, _e)
    f = check(af - a, nums, _f)

    return [a,b,c,d,e,f]


def solve7(sums, nums = None):
    """@see solve()"""
    ab = check(sums[0],  nums, _a, _b)
    ac = check(sums[1],  nums, _a, _c)
    fg = check(sums[-1], nums, _f, _g)
    eg = check(sums[-2], nums, _e, _g)

    # ab   ac   ad   ae   af   ag
    #      bc   bd   be   bf   bg
    #           cd   ce   cf   cg
    #                de   df   dg
    #                     ef   eg
    #                          fg

    # find candidates for ag:
    #   - bf + ag = ab + fg
    #   - ce + ag = ac + eg
    #   - be + ag = ab + eg
    #   - cf + ag = ac + fg
    #   - i_ag ∈ [5,15]

    candidates1 = []
    for ag in sums[5:16]:
        bf = ab + fg - ag
        ce = ac + eg - ag
        be = ab + eg - ag
        cf = ac + fg - ag
        candidate = (ag,be,bf,ce,cf)

        # check that ag is a reasonable candidate
        sumdup = [x for x in sums]
        if not (be <= bf <= cf and be <= ce <= cf):
            continue
        try:
            for entry in candidate:
                sumdup.remove(entry)
        except:
            continue

        if candidate not in candidates1:
            candidates1.append(candidate)

    # print duplicate candidates
    if len(candidates1) != 1:
        debug(f"nums: {nums}")
        debug(f"unexpected number of ag candidates: {candidates1}")
        debug('')

    candidates2 = []
    for ae in sums[3:7]:
        cg = ac + eg - ae
        af = ac + fg - cg
        bg = ab + fg - af
        candidate = (ae,af,bg,cg)

        # check that ae is a reasonable candidate
        sumdup = [x for x in sums]
        if not (ae <= af <= bg <= cg):
            continue
        try:
            for entry in candidate:
                sumdup.remove(entry)
        except:
            continue

        if candidate not in candidates2:
            candidates2.append(candidate)

    # print duplicate candidates
    if len(candidates2) != 1:
        debug(f"nums: {nums}")
        debug(f"unexpected number of ae candidates: {candidates2}")
        debug('')

    abcdefg = check(sum(sums)//6, nums, _a, _b, _c, _d, _e, _f, _g)

    def compute(set1, set2):
        ag, be, bf, ce, cf = set1
        ae, af, bg, cg     = set2
        filtered = list(sums)
        known = [ae, af, ag, be, bf, bg, ce, cf, cg]
        debug(f'known values: {known}')
        for x in known:
            filtered.remove(x)
        debug(len(filtered))
        abcd = sum(filtered[0:6])//3

        d = abcdefg - ag - bf - ce
        a = ab + ac + d - abcd
        b = ab - a
        c = ac - a

        defg = sum(filtered[6:12])//3
        g = fg + eg + d - defg
        e = eg - g
        f = fg - g
        computed = compute_sums([a,b,c,d,e,f,g])
        computed.sort()
        assert sums == computed
        return [a,b,c,d,e,f,g]

    candidates = []
    for set1 in candidates1:
        for set2 in candidates2:
            try:
                candidate = compute(set1, set2)
                if candidate not in candidates:
                    candidates.append(candidate)
            except:
                continue

    if len(candidates) != 1:
        print(f"nums: {nums}")
        print(f"unexpected number of final candidates: {candidates}")
        print()

    return candidates[0]

def solve7_alt(sums, nums = None):
    """@see solve()"""
    ab = check(sums[0],  nums, _a, _b)
    ac = check(sums[1],  nums, _a, _c)
    fg = check(sums[-1], nums, _f, _g)
    eg = check(sums[-2], nums, _e, _g)

    abcdefg = check(sum(sums)//6, nums, _a, _b, _c, _d, _e, _f, _g)

    # ab   ac   ad   ae   af   ag
    #      bc   bd   be   bf   bg
    #           cd   ce   cf   cg
    #                de   df   dg
    #                     ef   eg
    #                          fg

    def compute(bc):
        a,b,c = solve3([ab,ac,bc])
        ad = sums[2] if sums[2] != bc else sums[3]
        d = ad - a
        e = abcdefg - a - b - c - d - fg
        g = eg - e
        f = fg - g
        if not (a <= b <= c <= d <= e <= f <= g):
            return (0,)
        return (a,b,c,d,e,f,g)

    candidates = set()
    for bc in sums[2:7]:
        candidate  = compute(bc)
        recomputed = compute_sums(candidate)
        recomputed.sort()
        if recomputed == sums:
            candidates.add(candidate)

    if len(candidates) != 1:
        print(f"wrong number of candidates")
        print(f"  nums: {nums}")
        print(f"  candidates: {candidates}")

    return list(candidates.pop())


def summarize_diffs(sums):
    """
    Calculate and group all the pairwise differences of the sums
    """

    diffs = [(sums[0] + sums[j] - sums[j])//2 for i in range(len(sums)) for j in range(i) for k in range(j)]
    results = {}
    for d in diffs:
        results[d] = results.get(d,0) + 1

    output = list(results.items())
    output.sort(key=lambda p: -p[1])
    debug(output[:10])

def compute_sums(nums):
    return [nums[i] + nums[j] for i in range(len(nums)) for j in range(i)]


if __name__ == '__main__':

    k = int(sys.argv[1]) if len(sys.argv) > 1 else 7

    import random
    for i in range(100000):
        inputs = [random.randint(-1000,1000) for i in range(k)]
        inputs.sort()
        debug(f"original numbers: {inputs}")

        sums   = compute_sums(inputs)
        sums.sort()
        debug(f"sums: {sums}")
        random.shuffle(sums)

        outputs = solve(k, sums, inputs)
        debug(f"final numbers: {outputs}")
        assert outputs == inputs

