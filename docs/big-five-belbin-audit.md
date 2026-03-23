# Big Five and Belbin Inference: Audit Reference

The Big Five weight matrix and Belbin role inference remain valid after the archetype simplification from 24 types to 8 base patterns. Both modules operate on 6 subscale scores, not on type labels, so the type-system change leaves their inputs, formulas, and outputs unchanged. All 41 unit tests pass without modification.

This document records every constant, formula, and mapping in the two modules for auditor review.


## Big Five weight matrix and scoring pipeline

### Weight matrix (v4, covariance-aware)

The matrix maps 6 centred subscale scores (columns) to 5 Big Five trait z-scores (rows). Each cell is a fixed coefficient.

| Trait               | a_sat  | a_frust | b_sat  | b_frust | c_sat  | c_frust |
|---------------------|--------|---------|--------|---------|--------|---------|
| Openness            |  0.12  |   0.16  | -0.36  |  -0.35  |  0.52  |   0.33  |
| Conscientiousness   |  0.03  |   0.13  |  0.20  |   0.30  |  0.18  |  -0.45  |
| Extraversion        |  0.47  |   0.02  |  0.27  |   0.19  | -0.12  |   0.11  |
| Agreeableness       | -0.23  |   0.19  |  0.43  |  -0.13  |  0.08  |   0.18  |
| Neuroticism         |  0.00  |   0.24  |  0.05  |   0.41  | -0.03  |   0.05  |

Source: `src/python_scoring/big_five_inference.py`, lines 35-41.

### Centering formula

Each raw subscale score (0-10 scale) is centred before the dot product:

```
centred = (score - 5) / 5
```

Output range: -1.0 to +1.0. A score of 5 centres to 0 (neutral).

Source: `src/python_scoring/big_five_inference.py`, line 52.

### Percentile conversion formula

The dot product of centred scores and weight row yields a z-score. The z-score converts to a percentile:

```
percentile = 50 + z * 30
```

The result is clamped to the interval [1, 99] and rounded to one decimal place.

Source: `src/python_scoring/big_five_inference.py`, lines 65-68.

### Domain anchoring rationale

Each trait anchors on its theoretically defensible ABC domain, with cross-loadings that create genuine trait separation:

- **Openness** anchors on craft satisfaction (c_sat = +0.52) and craft frustration tolerance (c_frust = +0.33).
- **Conscientiousness** anchors on low craft frustration (c_frust = -0.45, discipline = low friction) with belonging reliability (b_sat = +0.20, b_frust = +0.30).
- **Extraversion** anchors on ambition satisfaction (a_sat = +0.47) and social energy (b_sat = +0.27).
- **Agreeableness** anchors on belonging satisfaction (b_sat = +0.43) with low assertion (a_sat = -0.23).
- **Neuroticism** anchors on belonging frustration (b_frust = +0.41) and ambition distress (a_frust = +0.24).


## Belbin role inference

### Domain-cluster mapping

Belbin's 9 roles group into three clusters, each mapped to one ABC domain:

| Cluster            | ABC Domain | Roles                                            |
|--------------------|------------|--------------------------------------------------|
| Thinking           | Craft      | Plant, Specialist, Monitor-Evaluator             |
| People             | Belonging  | Teamworker, Resource Investigator, Coordinator   |
| Action             | Ambition   | Shaper, Implementer, Completer-Finisher          |

Reference: Aranzabal et al. (2022).

Source: `src/python_scoring/belbin_inference.py`, lines 49-116.

### Role definitions: differentiating trait and qualifiers

Each role is differentiated by one Big Five trait. The qualifier depends on whether that trait exceeds the natural threshold (60th percentile).

| Role                  | Domain    | Trait               | Natural qualifier  | Manageable qualifier |
|-----------------------|-----------|---------------------|--------------------|----------------------|
| Plant                 | Craft     | Openness            | Creative           | Conceptual           |
| Specialist            | Craft     | Conscientiousness   | Deep Mastery       | Focused              |
| Monitor-Evaluator     | Craft     | Neuroticism         | Vigilant           | Analytical           |
| Teamworker            | Belonging | Agreeableness       | Anchor             | Supportive           |
| Resource Investigator | Belonging | Extraversion        | Networker          | Curious              |
| Coordinator           | Belonging | Conscientiousness   | Balanced           | Structured           |
| Shaper                | Ambition  | Extraversion        | Inspiring          | Driving              |
| Implementer           | Ambition  | Conscientiousness   | Systematic         | Practical            |
| Completer-Finisher    | Ambition  | Neuroticism         | Quality Driven     | Thorough             |

### Domain affinity weights

Domain ranking uses satisfaction scores (a_sat, b_sat, c_sat) sorted descending. Ties break by fixed order: ambition > belonging > craft.

| Rank position | Affinity weight |
|---------------|-----------------|
| 0 (primary)   | 1.0             |
| 1 (secondary) | 0.5             |
| 2 (tertiary)  | 0.0 (excluded)  |

Restricting to two clusters reduces noise without losing discriminant validity.

Source: `src/python_scoring/belbin_inference.py`, lines 36-39.

### Role scoring formula

Each role receives a continuous score:

```
role_score = domain_affinity * trait_percentile / 100
```

Where:
- `domain_affinity` comes from the rank table above (1.0, 0.5, or 0.0).
- `trait_percentile` is the Big Five percentile for that role's differentiating trait (1-99 scale).

Roles with a score at or above the threshold (0.30) fire. The highest-scoring role always fires, guaranteeing at least one role per participant.

Source: `src/python_scoring/belbin_inference.py`, lines 140-160, 206-213.

### Qualifier assignment

```
if trait_percentile >= 60.0:
    qualifier = qualifier_natural
else:
    qualifier = qualifier_manageable
```

Source: `src/python_scoring/belbin_inference.py`, lines 155-158.


## Verification: all 9 Belbin roles remain reachable with 8 base patterns

The Belbin module does not read archetype labels. It reads 6 subscale scores and 5 Big Five percentiles. The simplification from 24 types to 8 base patterns changes the label assigned to a score profile; it does not change the score profile itself. Every combination of domain ranking and trait percentile that produced a given Belbin role under the 24-type system produces the same role under the 8-type system.

The test `TestAllNineRolesCoverable::test_all_roles_reachable` confirms this by constructing a targeted input for each of the 9 roles and verifying it fires. All 9 pass.

Reachability by cluster:

- **Thinking (Craft primary):** Plant (high O), Specialist (high C), Monitor-Evaluator (high N).
- **People (Belonging primary):** Teamworker (high A), Resource Investigator (high E), Coordinator (high C).
- **Action (Ambition primary):** Shaper (high E), Implementer (high C), Completer-Finisher (high N).

Each of the 8 base patterns maps to one of 3 possible domain rankings (one domain is primary). Within each domain ranking, all 3 cluster roles are reachable depending on the Big Five profile. Because all 3 domain rankings remain achievable under the 8-pattern system, all 9 roles remain reachable.


## Impact of expanding from 24 items to 36 items

Expanding the item pool from 24 to 36 items changes item-level responses but does not change the scoring pipeline. Subscale scores remain on the 0-10 scale regardless of item count; additional items improve measurement precision (lower standard error per subscale) without altering the scale endpoints or the aggregation formula.

The Big Five weight matrix takes 6 subscale scores as input. The Belbin module takes those same 6 subscale scores plus 5 Big Five percentiles. Neither module references item count, item IDs, or archetype labels. Expanding from 24 to 36 items therefore requires no changes to the weight matrix, the centering formula, the percentile conversion, the domain-cluster mapping, or the role scoring formula.

What improves: subscale reliability. More items per subscale reduce measurement noise, which means the Big Five percentiles and Belbin role scores better reflect the true latent scores. The formulas stay the same; the inputs become more precise.


## Test results

All 41 tests pass (13 Big Five, 28 Belbin) as of 2026-03-22.

```
tests/python_tests/test_big_five.py    13 passed
tests/python_tests/test_belbin.py      28 passed
Total:                                 41 passed, 0 failed
```

Test coverage includes: centering arithmetic, percentile clamping, directional trait anchoring, domain ranking with tie-breaking, all 9 roles reachable, qualifier thresholds, multi-role firing, tertiary exclusion, return-value schema, and backward compatibility.
