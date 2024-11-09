import itertools, random

S = [random.randint(-10, 10) for i in range(4)]
o = []

## O(|S|! x |S|)
for p in itertools.permutations(S):
    is_ordered = True
    for i in range(1, len(p)):
        is_ordered = is_ordered and (p[i - 1] <= p[i])
    # end for
    if is_ordered:
        o = p
    # end if
# end for

print(o)
