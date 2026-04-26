"""Authoritative banned-term list for user-facing output.

Reference: abc-assessment-spec Section 17.3

No term in this list may appear in any athlete- or coach-facing surface.
Internal analysis, validity documents, and research write-ups are allowed
to use these terms; narrative templates, on-screen copy, and recommendation
text are not.

The list is imported by test files that enforce the rule and by any
future production lint rule. Keeping it in one place prevents drift.
"""

from __future__ import annotations

import re

# Psychometric internals
_PSYCHOMETRIC_TERMS = [
    "bifactor",
    "omega",
    "cronbach",
    "mcdonald",
    "cfi",
    "rmsea",
    "srmr",
    "wlsmv",
    "esem",
    "cfa",
    "eap",
    "sem",
    "measurement invariance",
    "configural",
    "metric",
    "scalar",
    "icc",
    "dif",
    "rci",
    "conditional sem",
]

# Statistical internals
_STATISTICAL_TERMS = [
    "mahalanobis",
    "cusum",
    "ri-clpm",
    "clpm",
    "polychoric",
    "monte carlo",
    "likelihood",
    "posterior",
    "prior",
    "bayes factor",
    "p-value",
    "confidence interval",
    "credibility interval",
    "effect size",
    "regression to the mean",
]

# SDT mini-theory jargon
_SDT_TERMS = [
    "introjection",
    "introjected",
    "identified regulation",
    "integrated regulation",
    "amotivation",
    "intrinsic motivation",
    "extrinsic motivation",
    "harmonious passion",
    "obsessive passion",
    "causality orientation",
    "autonomy support",
    "need thwarting",
    "need frustration",
    "self-concordance",
    "authentic inner compass",
    "relative autonomy index",
    "organismic integration",
    "basic psychological needs",
]

# Measure names
_MEASURE_NAMES = [
    "bpnsfs",
    "abq",
    "bpnt",
    "sdt",
    "oit",
    "gcos",
    "bfi-2",
    "mtq48",
    "strengthsfinder",
    "pnse",
    "ess",
    "rai",
    "ploc",
]

BANNED_TERMS: tuple[str, ...] = tuple(
    _PSYCHOMETRIC_TERMS + _STATISTICAL_TERMS + _SDT_TERMS + _MEASURE_NAMES
)


def contains_banned_term(text: str) -> tuple[bool, str | None]:
    """Return (True, matched_term) if any banned term appears in text.

    Matching is case-insensitive and uses word boundaries so that, for
    example, "prior" matches "a prior belief" but not "priority". The
    first match wins; callers that need all matches should iterate.

    Reference: abc-assessment-spec Section 17.3
    """
    lowered = text.lower()
    for term in BANNED_TERMS:
        pattern = r"\b" + re.escape(term) + r"\b"
        if re.search(pattern, lowered):
            return True, term
    return False, None
