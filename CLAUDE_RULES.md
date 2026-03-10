# Claude Code Development Rules — ABC Assessment Project

## BLOCKING RULES (Non-negotiable)

These rules override all other considerations. Claude Code MUST follow these.

### Rule 1: No Custom Statistical Implementations

NEVER implement CFA, factor analysis, or SEM from scratch.
ALWAYS use established libraries: lavaan (R), scipy.stats (Python).

Custom implementations cannot be audited by external experts.

Verification: `grep -r "def confirmatory_factor_analysis" src/` should return nothing.

### Rule 2: Every Calculation Must Reference Spec

NEVER implement formulas without a spec reference.
ALWAYS include a comment: `# Reference: abc-assessment-spec Section X.Y`

```python
# WRONG
def compute_mean(items):
    return sum(items) / len(items)

# CORRECT
def compute_subscale_mean(items: list[float]) -> float:
    """Compute mean of 4-item subscale.

    Reference: abc-assessment-spec Section 2.1
    """
    return sum(items) / len(items)
```

Verification: `python scripts/check_spec_references.py` must pass before commit.

### Rule 3: Test-First Development (TDD)

NEVER implement a module before its tests exist.
ALWAYS write tests first, then implement.

Workflow:
1. Create test_module.py with comprehensive tests
2. Run pytest — tests FAIL (correct, no implementation yet)
3. Implement module.py
4. Run pytest — tests PASS
5. Commit

Verification: git history shows test commit before implementation commit.

### Rule 4: Validation Gates Are Real

NEVER proceed to the next phase if the current phase fails.
ALWAYS wait for explicit approval before advancing.

Phase 0 to Phase A gate:
- R validation must output "ABC 6-FACTOR MODEL VALIDATED"
- All fit indices must show PASS
- User must explicitly say "proceed to Python"

If validation fails: STOP, report failure, propose fixes, wait for approval.

### Rule 5: Ground Truth Tests Are Mandatory

NEVER skip ground truth validation.
ALWAYS test against known-answer datasets:

- Perfect Thriving: all sat items 7, frust items 1 -> sat=10.0, frust=0.0, state=Thriving
- Perfect Distressed: all sat items 1, frust items 7 -> sat=0.0, frust=10.0, state=Distressed
- Perfect Vulnerable: all items 7 -> sat=10.0, frust=10.0, state=Vulnerable
- Perfect Mild: all items 1 -> sat=0.0, frust=0.0, state=Mild
- Known Midpoint: all items 4 -> all subscales=5.0

These tests must pass with 100% accuracy.

### Rule 6: No Silent Failures

NEVER suppress errors or warnings.
ALWAYS make failures loud and obvious.

```python
# WRONG
try:
    score = compute_score(items)
except:
    score = 0

# CORRECT
try:
    score = compute_score(items)
except Exception as e:
    raise ValueError(f"Scoring failed for items {items}: {e}")
```

### Rule 7: Reproducibility Is Non-Negotiable

NEVER use random operations without seeding.
ALWAYS set seed at the start of scripts.

R scripts:
```r
set.seed(42)  # First line after library loads
```

Python scripts:
```python
np.random.seed(42)  # Before any random operations
```

### Rule 8: External Review Requirements

NEVER claim "validation complete" without audit-ready outputs.
ALWAYS generate:

- Full lavaan output (not truncated): `outputs/reports/lavaan_full_output.txt`
- CSV exports of all results: `outputs/reports/model_comparison.csv`
- One-command reproduction script: `scripts/reproduce_validation.R`
- Complete methodological justification: `docs/external-review-package.md`

---

## NON-BLOCKING GUIDELINES (Preferences)

- Prefer descriptive variable names over short ones
- Prefer explicit over implicit (no magic numbers)
- Add docstrings to all public functions
- Use type hints in Python
- Comment complex logic

---

## Single Source of Truth

| Decision               | Single Source                              |
|------------------------|--------------------------------------------|
| Mathematical formulas  | abc-assessment-spec Section 13             |
| Validation thresholds  | config/validation_thresholds.yaml          |
| Correlation matrices   | config/correlation_matrices.yaml           |
| R methodology          | lavaan package (no custom CFA code)        |
| Python correctness     | Test suite (tests/python_tests/)           |
| Expected results       | R validation outputs (ground truth)        |
| Environment setup      | Makefile                                   |

---

## Verification Commands

Before claiming any phase complete, run:

```bash
make lint          # No linting errors
make test-python   # All tests pass
make coverage      # >= 85% coverage
make test-r        # R scripts complete successfully
make check-spec    # All formulas reference spec
```

---

## When in Doubt

1. Check the spec (docs/abc-assessment-spec.md)
2. Check the tests (what do tests expect?)
3. Check established packages (lavaan docs, scipy docs)
4. Ask the user

Never guess. Never approximately implement. Never skip validation.
