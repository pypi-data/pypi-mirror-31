#! /usr/bin/env python3

from typing import *

Range = Tuple[float, float]

from math import inf
from bisect import bisect

def histogram(thresholds: List[float], data: Iterable[float], leftmost: float = -inf) -> Mapping[float, int]:
    stats = [0] * (len(thresholds) + 1)

    for v in data:
        pos = bisect(thresholds, v)
        stats[pos] += 1

    return dict(zip([leftmost] + thresholds, stats))


def covers(covered: Iterable[Range]) -> Iterable[Range]:
    laststart = lastend = -inf
    for localstart, localend in covered:
        if lastend < localstart:
            if laststart < lastend:
                yield (laststart, lastend)

            laststart = localstart

        if lastend < localend:
            lastend = localend

    if laststart < lastend:
        yield (laststart, lastend)


def gaps(covered: Iterable[Range], whole: Range = (-inf, inf)) -> Iterable[Range]:
    start, end = whole

    lastend = start
    for localstart, localend in covered:
        localstart = max(start, localstart)
        localend = min(end, localend)

        if lastend < localstart:
            yield (lastend, localstart)

        if lastend < localend:
            lastend = localend

    if lastend < end:
        yield (lastend, end)
