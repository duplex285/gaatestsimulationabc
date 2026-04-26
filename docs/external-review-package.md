---
layout: default
title: External Review Package
---

# External Review Package

**Purpose.** Onboard external reviewers (psychometricians, sport psychologists) and provide everything needed for a professional audit of the ABC Assessment.

**Repository.** [github.com/duplex285/gaatestsimulationabc](https://github.com/duplex285/gaatestsimulationabc), branch `literature-review-implementation`.

---

## What ABC is

ABC is a 36-item athlete self-report instrument that measures need satisfaction and frustration across three psychological needs translated to athlete domains:

- **Ambition** (autonomy): goal-pursuit, volitional self-direction
- **Belonging** (relatedness): authentic connection with teammates and coaches
- **Craft** (competence): skill development and mastery

It is grounded in Self-Determination Theory (Deci & Ryan 2000), follows the Bartholomew et al. (2011) need-thwarting framework for frustration items, and uses methodologies from Howard 2024 Oxford Handbook Ch. 22 for psychometric validation.

ABC is intended for biweekly longitudinal administration to athletes ages 18 to 25 in NCAA and elite club programs. It outputs continuous subscale scores, a categorical 4-state domain classification (display layer), and an 8-archetype theoretical taxonomy.

## What this audit is for

The synthetic-data validation phase is complete: 493 tests pass, 0 fail. A 49-paper literature review (Howard 2024 Ch. 22 plus supporting work) generated 18 implementation work items, of which a substantial subset has been implemented in the current branch. The instrument has not yet been tested empirically on real athletes.

The audit asks: **before Phase A pilot recruitment begins, are the items, the validity argument, the psychometric methods, and the open methodological decisions defensible?**

External reviewers are not expected to validate items via cognitive pretesting (that is a separate downstream step). External reviewers are expected to evaluate the design, the theoretical commitments, the methodological choices, and the planned empirical work.

## What you should read

Minimum reading for an informed review:

1. **[Landing page](index.html)** for orientation (this page is also accessible from there).
2. **[ABC Assessment Spec](abc-assessment-spec.html)** for the instrument and scoring.
3. **[Items v1](new-items-draft.html)** for the 36 current items.
4. **[Items v2](new-items-draft-v2.html)** for the 10 proposed item revisions.
5. **[Validity argument](validity-argument.html)** for the APA Standards 2014 evidentiary frame.
6. **[Methods (audit)](methods-audit.html)** for the psychometric infrastructure.
7. **[Howard 2024 implementation plan](howard-2024-implementation-plan.html)** for the 18 work items, especially Section "Literature Review v2."
8. **[Audit checklist](audit-checklist.html)** to organize your review.

Estimated reading time: 4 to 6 hours for a thorough review.

Optional context:
- [Personalization plan](improvement-plan-personalization-engine.html) (long; Section 18 is the literature-review reconciliation)
- [Phase A pre-registration](phase-a-preregistration.html)
- [Aspiration Index supplement](aspiration-index-supplement.html)

## What we are asking

Please use the [audit checklist](audit-checklist.html) to organize your review. Specifically:

**For psychometricians.** Sections A.1 (measurement model), A.2 (LPA model selection), A.3 (reverse-item design), A.4 (effect-size benchmarks), A.5 (difference scores and categorization), A.6 (cascade hypothesis), A.7 (sample size and power).

**For sport psychologists.** Sections B.1 (item content), B.2 (sport-specific gaps), B.3 (cultural and developmental accessibility), B.4 (goal content), B.5 (coach circumplex), B.6 (athlete-facing reports), B.7 (practitioner workflows).

## What we will do with your review

1. **Address each comment in writing.** Either accepted (with revisions made and documented) OR explicitly rejected (with rationale) in `docs/literature-review-activity-log.md` issue log.
2. **Acknowledge.** Reviewers willing to be acknowledged will be listed in publications and in this document with affiliation.
3. **Iterate.** A second-round audit may be requested for substantive item-level revisions.

## Reviewer acknowledgements (to be populated)

| Reviewer | Affiliation | Expertise | Date of review | Notes |
|---|---|---|---|---|
| (pending) | (pending) | (pending) | (pending) | (pending) |

## Conflict of interest

We ask reviewers to declare:
- Consulting relationships with athlete wellness platforms or assessment publishers
- Financial interests in competing instruments
- Prior published critique of any methodology used in ABC

Declarations do not disqualify a review; they contextualize it.

## Compensation

External reviewers may be compensated at a customary academic consulting rate. Contact the project owner for terms.

## Authority

The project owner has final decision authority. Reviewer comments inform decisions; they do not override them. The audit serves transparency and methodological discipline.

## Contact

Project owner: Greg Akinbiyi
Repository: [github.com/duplex285/gaatestsimulationabc](https://github.com/duplex285/gaatestsimulationabc)

---

## Reproducibility

Anyone can reproduce the synthetic-data validation:

```bash
git clone https://github.com/duplex285/gaatestsimulationabc.git
cd gaatestsimulationabc
git checkout literature-review-implementation
make setup
make validate-all
```

This runs the full 493+-test suite and confirms all results in this audit package. See `Makefile` for individual commands.

## License

Code: MIT License (see repository).
Documentation: CC-BY 4.0 (cite as "Akinbiyi, G. (2026). ABC Assessment Audit Package. https://github.com/duplex285/gaatestsimulationabc").
Items: ABC Assessment items are proprietary to the project owner. External use requires permission. The items are not redistributions of any licensed instrument (BPNSFS, PNTS, ABQ, MWMS); they are original to ABC, drawing on the same underlying SDT science.
