"""
Given the 21 pairwise sums of 7 numbers in arbitrary order, find the 7 numbers
"""

import math
import sys

from fractions import Fraction
from numbers   import Rational
from typing    import List, Optional


_a, _b, _c, _d, _e, _f, _g = range(7)


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
        assert x == correct, f"incorrect step: computed {x} != expected {correct}"

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
        solve7,
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
    sums, nums, translation, scale = normalize(sums, nums, 0, 0, 1, 1)

    # ab = 0 and ac = 1
    ab = check(sums[0],  nums, _a, _b)
    ac = check(sums[1],  nums, _a, _c)
    ef = check(sums[-1], nums, _e, _f)
    df = check(sums[-2], nums, _d, _f)
    
    abcdef = check(sum(sums)//5, nums, _a, _b, _c, _d, _e, _f)

    af = check((ab + ac + ef + df - abcdef), nums, _a, _f)
    bd = check(df - af, nums, _b, _d)
    cd = check(bd + 1,  nums, _c, _d)
    ce = check(cd + ef - df, nums, _c, _e)
    be = check(bd + ef - df, nums, _b, _e)

    #*ab  *ac   ad   ae  *af        0   1   a+d   a+e   a+f
    #      bc  *bd  *be   bf          1-2a  d-a   e-a   f-a
    #          *cd  *ce   cf                d-a+1 e-a+1 f-a+1
    #                de  *df                      d+e   d+f
    #                    *ef                            e+f

    for entry in [ab,ac,af,bd,be,cd,ce,df,ef]:
        sums.remove(entry)

    # sums[:3] is {bc, ad, ae}
    # af + abcdef - sum(sums[:3]) = af + abcdef - bc - ad - ae = 2f

    aabcde = check(sum(sums[:3]), nums, _a, _a, _b, _c, _d, _e)
    a = check((aabcde + af - abcdef)//2, nums, _a)
    b = check(ab - a, nums, _b)
    c = check(ac - a, nums, _c)
    d = check(bd - b, nums, _d)
    e = check(be - b, nums, _e)
    f = check(af - a, nums, _f)

    return unnormalize([a,b,c,d,e,f], translation, scale)


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
        if set([bf,ce,be,cf]).issubset(set(sums)) and be < bf < cf and be < ce < cf:
            candidates1.append((ag,be,bf,ce,cf))
            check(bf, nums, _b, _f)
            check(ce, nums, _c, _e)
            check(be, nums, _b, _e)
            check(cf, nums, _c, _f)

    print(f"--- there are {len(candidates1)} candidates for ag: {candidates1}")

    candidates2 = []
    for ae in sums[3:7]:
        cg = ac + eg - ae
        af = ac + fg - cg
        bg = ab + fg - af
        if set([cg, af, bg]).issubset(set(sums)) and ae < af < bg < cg:
            candidates2.append((ae, af, bg, cg))
            check(cg, nums, _c, _g)
            check(af, nums, _a, _f)
            check(bg, nums, _b, _g)

    print(f"--- there are {len(candidates2)} candidates for ae: {candidates2}")

    abcdefg = check(sum(sums)//6, nums, _a, _b, _c, _d, _e, _f, _g)

    def compute(set1, set2):
        ag, be, bf, ce, cf = set1
        ae, af, bg, cg     = set2
        filtered = list(sums)
        for x in [ae, af, ag, be, bf, bg, ce, cf, cg]:
            filtered.remove(x)
        print(len(filtered))
        abcd = check(sum(filtered[0:6])//3, nums, _a, _b, _c, _d)

        d = abcdefg - ag - bf - ce
        a = ab + ac + d - abcd
        b = ab - a
        c = ac - a

        defg = check(sum(filtered[6:12])//3, nums, _d, _e, _f, _g)
        g = fg + eg + d - defg
        e = eg - g
        f = fg - g
        return [a,b,c,d,e,f,g]

    candidates = [compute(set1, set2) for set1 in candidates1 for set2 in candidates2]
    print(candidates)

    return candidates[0]


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
    print(output[:10])

def compute_sums(nums):
    return [nums[i] + nums[j] for i in range(len(nums)) for j in range(i)]


if __name__ == '__main__':

    k = int(sys.argv[1]) if len(sys.argv) > 1 else 7

    import random
    inputs = [random.randint(-1000,1000) for i in range(k)]
    inputs =   [-964, -769, -769, -114, 281, 742, 945]
    inputs.sort()
    print(f"original numbers: {inputs}")

    sums   = compute_sums(inputs)
    sums.sort()
    print(f"sums: {sums}")
    random.shuffle(sums)

    outputs = solve(k, sums, inputs)
    print(f"final numbers: {outputs}")
    assert outputs == inputs

