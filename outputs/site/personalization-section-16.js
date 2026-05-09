/**
 * ABC Section 16 SDT Mini-Theory Extensions (JS port)
 *
 * Faithful port of the Python scoring modules:
 *   - passion_quality.py            (16.2)
 *   - overinvestment_trigger.py     (16.2)
 *   - regulatory_style.py           (16.1)
 *   - regulation_erosion.py         (16.1)
 *   - self_concordance.py           (16.7)
 *   - self_concordance_trajectory.py (16.7)
 *   - group_conscious.py            (16.5)
 *   - causality_orientations.py     (16.6)
 *   - coach_circumplex.py           (16.3)
 *   - coach_circumplex_scorer.py    (16.3)
 *   - narrative_engine.py           (14 new generators)
 *
 * All public methods, constants, and narratives mirror the Python implementation
 * line-for-line. Item text is taken verbatim from the docs/*-items-draft.md sources.
 *
 * Reference: abc-assessment-spec Section 16 (per-section)
 */

const ABCSection16 = (function () {
  "use strict";

  // ===========================================================================
  // ITEM REGISTRY
  // Shape mirrors index.html ASSESS_ITEMS so the form can render uniformly.
  // ===========================================================================

  var ITEMS = {
    // --- 16.2 Passion quality (HP = harmonious, OP = obsessive) ---
    HP1: { layer: "passion", subscale: "harmonious", domainLabel: "Passion",
      text: "How often in the past three months did your sport fit well alongside the other things that matter in your life?", reverse: false },
    HP2: { layer: "passion", subscale: "harmonious", domainLabel: "Passion",
      text: "How often in the past three months did you engage with your sport because you genuinely wanted to, not because you felt you had to?", reverse: false },
    HP3: { layer: "passion", subscale: "harmonious", domainLabel: "Passion",
      text: "How often in the past three months were you able to step away from sport when you needed to, without feeling like you were losing part of yourself?", reverse: false },
    OP1: { layer: "passion", subscale: "obsessive", domainLabel: "Passion",
      text: "How often in the past three months did you find it hard to stop thinking about your sport even when you wanted a break?", reverse: false },
    OP2: { layer: "passion", subscale: "obsessive", domainLabel: "Passion",
      text: "How often in the past three months did you feel tense or uneasy when you were unable to train?", reverse: false },
    OP3: { layer: "passion", subscale: "obsessive", domainLabel: "Passion",
      text: "How often in the past three months did your commitment to sport create friction with other parts of your life?", reverse: false },

    // --- 16.1 Regulatory style ---
    AR1: { layer: "regulatory", subscale: "autonomous", domain: "ambition", domainLabel: "Regulation — Ambition",
      text: "How often in the past two weeks did you pursue your goals because they genuinely matter to who you are?", reverse: false },
    AR2: { layer: "regulatory", subscale: "controlled", domain: "ambition", domainLabel: "Regulation — Ambition",
      text: "How often in the past two weeks did you pursue your goals because you would feel guilty, ashamed, or anxious if you did not?", reverse: false },
    BR1: { layer: "regulatory", subscale: "autonomous", domain: "belonging", domainLabel: "Regulation — Belonging",
      text: "How often in the past two weeks did you invest in relationships on this team because you genuinely care about the people?", reverse: false },
    BR2: { layer: "regulatory", subscale: "controlled", domain: "belonging", domainLabel: "Regulation — Belonging",
      text: "How often in the past two weeks did you invest in relationships on this team because you felt you had to keep up appearances or avoid being excluded?", reverse: false },
    CR1: { layer: "regulatory", subscale: "autonomous", domain: "craft", domainLabel: "Regulation — Craft",
      text: "How often in the past two weeks did you work on your skills because improving them is important to who you are as an athlete?", reverse: false },
    CR2: { layer: "regulatory", subscale: "controlled", domain: "craft", domainLabel: "Regulation — Craft",
      text: "How often in the past two weeks did you work on your skills because you worried about what coaches, teammates, or rivals would think if you did not?", reverse: false },

    // --- 16.5 Group-conscious team measurement ---
    AG1: { layer: "groupConscious", subscale: "collective", domain: "ambition", domainLabel: "Team — Ambition",
      text: "How often in the past two weeks did you sense that your teammates' goals were meaningful to them?", reverse: false },
    BG1: { layer: "groupConscious", subscale: "collective", domain: "belonging", domainLabel: "Team — Belonging",
      text: "How often in the past two weeks did you notice your teammates feeling connected to each other?", reverse: false },
    CG1: { layer: "groupConscious", subscale: "collective", domain: "craft", domainLabel: "Team — Craft",
      text: "How often in the past two weeks did you see your teammates growing in their skills?", reverse: false },
    TI1: { layer: "groupConscious", subscale: "team_id", domainLabel: "Team Identification",
      text: "How often in the past two weeks did this team's wins or losses feel personal to you?", reverse: false },
    TI2: { layer: "groupConscious", subscale: "team_id", domainLabel: "Team Identification",
      text: "How often in the past two weeks did you feel like a real member of this team, not just someone on the roster?", reverse: false },

    // --- 16.7 Self-concordance (per-goal) ---
    SC1: { layer: "selfConcordance", subscale: "controlled", domainLabel: "Goal Reasons",
      text: "Thinking about a goal you are working on right now, how true is this reason: because someone else (a coach, parent, or teammate) wants me to.", reverse: false },
    SC2: { layer: "selfConcordance", subscale: "controlled", domainLabel: "Goal Reasons",
      text: "Thinking about a goal you are working on right now, how true is this reason: because I would feel guilty, anxious, or disappointed in myself if I did not.", reverse: false },
    SC3: { layer: "selfConcordance", subscale: "autonomous", domainLabel: "Goal Reasons",
      text: "Thinking about a goal you are working on right now, how true is this reason: because it matters to me personally.", reverse: false },
    SC4: { layer: "selfConcordance", subscale: "autonomous", domainLabel: "Goal Reasons",
      text: "Thinking about a goal you are working on right now, how true is this reason: because I find the work itself interesting or rewarding.", reverse: false },

    // --- 16.6 Causality orientations (annual cadence) ---
    AO1: { layer: "causality", subscale: "autonomy", domainLabel: "Approach to Situations",
      text: "Over the past month, how often did you make a decision because it felt right for you, regardless of what others thought?", reverse: false },
    AO2: { layer: "causality", subscale: "autonomy", domainLabel: "Approach to Situations",
      text: "Over the past month, how often did you notice what you wanted before deciding what to do?", reverse: false },
    AO3: { layer: "causality", subscale: "autonomy", domainLabel: "Approach to Situations",
      text: "Over the past month, how often did you change direction when a path no longer fit what you wanted?", reverse: false },
    AO4: { layer: "causality", subscale: "autonomy", domainLabel: "Approach to Situations",
      text: "Over the past month, how often did you approach a hard task by figuring out what interested you about it?", reverse: false },
    CO1: { layer: "causality", subscale: "controlled", domainLabel: "Approach to Situations",
      text: "Over the past month, how often did you make a decision based on what others would think?", reverse: false },
    CO2: { layer: "causality", subscale: "controlled", domainLabel: "Approach to Situations",
      text: "Over the past month, how often did you follow a plan because you were supposed to, not because you wanted to?", reverse: false },
    CO3: { layer: "causality", subscale: "controlled", domainLabel: "Approach to Situations",
      text: "Over the past month, how often did you feel you had to meet an expectation, even when it did not fit you?", reverse: false },
    CO4: { layer: "causality", subscale: "controlled", domainLabel: "Approach to Situations",
      text: "Over the past month, how often did you approach a hard task by focusing on what would look good?", reverse: false },
    IO1: { layer: "causality", subscale: "impersonal", domainLabel: "Approach to Situations",
      text: "Over the past month, how often did a situation feel out of your hands, like it was happening to you?", reverse: false },
    IO2: { layer: "causality", subscale: "impersonal", domainLabel: "Approach to Situations",
      text: "Over the past month, how often did you feel stuck when a decision needed to be made?", reverse: false },
    IO3: { layer: "causality", subscale: "impersonal", domainLabel: "Approach to Situations",
      text: "Over the past month, how often did an outcome feel like it was mostly luck, good or bad?", reverse: false },
    IO4: { layer: "causality", subscale: "impersonal", domainLabel: "Approach to Situations",
      text: "Over the past month, how often did you find yourself unable to act on what you wanted?", reverse: false },

    // --- 16.3 Coach circumplex (24 items, dual-rater) ---
    // Stem prepended at render: "How often in the past month did you..."
    CXA1: { layer: "coachCircumplex", facet: "autonomy_support", domainLabel: "Coaching — Autonomy",
      text: "How often in the past month did you acknowledge that an athlete saw a situation differently than you did?", reverse: false },
    CXA2: { layer: "coachCircumplex", facet: "autonomy_support", domainLabel: "Coaching — Autonomy",
      text: "How often in the past month did you offer athletes a genuine choice within a training decision?", reverse: false },
    CXA3: { layer: "coachCircumplex", facet: "autonomy_support", domainLabel: "Coaching — Autonomy",
      text: "How often in the past month did you explain the reason behind a drill or a rule?", reverse: false },
    CXA4: { layer: "coachCircumplex", facet: "autonomy_support", domainLabel: "Coaching — Autonomy",
      text: "How often in the past month did you ask an athlete for their opinion before deciding?", reverse: false },
    CXA5: { layer: "coachCircumplex", facet: "autonomy_support", domainLabel: "Coaching — Autonomy",
      text: "How often in the past month did you let an athlete take initiative without stepping in?", reverse: false },
    CXS1: { layer: "coachCircumplex", facet: "structure", domainLabel: "Coaching — Structure",
      text: "How often in the past month did you make the goal of a drill or session clear before starting?", reverse: false },
    CXS2: { layer: "coachCircumplex", facet: "structure", domainLabel: "Coaching — Structure",
      text: "How often in the past month did you give an athlete specific, constructive feedback on their performance?", reverse: false },
    CXS3: { layer: "coachCircumplex", facet: "structure", domainLabel: "Coaching — Structure",
      text: "How often in the past month did you break a difficult skill into steps an athlete could work through?", reverse: false },
    CXS4: { layer: "coachCircumplex", facet: "structure", domainLabel: "Coaching — Structure",
      text: "How often in the past month did you follow through on something you said you would do?", reverse: false },
    CXS5: { layer: "coachCircumplex", facet: "structure", domainLabel: "Coaching — Structure",
      text: "How often in the past month did you adjust a plan when it was not working, rather than push through?", reverse: false },
    CXR1: { layer: "coachCircumplex", facet: "relatedness_support", domainLabel: "Coaching — Relatedness",
      text: "How often in the past month did you ask an athlete about something in their life outside sport?", reverse: false },
    CXR2: { layer: "coachCircumplex", facet: "relatedness_support", domainLabel: "Coaching — Relatedness",
      text: "How often in the past month did you show genuine warmth when an athlete was struggling?", reverse: false },
    CXR3: { layer: "coachCircumplex", facet: "relatedness_support", domainLabel: "Coaching — Relatedness",
      text: "How often in the past month did you remember something specific an athlete told you before?", reverse: false },
    CXR4: { layer: "coachCircumplex", facet: "relatedness_support", domainLabel: "Coaching — Relatedness",
      text: "How often in the past month did you celebrate an athlete's non-performance win (academic, personal, social)?", reverse: false },
    CXR5: { layer: "coachCircumplex", facet: "relatedness_support", domainLabel: "Coaching — Relatedness",
      text: "How often in the past month did you make it clear that an athlete mattered regardless of how they performed?", reverse: false },
    CXC1: { layer: "coachCircumplex", facet: "controlling", domainLabel: "Coaching — Controlling",
      text: "How often in the past month did you use guilt or shame to push an athlete to try harder?", reverse: false },
    CXC2: { layer: "coachCircumplex", facet: "controlling", domainLabel: "Coaching — Controlling",
      text: "How often in the past month did you withdraw attention or warmth when an athlete performed poorly?", reverse: false },
    CXC3: { layer: "coachCircumplex", facet: "controlling", domainLabel: "Coaching — Controlling",
      text: "How often in the past month did you compare an athlete unfavorably to a teammate or rival to motivate them?", reverse: false },
    CXC4: { layer: "coachCircumplex", facet: "controlling", domainLabel: "Coaching — Controlling",
      text: "How often in the past month did you interrupt an athlete to correct them before they finished speaking?", reverse: false },
    CXC5: { layer: "coachCircumplex", facet: "controlling", domainLabel: "Coaching — Controlling",
      text: "How often in the past month did you frame rewards as contingent on meeting your expectations rather than as recognition?", reverse: false },
    CXH1: { layer: "coachCircumplex", facet: "chaos", domainLabel: "Coaching — Chaos",
      text: "How often in the past month did you change the plan or expectations without warning athletes?", reverse: false },
    CXH2: { layer: "coachCircumplex", facet: "chaos", domainLabel: "Coaching — Chaos",
      text: "How often in the past month did you forget or drop something you had previously committed to?", reverse: false },
    CXH3: { layer: "coachCircumplex", facet: "chaos", domainLabel: "Coaching — Chaos",
      text: "How often in the past month did you show up to practice without a clear plan?", reverse: false },
    CXH4: { layer: "coachCircumplex", facet: "chaos", domainLabel: "Coaching — Chaos",
      text: "How often in the past month did you respond to the same athlete behavior with different reactions on different days?", reverse: false },
  };

  var LAYER_ITEMS = {
    passion: ["HP1", "HP2", "HP3", "OP1", "OP2", "OP3"],
    regulatory: ["AR1", "AR2", "BR1", "BR2", "CR1", "CR2"],
    groupConscious: ["AG1", "BG1", "CG1", "TI1", "TI2"],
    selfConcordance: ["SC1", "SC2", "SC3", "SC4"],
    causality: ["AO1", "AO2", "AO3", "AO4", "CO1", "CO2", "CO3", "CO4", "IO1", "IO2", "IO3", "IO4"],
    coachCircumplex: ["CXA1","CXA2","CXA3","CXA4","CXA5","CXS1","CXS2","CXS3","CXS4","CXS5","CXR1","CXR2","CXR3","CXR4","CXR5","CXC1","CXC2","CXC3","CXC4","CXC5","CXH1","CXH2","CXH3","CXH4"],
  };

  // ===========================================================================
  // HELPERS
  // ===========================================================================

  function normalize10(mean1to7) { return ((mean1to7 - 1.0) / 6.0) * 10.0; }

  function _mean(xs) {
    if (!xs.length) return null;
    var s = 0;
    for (var i = 0; i < xs.length; i++) s += xs[i];
    return s / xs.length;
  }

  function _stdev(xs) {
    if (xs.length < 2) return 0;
    var m = _mean(xs);
    var ss = 0;
    for (var i = 0; i < xs.length; i++) ss += (xs[i] - m) * (xs[i] - m);
    return Math.sqrt(ss / (xs.length - 1));
  }

  // Banker's rounding (round half to even), matching Python 3's built-in round().
  function _roundHalfToEven(x) {
    var floor = Math.floor(x);
    var diff = x - floor;
    if (diff < 0.5) return floor;
    if (diff > 0.5) return floor + 1;
    return floor % 2 === 0 ? floor : floor + 1;
  }

  function _present(responses, codes) {
    var out = [];
    for (var i = 0; i < codes.length; i++) {
      var v = responses[codes[i]];
      if (v !== undefined && v !== null) out.push(v);
    }
    return out;
  }

  function _olsSlope(xs, ys) {
    var n = xs.length;
    var xMean = _mean(xs);
    var yMean = _mean(ys);
    var num = 0, den = 0;
    for (var i = 0; i < n; i++) {
      num += (xs[i] - xMean) * (ys[i] - yMean);
      den += (xs[i] - xMean) * (xs[i] - xMean);
    }
    if (den === 0) return 0;
    return num / den;
  }

  // ===========================================================================
  // 16.2 PASSION QUALITY
  // ===========================================================================

  var PASSION = {
    HP_ITEMS: ["HP1","HP2","HP3"],
    OP_ITEMS: ["OP1","OP2","OP3"],
    ALL_ITEMS: ["HP1","HP2","HP3","OP1","OP2","OP3"],
    MIN_ITEMS_FOR_DISPLAY: 4,
    MIN_ITEMS_FOR_RECOMMENDATION: 6,
    BALANCE_LEANING_THRESHOLD: 2.0,
    BALANCE_AMBIGUOUS_THRESHOLD: 1.0,
    SUBSCALE_ELEVATED_THRESHOLD: 5.0,
  };

  function scorePassionQuality(responses) {
    var hpRaw = _present(responses, PASSION.HP_ITEMS);
    var opRaw = _present(responses, PASSION.OP_ITEMS);
    var itemsAnswered = hpRaw.length + opRaw.length;

    if (itemsAnswered < PASSION.MIN_ITEMS_FOR_DISPLAY) {
      return {
        hp_score: null, op_score: null, balance: null,
        leaning: "not_computed", items_answered: itemsAnswered,
        display_gate_passed: false, recommendation_gate_passed: false,
        gate_reason: "fewer than 4 of 6 passion items answered",
      };
    }

    var hpScore = hpRaw.length ? normalize10(_mean(hpRaw)) : null;
    var opScore = opRaw.length ? normalize10(_mean(opRaw)) : null;
    var balance = (hpScore !== null && opScore !== null) ? (hpScore - opScore) : null;

    var hpElev = hpScore !== null && hpScore >= PASSION.SUBSCALE_ELEVATED_THRESHOLD;
    var opElev = opScore !== null && opScore >= PASSION.SUBSCALE_ELEVATED_THRESHOLD;
    var leaning;
    if (hpElev && opElev) leaning = "mixed";
    else if (!hpElev && !opElev) leaning = "uninvested";
    else if (balance !== null && balance >= PASSION.BALANCE_LEANING_THRESHOLD && hpElev) leaning = "harmonious";
    else if (balance !== null && balance <= -PASSION.BALANCE_LEANING_THRESHOLD && opElev) leaning = "obsessive";
    else leaning = "insufficient_signal";

    var allAnswered = itemsAnswered === PASSION.MIN_ITEMS_FOR_RECOMMENDATION;
    var decisiveLeaning = ["harmonious","obsessive","mixed","uninvested"].indexOf(leaning) >= 0;
    var recPass = false;
    var gateReason = "";
    if (allAnswered && decisiveLeaning) {
      recPass = true;
      gateReason = "recommendation gate passed";
    } else if (allAnswered && balance !== null && Math.abs(balance) < PASSION.BALANCE_AMBIGUOUS_THRESHOLD) {
      gateReason = "pattern still forming; balance close to zero";
    } else if (!allAnswered) {
      gateReason = itemsAnswered + " of 6 items answered; recommendation gate requires all six";
    } else {
      gateReason = "leaning not strong enough to drive recommendation";
    }

    return {
      hp_score: hpScore, op_score: opScore, balance: balance,
      leaning: leaning, items_answered: itemsAnswered,
      display_gate_passed: true, recommendation_gate_passed: recPass,
      gate_reason: gateReason,
    };
  }

  // ===========================================================================
  // 16.2 OVERINVESTMENT TRIGGER
  // ===========================================================================

  var OVERINVEST = {
    SAT_THRIVING_THRESHOLD: 7.0,
    FRUST_LOW_THRESHOLD: 3.0,
    RECOVERY_DECLINING_THRESHOLD: 40.0,
    COGNITIVE_LOAD_HIGH_THRESHOLD: 70.0,
  };

  function evaluateOverinvestment(subscales, passion, dailySignals) {
    // Identify thriving domains
    var thriving = [];
    var domains = ["ambition","belonging","craft"];
    for (var i = 0; i < domains.length; i++) {
      var dk = domains[i].charAt(0);
      var sat = subscales[dk + "_sat"];
      var frust = subscales[dk + "_frust"];
      if (sat !== undefined && frust !== undefined &&
          sat >= OVERINVEST.SAT_THRIVING_THRESHOLD &&
          frust < OVERINVEST.FRUST_LOW_THRESHOLD) {
        thriving.push(domains[i]);
      }
    }
    var abcPattern = thriving.length >= 2;

    var crossConcern = null;
    if (dailySignals) {
      crossConcern = (dailySignals.recovery_slope < OVERINVEST.RECOVERY_DECLINING_THRESHOLD &&
                      dailySignals.cognitive_load > OVERINVEST.COGNITIVE_LOAD_HIGH_THRESHOLD);
    }

    var shouldEscalate = abcPattern && (crossConcern === true || crossConcern === null);
    var triggered, path, recommendation, rationale;

    if (!shouldEscalate) {
      triggered = false; path = "not_triggered"; recommendation = null;
      rationale = !abcPattern
        ? "no overinvestment pattern; fewer than two domains thriving"
        : "two or more domains thriving, recovery signals clear";
    } else if (!passion.recommendation_gate_passed) {
      triggered = true; path = "insufficient_evidence"; recommendation = "watch";
      rationale = "overinvestment pattern present but passion leaning is unclear: " + passion.gate_reason;
    } else if (passion.leaning === "harmonious") {
      triggered = true; path = "harmonious"; recommendation = "protect_recovery";
      rationale = "thriving pattern with harmonious leaning; protect recovery without reducing engagement";
    } else if (passion.leaning === "obsessive") {
      triggered = true; path = "obsessive"; recommendation = "identity_conversation";
      rationale = "thriving pattern with obsessive leaning; check for identity capture and conflict with other life domains";
    } else if (passion.leaning === "mixed") {
      triggered = true; path = "mixed"; recommendation = "check_conflict";
      rationale = "thriving pattern with both harmonious and obsessive elevated; intensity is real, check for underlying conflict";
    } else {
      triggered = true; path = "insufficient_evidence"; recommendation = "watch";
      rationale = "thriving pattern present but passion leaning is " + passion.leaning;
    }

    return {
      triggered: triggered, path: path,
      thriving_domains: thriving,
      cross_signal_present: dailySignals !== undefined && dailySignals !== null,
      cross_signal_concern: crossConcern,
      coach_recommendation: recommendation,
      rationale: rationale,
    };
  }

  // ===========================================================================
  // 16.1 REGULATORY STYLE + EROSION
  // ===========================================================================

  var REGULATORY = {
    DOMAIN_ITEMS: { ambition: ["AR1","AR2"], belonging: ["BR1","BR2"], craft: ["CR1","CR2"] },
    STYLE_ELEVATED_THRESHOLD: 5.0,
    STYLE_AMBIGUOUS_MARGIN: 1.0,
    STYLE_RANK: { identified: 3, conflicted: 2, introjected: 1, amotivated: 0, not_computed: -1 },
  };

  function _scoreDomainRegulation(responses, autoCode, ctrlCode) {
    var autoPresent = responses[autoCode] !== undefined && responses[autoCode] !== null;
    var ctrlPresent = responses[ctrlCode] !== undefined && responses[ctrlCode] !== null;
    if (!autoPresent || !ctrlPresent) {
      var missing = [];
      if (!autoPresent) missing.push(autoCode);
      if (!ctrlPresent) missing.push(ctrlCode);
      return {
        autonomous_score: null, controlled_score: null, rai: null,
        style: "not_computed",
        display_gate_passed: false, recommendation_gate_passed: false,
        gate_reason: "missing item(s): " + missing.join(", "),
      };
    }
    var autoS = normalize10(responses[autoCode]);
    var ctrlS = normalize10(responses[ctrlCode]);
    var rai = autoS - ctrlS;

    var autoElev = autoS >= REGULATORY.STYLE_ELEVATED_THRESHOLD;
    var ctrlElev = ctrlS >= REGULATORY.STYLE_ELEVATED_THRESHOLD;
    var style;
    if (autoElev && !ctrlElev) style = "identified";
    else if (autoElev && ctrlElev) style = "conflicted";
    else if (!autoElev && ctrlElev) style = "introjected";
    else style = "amotivated";

    var autoMargin = Math.abs(autoS - REGULATORY.STYLE_ELEVATED_THRESHOLD);
    var ctrlMargin = Math.abs(ctrlS - REGULATORY.STYLE_ELEVATED_THRESHOLD);
    var recPass = (autoMargin >= REGULATORY.STYLE_AMBIGUOUS_MARGIN && ctrlMargin >= REGULATORY.STYLE_AMBIGUOUS_MARGIN);
    var reason = recPass ? "recommendation gate passed" : "one or both scores too close to the style boundary";

    return {
      autonomous_score: autoS, controlled_score: ctrlS, rai: rai, style: style,
      display_gate_passed: true, recommendation_gate_passed: recPass, gate_reason: reason,
    };
  }

  function scoreRegulatoryStyle(responses) {
    var domains = {};
    var doms = ["ambition","belonging","craft"];
    var itemsAnswered = 0;
    for (var i = 0; i < doms.length; i++) {
      var pair = REGULATORY.DOMAIN_ITEMS[doms[i]];
      domains[doms[i]] = _scoreDomainRegulation(responses, pair[0], pair[1]);
      if (responses[pair[0]] !== undefined) itemsAnswered++;
      if (responses[pair[1]] !== undefined) itemsAnswered++;
    }
    return { domains: domains, items_answered: itemsAnswered };
  }

  function detectRegulationErosion(profileHistory) {
    if (profileHistory.length < 2) return [];
    var doms = ["ambition","belonging","craft"];
    var events = [];
    for (var d = 0; d < doms.length; d++) {
      var domain = doms[d];
      var styles = [];
      for (var i = 0; i < profileHistory.length; i++) {
        styles.push(profileHistory[i].domains[domain].style);
      }
      var computable = styles.filter(function (s) { return s !== "not_computed"; });
      var fired = false, lookback = 0;
      if (computable.length >= 3) {
        var recent3 = computable.slice(-3);
        var ranks3 = recent3.map(function (s) { return REGULATORY.STYLE_RANK[s]; });
        var monotonic = ranks3[2] <= ranks3[1] && ranks3[1] <= ranks3[0];
        var netDrop = ranks3[2] < ranks3[0];
        fired = monotonic && netDrop; lookback = 3;
      } else if (computable.length === 2) {
        var ranks2 = computable.map(function (s) { return REGULATORY.STYLE_RANK[s]; });
        fired = ranks2[1] < ranks2[0]; lookback = 2;
      }
      if (fired) {
        events.push({
          domain: domain,
          style_series: styles,
          rank_series: styles.map(function (s) { return REGULATORY.STYLE_RANK[s]; }),
          lookback: lookback,
        });
      }
    }
    return events;
  }

  // ===========================================================================
  // 16.7 SELF-CONCORDANCE + TRAJECTORY
  // ===========================================================================

  var SC = {
    AUTONOMOUS_ITEMS: ["SC3","SC4"],
    CONTROLLED_ITEMS: ["SC1","SC2"],
    ALL_ITEMS: ["SC1","SC2","SC3","SC4"],
    LEANING_THRESHOLD: 3.0,
    ELEVATED_THRESHOLD: 5.0,
    DISPLAY_MIN_TOTAL: 3,
  };

  function scoreSelfConcordance(responses, goalText) {
    var auto = _present(responses, SC.AUTONOMOUS_ITEMS);
    var ctrl = _present(responses, SC.CONTROLLED_ITEMS);
    var itemsAnswered = auto.length + ctrl.length;

    if (itemsAnswered < SC.DISPLAY_MIN_TOTAL || auto.length < 1 || ctrl.length < 1) {
      return {
        autonomous_score: null, controlled_score: null,
        self_concordance: null, leaning: "not_computed",
        items_answered: itemsAnswered,
        display_gate_passed: false, recommendation_gate_passed: false,
        gate_reason: "need at least " + SC.DISPLAY_MIN_TOTAL +
          " items with both subscales represented; got " + itemsAnswered +
          " total, autonomous=" + auto.length + ", controlled=" + ctrl.length,
        goal_text: goalText || null,
      };
    }
    var autoS = normalize10(_mean(auto));
    var ctrlS = normalize10(_mean(ctrl));
    var sc = autoS - ctrlS;

    var leaning;
    if (sc >= SC.LEANING_THRESHOLD && autoS >= SC.ELEVATED_THRESHOLD) leaning = "autonomous";
    else if (sc <= -SC.LEANING_THRESHOLD && ctrlS >= SC.ELEVATED_THRESHOLD) leaning = "controlled";
    else leaning = "mixed";

    var allAnsweredSC = itemsAnswered === SC.ALL_ITEMS.length;
    var clearLeaning = leaning === "autonomous" || leaning === "controlled";
    var recPass = allAnsweredSC && clearLeaning;
    var reason;
    if (recPass) reason = "recommendation gate passed";
    else if (!allAnsweredSC) reason = itemsAnswered + " of 4 items answered; recommendation gate requires all four";
    else reason = "all items answered but no clear autonomous or controlled lean";

    return {
      autonomous_score: autoS, controlled_score: ctrlS,
      self_concordance: sc, leaning: leaning,
      items_answered: itemsAnswered,
      display_gate_passed: true, recommendation_gate_passed: recPass,
      gate_reason: reason, goal_text: goalText || null,
    };
  }

  var SC_TRAJ = {
    MIN_POINTS_FOR_TRAJECTORY: 3,
    FLAT_SLOPE_TOLERANCE: 0.5,
    OSCILLATION_SD_THRESHOLD: 2.5,
    DIRECTIONAL_MAGNITUDE_THRESHOLD: 1.0,
  };

  function _classifyTrajectoryLabel(slope, magnitude, sd) {
    if (sd >= SC_TRAJ.OSCILLATION_SD_THRESHOLD &&
        Math.abs(magnitude) < SC_TRAJ.DIRECTIONAL_MAGNITUDE_THRESHOLD) {
      return ["oscillating", "flat"];
    }
    if (Math.abs(slope) < SC_TRAJ.FLAT_SLOPE_TOLERANCE &&
        Math.abs(magnitude) < SC_TRAJ.DIRECTIONAL_MAGNITUDE_THRESHOLD) {
      return ["stable", "flat"];
    }
    if (magnitude >= SC_TRAJ.DIRECTIONAL_MAGNITUDE_THRESHOLD && slope > 0) {
      return ["becoming_more_autonomous", "rising"];
    }
    if (magnitude <= -SC_TRAJ.DIRECTIONAL_MAGNITUDE_THRESHOLD && slope < 0) {
      return ["becoming_more_controlled", "falling"];
    }
    return ["stable", "flat"];
  }

  function computeGoalTrajectory(points) {
    if (!points || !points.length) return null;
    var goalIds = {};
    for (var i = 0; i < points.length; i++) goalIds[points[i].goal_id] = true;
    var ids = Object.keys(goalIds);
    if (ids.length > 1) throw new Error("all points must share the same goal_id");
    var goalId = ids[0];
    var nTotal = points.length;
    var computable = points.filter(function (p) {
      return p.profile.display_gate_passed && p.profile.self_concordance !== null;
    });
    var nComp = computable.length;
    if (nComp < SC_TRAJ.MIN_POINTS_FOR_TRAJECTORY) {
      var latest = nComp ? computable[nComp - 1].profile.self_concordance : null;
      return {
        goal_id: goalId, n_points_total: nTotal, n_points_computable: nComp,
        slope: null, magnitude: null, within_series_sd: null,
        direction: "insufficient_data", label: "insufficient_data",
        latest_self_concordance: latest,
      };
    }
    var xs = computable.map(function (p) { return p.cycle_index; });
    var ys = computable.map(function (p) { return p.profile.self_concordance; });
    var slope = _olsSlope(xs, ys);
    var magnitude = ys[ys.length - 1] - ys[0];
    var sd = _stdev(ys);
    var ld = _classifyTrajectoryLabel(slope, magnitude, sd);
    return {
      goal_id: goalId, n_points_total: nTotal, n_points_computable: nComp,
      slope: slope, magnitude: magnitude, within_series_sd: sd,
      direction: ld[1], label: ld[0],
      latest_self_concordance: ys[ys.length - 1],
    };
  }

  // ===========================================================================
  // 16.5 GROUP-CONSCIOUS + DISPERSION
  // ===========================================================================

  var GC = {
    COLLECTIVE: { ambition: "AG1", belonging: "BG1", craft: "CG1" },
    TI_ITEMS: ["TI1","TI2"],
    LEVEL_HIGH_THRESHOLD: 7.0,
    LEVEL_MODERATE_THRESHOLD: 4.0,
    EMPATHIC_RISK_TI_MIN: 6.0,
    EMPATHIC_RISK_COLLECTIVE_MAX: 4.0,
    DISPERSION_TIGHT: 1.5,
    DISPERSION_HIGH: 2.5,
    DISPERSION_MIN_ATHLETES: 3,
  };

  function _level(score) {
    if (score === null || score === undefined) return "not_computed";
    if (score >= GC.LEVEL_HIGH_THRESHOLD) return "high";
    if (score >= GC.LEVEL_MODERATE_THRESHOLD) return "moderate";
    return "low";
  }

  function scoreGroupConscious(responses) {
    var collective = {};
    var doms = ["ambition","belonging","craft"];
    var answered = 0;
    for (var i = 0; i < doms.length; i++) {
      var dom = doms[i];
      var code = GC.COLLECTIVE[dom];
      var raw = responses[code];
      if (raw === undefined || raw === null) {
        collective[dom] = { domain: dom, score: null, level: "not_computed",
          display_gate_passed: false, recommendation_gate_passed: false,
          gate_reason: "missing item " + code };
      } else {
        var s = normalize10(raw);
        collective[dom] = { domain: dom, score: s, level: _level(s),
          display_gate_passed: true, recommendation_gate_passed: true, gate_reason: "ok" };
        answered++;
      }
    }
    var tiPresent = _present(responses, GC.TI_ITEMS);
    var ti;
    if (tiPresent.length === 0) {
      ti = { score: null, level: "not_computed", items_answered: 0,
        display_gate_passed: false, recommendation_gate_passed: false,
        gate_reason: "no team identification items answered" };
    } else {
      var tiScore = normalize10(_mean(tiPresent));
      var tiRecPass = tiPresent.length === GC.TI_ITEMS.length;
      ti = { score: tiScore, level: _level(tiScore), items_answered: tiPresent.length,
        display_gate_passed: true, recommendation_gate_passed: tiRecPass,
        gate_reason: tiRecPass ? "recommendation gate passed" : "only one of two team-identification items answered" };
    }
    answered += tiPresent.length;

    var empathicRisk = [];
    if (ti.score !== null && ti.score >= GC.EMPATHIC_RISK_TI_MIN) {
      for (var j = 0; j < doms.length; j++) {
        var d = doms[j];
        if (collective[d].score !== null && collective[d].score < GC.EMPATHIC_RISK_COLLECTIVE_MAX) {
          empathicRisk.push(d);
        }
      }
    }

    return {
      collective: collective, team_identification: ti,
      empathic_risk_domains: empathicRisk, items_answered: answered,
    };
  }

  function _dispersionBand(sd) {
    if (sd < GC.DISPERSION_TIGHT) return "tight";
    if (sd < GC.DISPERSION_HIGH) return "moderate";
    return "high";
  }

  function computeTeamDispersion(athleteSubscales) {
    var n = athleteSubscales.length;
    if (n < GC.DISPERSION_MIN_ATHLETES) {
      return { team_size: n, subscale_sds: {}, subscale_bands: {},
        high_dispersion_subscales: [], computed: false,
        reason: "fewer than " + GC.DISPERSION_MIN_ATHLETES + " athletes; dispersion not computed" };
    }
    var keys = ["a_sat","a_frust","b_sat","b_frust","c_sat","c_frust"];
    var sds = {}, bands = {}, highDisp = [];
    for (var k = 0; k < keys.length; k++) {
      var key = keys[k];
      var values = [];
      for (var a = 0; a < n; a++) if (athleteSubscales[a][key] !== undefined) values.push(athleteSubscales[a][key]);
      if (values.length >= GC.DISPERSION_MIN_ATHLETES) {
        var sd = _stdev(values);
        sds[key] = sd;
        bands[key] = _dispersionBand(sd);
        if (bands[key] === "high") highDisp.push(key);
      }
    }
    return { team_size: n, subscale_sds: sds, subscale_bands: bands,
      high_dispersion_subscales: highDisp, computed: true, reason: "dispersion computed" };
  }

  // ===========================================================================
  // 16.6 CAUSALITY ORIENTATIONS
  // ===========================================================================

  var CAUS = {
    ITEMS: { autonomy: ["AO1","AO2","AO3","AO4"],
             controlled: ["CO1","CO2","CO3","CO4"],
             impersonal: ["IO1","IO2","IO3","IO4"] },
    TOTAL_ITEM_COUNT: 12,
    DISPLAY_MIN_TOTAL: 8,
    DISPLAY_MIN_PER_SUBSCALE: 2,
    DOMINANT_SCORE_THRESHOLD: 6.0,
    DOMINANT_MARGIN: 1.5,
    EMERGENT_CEILING: 4.0,
  };

  function _classifyDominantOrientation(autonomy, controlled, impersonal) {
    var scored = [["autonomy", autonomy], ["controlled", controlled], ["impersonal", impersonal]];
    scored.sort(function (a, b) { return b[1] - a[1]; });
    var top = scored[0], second = scored[1];
    if (top[1] < CAUS.EMERGENT_CEILING) return "emergent";
    if (top[1] >= CAUS.DOMINANT_SCORE_THRESHOLD && (top[1] - second[1]) >= CAUS.DOMINANT_MARGIN) return top[0];
    return "mixed";
  }

  function scoreCausalityOrientations(responses) {
    var subs = {};
    var counts = {};
    var totalAnswered = 0;
    var subNames = ["autonomy","controlled","impersonal"];
    for (var i = 0; i < subNames.length; i++) {
      var sn = subNames[i];
      var present = _present(responses, CAUS.ITEMS[sn]);
      counts[sn] = present.length;
      subs[sn] = present.length ? normalize10(_mean(present)) : null;
      totalAnswered += present.length;
    }
    var minPer = Math.min(counts.autonomy, counts.controlled, counts.impersonal);
    if (totalAnswered < CAUS.DISPLAY_MIN_TOTAL || minPer < CAUS.DISPLAY_MIN_PER_SUBSCALE) {
      return {
        autonomy_score: null, controlled_score: null, impersonal_score: null,
        dominant: "not_computed", items_answered: totalAnswered,
        display_gate_passed: false, recommendation_gate_passed: false,
        gate_reason: "need at least " + CAUS.DISPLAY_MIN_TOTAL + " items total and " +
          CAUS.DISPLAY_MIN_PER_SUBSCALE + " per subscale; got " + totalAnswered +
          " total and min-per-subscale " + minPer,
      };
    }
    var dominant = _classifyDominantOrientation(subs.autonomy, subs.controlled, subs.impersonal);
    var allAnsweredCO = totalAnswered === CAUS.TOTAL_ITEM_COUNT;
    var clearDominant = dominant === "autonomy" || dominant === "controlled" || dominant === "impersonal";
    var recPass = allAnsweredCO && clearDominant;
    var reason;
    if (recPass) reason = "recommendation gate passed";
    else if (!allAnsweredCO) reason = totalAnswered + " of " + CAUS.TOTAL_ITEM_COUNT + " items answered; recommendation gate requires all twelve";
    else reason = "all items answered but no single orientation clearly dominant";
    return {
      autonomy_score: subs.autonomy, controlled_score: subs.controlled, impersonal_score: subs.impersonal,
      dominant: dominant, items_answered: totalAnswered,
      display_gate_passed: true, recommendation_gate_passed: recPass, gate_reason: reason,
    };
  }

  // ===========================================================================
  // 16.3 COACH CIRCUMPLEX
  // ===========================================================================

  var CIRCUMPLEX = {
    FACET_ITEMS: {
      autonomy_support: ["CXA1","CXA2","CXA3","CXA4","CXA5"],
      structure: ["CXS1","CXS2","CXS3","CXS4","CXS5"],
      relatedness_support: ["CXR1","CXR2","CXR3","CXR4","CXR5"],
      controlling: ["CXC1","CXC2","CXC3","CXC4","CXC5"],
      chaos: ["CXH1","CXH2","CXH3","CXH4"],
    },
    SUPPORTIVE_FACETS: ["autonomy_support","structure","relatedness_support"],
    THWARTING_FACETS: ["controlling","chaos"],
    DISPLAY_MIN_ITEMS_PER_FACET: 3,
    COMPOSITE_SUPPORT_HIGH: 6.0,
    COMPOSITE_THWART_HIGH: 4.0,
    GAP_FLAG_THRESHOLD: 2.0,
    AGGREGATE_MIN_RATERS: 3,
  };

  function _facetLevel(facetName, score) {
    if (score === null || score === undefined) return "not_computed";
    if (CIRCUMPLEX.SUPPORTIVE_FACETS.indexOf(facetName) >= 0) {
      if (score >= 7.0) return "high";
      if (score >= 4.5) return "moderate";
      return "low";
    }
    // thwarting facets
    if (score >= 5.0) return "high";
    if (score >= 3.0) return "moderate";
    return "low";
  }

  function _scoreFacet(facetName, responses) {
    var codes = CIRCUMPLEX.FACET_ITEMS[facetName];
    var present = _present(responses, codes);
    if (present.length < CIRCUMPLEX.DISPLAY_MIN_ITEMS_PER_FACET) {
      return { score: null, items_answered: present.length, level: "not_computed",
        display_gate_passed: false, recommendation_gate_passed: false,
        gate_reason: "fewer than " + CIRCUMPLEX.DISPLAY_MIN_ITEMS_PER_FACET + " items answered for facet '" + facetName + "'" };
    }
    var s = normalize10(_mean(present));
    var recPass = present.length === codes.length;
    return { score: s, items_answered: present.length, level: _facetLevel(facetName, s),
      display_gate_passed: true,
      recommendation_gate_passed: recPass,
      gate_reason: recPass ? "recommendation gate passed" : present.length + " of " + codes.length + " items answered; full facet needed" };
  }

  function _classifyDominantApproach(supportive, thwarting) {
    if (supportive === null || thwarting === null) return "not_computed";
    var sH = supportive >= CIRCUMPLEX.COMPOSITE_SUPPORT_HIGH;
    var tH = thwarting >= CIRCUMPLEX.COMPOSITE_THWART_HIGH;
    if (sH && !tH) return "supportive";
    if (sH && tH) return "mixed";
    if (!sH && !tH) return "under-structured";
    return "thwarting";
  }

  function scoreCircumplex(responses, rater) {
    var facets = {};
    var supScores = [];
    var thwScores = [];
    var facetNames = Object.keys(CIRCUMPLEX.FACET_ITEMS);
    for (var i = 0; i < facetNames.length; i++) {
      var fn = facetNames[i];
      var fs = _scoreFacet(fn, responses);
      facets[fn] = fs;
      if (fs.score !== null) {
        if (CIRCUMPLEX.SUPPORTIVE_FACETS.indexOf(fn) >= 0) supScores.push(fs.score);
        else thwScores.push(fs.score);
      }
    }
    var supportive = supScores.length >= 2 ? _mean(supScores) : null;
    var thwarting = thwScores.length >= 1 ? _mean(thwScores) : null;
    return {
      rater: rater || "coach_self",
      facets: facets,
      need_supportive: supportive,
      need_thwarting: thwarting,
      dominant_approach: _classifyDominantApproach(supportive, thwarting),
    };
  }

  function aggregateAthleteRatings(responsesByAthlete) {
    var allCodes = [];
    var fnames = Object.keys(CIRCUMPLEX.FACET_ITEMS);
    for (var i = 0; i < fnames.length; i++) allCodes = allCodes.concat(CIRCUMPLEX.FACET_ITEMS[fnames[i]]);
    var valid = responsesByAthlete.filter(function (r) {
      for (var c = 0; c < allCodes.length; c++) if (r[allCodes[c]] !== undefined) return true;
      return false;
    });
    if (valid.length < CIRCUMPLEX.AGGREGATE_MIN_RATERS) return null;
    var aggregated = {};
    for (var c2 = 0; c2 < allCodes.length; c2++) {
      var code = allCodes[c2];
      var values = [];
      for (var v = 0; v < valid.length; v++) if (valid[v][code] !== undefined) values.push(valid[v][code]);
      if (values.length) aggregated[code] = _roundHalfToEven(_mean(values));
    }
    return scoreCircumplex(aggregated, "athlete_of_coach");
  }

  function computeCircumplexGaps(coachSelf, athleteAgg) {
    if (!coachSelf || !athleteAgg) return [];
    if (coachSelf.rater !== "coach_self") throw new Error("coach_self profile must have rater='coach_self'");
    if (athleteAgg.rater !== "athlete_of_coach") throw new Error("athlete_aggregate profile must have rater='athlete_of_coach'");
    var gaps = [];
    var fnames = Object.keys(CIRCUMPLEX.FACET_ITEMS);
    for (var i = 0; i < fnames.length; i++) {
      var fn = fnames[i];
      var c = coachSelf.facets[fn].score;
      var a = athleteAgg.facets[fn].score;
      if (c === null || a === null) continue;
      var diff = c - a;
      var flagged = Math.abs(diff) > CIRCUMPLEX.GAP_FLAG_THRESHOLD;
      var direction = diff > CIRCUMPLEX.GAP_FLAG_THRESHOLD ? "coach_higher"
                    : (diff < -CIRCUMPLEX.GAP_FLAG_THRESHOLD ? "athlete_higher" : "aligned");
      gaps.push({ facet: fn, coach_self_score: c, athlete_aggregate_score: a,
        gap: diff, flagged: flagged, direction: direction });
    }
    return gaps;
  }

  // ===========================================================================
  // NARRATIVES (verbatim from narrative_engine.py)
  // ===========================================================================

  var DOMAIN_PLAIN = {
    ambition: { athlete_target: "your goals", athlete_verb: "chase", coach_target: "goal pursuit" },
    belonging: { athlete_target: "your teammates", athlete_verb: "invest in", coach_target: "team relationships" },
    craft: { athlete_target: "your skills", athlete_verb: "work on", coach_target: "skill development" },
  };

  var NARR = {};

  // --- 1. Passion ---
  NARR.passion = {
    harmonious: {
      athlete: { summary: "Your drive stays in balance with the rest of your life. You can step back when you need to, and come back when you want to. That is a strong foundation.", reflection_prompt: "When was the last time you took a full day off without feeling like you were losing something?" },
      coach: { summary: "The athlete can step away from sport without losing their sense of self. Drive is high and healthy. Protect recovery; do not restrict engagement.", conversation_starter: "Ask what the athlete wants the training week to give them. A clear answer is a sign of flexible commitment." },
    },
    obsessive: {
      athlete: { summary: "You find it hard to step away from sport, even when you need a break. The drive is real. It is also carrying a cost. That is worth a conversation.", reflection_prompt: "What does a day without training feel like for you right now? What do you notice in yourself?" },
      coach: { summary: "The athlete has trouble stepping away from sport. Drive is high but it carries cost to other parts of life. An identity-level conversation is warranted, not a training adjustment.", conversation_starter: "Ask what a week off would cost the athlete. Listen for whether the answer is about performance or about self." },
    },
    mixed: {
      athlete: { summary: "You bring intense commitment. Some of it lifts you. Some of it weighs on you. Both are real.", reflection_prompt: "Which parts of your training week give you energy, and which parts take it?" },
      coach: { summary: "Both the healthy and the costly forms of commitment are elevated. Intensity is real. Check for underlying conflict before acting on the signal.", conversation_starter: "Ask what the training week gives the athlete, and what it takes from them. Both answers matter." },
    },
    uninvested: {
      athlete: { summary: "Sport is not a strong source of energy right now. That is not a problem to solve. It is a signal about where your drive sits today.", reflection_prompt: "What does pull on you right now, if not sport?" },
      coach: { summary: "Sport is not carrying strong positive or negative charge for this athlete. Investigate other drivers before reading this as burnout.", conversation_starter: "Ask what the athlete is looking forward to outside of sport. A flat answer here points to something broader." },
    },
    insufficient_signal: {
      athlete: { summary: "Too early to say which way this is leaning. A few more check-ins will sharpen the picture.", reflection_prompt: "No action needed yet. Keep checking in." },
      coach: { summary: "Signal too weak to act on. Hold for another cycle.", conversation_starter: "No action needed. Revisit after the next check-in." },
    },
    not_computed: {
      athlete: { summary: "Not enough check-in answers yet to say how this is sitting for you.", reflection_prompt: "Complete the full check-in next time for a clearer read." },
      coach: { summary: "Not enough answers yet. Hold for another cycle.", conversation_starter: "No action needed. Make sure the athlete completes the full check-in next cycle." },
    },
  };

  // --- 2. Overinvestment ---
  NARR.overinvestment = {
    harmonious: { athlete: "Your drive in training is strong right now. A rest day this week is part of the plan, not a setback.", coach: "This athlete is pushing hard from a healthy place. Protect recovery without restricting engagement. A light week is maintenance, not demotion." },
    obsessive: { athlete: "Your drive is high, and you are finding it hard to step back. That tension is worth a conversation, not a harder week.", coach: "This athlete is pushing hard from a place of tension. A one-to-one that is not about performance is the action. Check whether they feel they can step back without losing standing on the team." },
    mixed: { athlete: "You are pushing hard. Some of that is lifting you, some of it is costing you. Worth pausing to notice which is which.", coach: "The athlete shows both healthy and costly commitment at once. Ask what the training week gives them, and what it takes from them." },
    insufficient_evidence: { athlete: "We do not have enough to say yet. Keep checking in.", coach: "Thriving pattern is present but passion leaning is not clear yet. Watch for another cycle before acting." },
    not_triggered: { athlete: "Nothing flagged on the overinvestment side right now.", coach: "No overinvestment trigger for this athlete in this cycle." },
  };

  // --- 3. Regulatory ---
  NARR.regulatory = {
    identified: { athlete: "You {verb} {target} because they genuinely matter to you. That is the strongest kind of drive. It holds up when things get hard.",
                  coach: "In {target}, the athlete's drive is values-based. It tends to hold up when things get hard. Keep offering reasons and choices. Avoid pressure tactics; they weaken ownership." },
    conflicted: { athlete: "You {verb} {target} for real reasons, and also because you feel you have to. Both are true at the same time. That mix is workable, but the pressure side is worth naming.",
                  coach: "The athlete values {target} and also feels pressure here. The source of the pressure is worth naming in a one-to-one. When things get hard, the pressure side tends to break the engagement." },
    introjected: { athlete: "You {verb} {target} more out of pressure than out of want. That can still produce effort, but it tends to wear down. Worth a look at where the pressure is coming from.",
                   coach: "In {target}, the athlete's drive runs on obligation or image, not on real value. That is a thin foundation. A conversation about what the athlete actually wants from this part of their life is the action." },
    amotivated: { athlete: "You are not feeling much pull toward {target} right now, either from inside or from outside. That is worth noticing. It does not have to be a problem, but it is a signal.",
                  coach: "The athlete is disengaged in {target}: neither values nor pressure is active. Investigate what changed. This is often an earlier warning than low satisfaction on its own." },
    not_computed: { athlete: "Not enough check-in answers yet for {target}. Complete both items next time for a clearer read.",
                    coach: "Not enough answers to read {target} motivation this cycle. Ensure the athlete completes both items next time." },
  };

  // --- 4. Erosion ---
  NARR.erosion = {
    athlete: "Something about {target} has shifted over the last few check-ins. The pull that was value-based is moving toward pressure-based. Worth a quiet look at what has changed around this part of your life.",
    coach: "Motivation in {target} is moving from values-based to pressure-based. This has shown up over the last two or three check-ins. The usual scores may still look healthy; this signal often moves first. A conversation that is not about performance is the action.",
  };

  // --- 5. Self-concordance trajectory ---
  NARR.scTrajectory = {
    becoming_more_autonomous: {
      athlete: "Your reasons for this goal are moving in a healthy direction over the last few check-ins. The goal is becoming more yours. Keep noticing what is drawing you in.",
      coach: "The athlete's reasons for this goal are shifting from pressure-based to values-based across recent cycles. Internalization is happening. Protect the conditions that are letting it happen; do not add external rewards or pressure now." },
    becoming_more_controlled: {
      athlete: "Your reasons for this goal are shifting toward pressure over the last few check-ins. Worth a quiet look at what changed. Sometimes the goal is right and the context is off.",
      coach: "The athlete's reasons for this goal are drifting from values-based to pressure-based across recent cycles. This is an early signal that often shows up before engagement drops. A non-performance conversation about the goal itself is the action." },
    stable: {
      athlete: "Your reasons for this goal are holding steady across the last few check-ins. That is the most common pattern and tells you the goal is settled, for now.",
      coach: "The athlete's reasons for this goal are stable across recent cycles. No movement to act on. Revisit when a new goal is set or context changes." },
    oscillating: {
      athlete: "Your reasons for this goal swing from cycle to cycle. That can mean the goal is contested for you, or that the context around it keeps changing. Worth a closer look at what is driving the swings.",
      coach: "The athlete's reasons for this goal swing across recent cycles without a clear direction. The goal may be contested or the context around it unstable. Ask what changes between weeks where the goal feels theirs and weeks where it does not." },
    insufficient_data: {
      athlete: "Not enough check-ins on this goal yet to read a trend. Two more cycles will give a useful picture.",
      coach: "Not enough cycles on this goal to compute a trajectory. Revisit after at least three completed check-ins on the same goal." },
  };

  // --- 6. Self-concordance per-cycle ---
  NARR.selfConcordance = {
    autonomous: {
      athlete: "This goal is yours. You are pursuing it because it matters to you and because the work itself draws you in. That kind of goal tends to hold up across setbacks and tends to lift well-being as you make progress on it.",
      coach: "The athlete's reasons for this goal are values-based and interest-based. Goals like this hold up under setback and tend to drive both performance and well-being. Protect the conditions that allow this; do not tie it to external rewards or pressure." },
    controlled: {
      athlete: "You are pursuing this goal more because of pressure than because it fits you. Pressure goals can produce real effort, but progress on them does not lift well-being the way self-chosen goals do. Worth a look at whether to keep, reframe, or release this one.",
      coach: "The athlete's reasons here are pressure-based or obligation-based. Even if the athlete makes progress, the well-being lift will be smaller than for a self-chosen goal. A conversation about whether to keep, reshape, or step away from the goal is the action." },
    mixed: {
      athlete: "You hold both kinds of reasons for this goal. Some of them fit you, some are pressure. That is workable. The pressure side is worth naming because it tends to grow under stress.",
      coach: "The athlete's reasons for this goal mix self-chosen and pressure-based. Watch under stress; the pressure side tends to take over. Help the athlete name the source of the pressure so it can be addressed directly." },
    not_computed: {
      athlete: "Not enough answers yet to read how this goal is sitting with you. Complete all four reasons next cycle for a clearer read.",
      coach: "Not enough data on the athlete's reasons for this goal. Ensure all four reasons are completed next cycle." },
  };

  // --- 7. Causality orientations ---
  NARR.causality = {
    autonomy: {
      athlete: "You tend to move through situations from your own sense of what you want. When something does not fit, you adjust. That is a resilient way to operate. It does not make every situation easy, but it tends to hold up under pressure.",
      coach: "This athlete reads situations as opportunities for choice. They tolerate coaching-style variation well and respond to reasons and options. Pressure tactics will not help them more than with other athletes, and may cost more." },
    controlled: {
      athlete: "You tend to read situations through what others expect from you. That can get a lot done. It also wears on you over time. Worth noticing when a choice is yours, not theirs.",
      coach: "This athlete reads situations as demands. They do well with clear expectations. They are also more exposed than other athletes to pressure tactics. Reasons, choice, and voice pay off more here than elsewhere." },
    impersonal: {
      athlete: "Situations often feel like they happen to you rather than through you. That is a read, not a fact. It shifts when one small thing in your week starts going to plan. Start with one controllable piece and build from there.",
      coach: "This athlete reads situations as beyond their own influence. They are at higher risk of checking out. They also respond less to pressure or choice alone. Start with structure and small, steady wins. Build choice in later." },
    mixed: {
      athlete: "You do not lean clearly one way. Sometimes you read situations as yours to shape, sometimes as something pushing on you. That is normal and tells you less than a clearer pattern would. Worth watching which one shows up when things get hard.",
      coach: "The athlete does not show one clear pattern. How you coach them will depend on which lens is active in the moment. Watch under pressure. That is when the dominant lens usually shows up." },
    emergent: {
      athlete: "No clear pattern is showing up yet. That is not a problem. A year or two of check-ins will sharpen the picture.",
      coach: "No clear orientation is reading from the data. This is common at first administration. Revisit at the next annual cycle." },
    not_computed: {
      athlete: "Not enough answers yet to read how you tend to approach situations. Complete the full screen at the next annual check-in.",
      coach: "Not enough data to score orientation. Ensure the full screen is completed at the next annual administration." },
  };

  // --- 8. Collective satisfaction ---
  NARR.collectiveSatisfaction = {
    ambition: {
      high: { athlete: "You see your teammates chasing their own goals with meaning. That reads as a healthy team climate for drive.", coach: "The athlete perceives their teammates' goals as meaningful to them. The team climate for drive is reading as healthy." },
      moderate: { athlete: "Your teammates' goals land as meaningful to them some of the time. Mixed picture.", coach: "The athlete's read of teammates' goal-meaning is mixed. Watch for which athletes carry the signal." },
      low: { athlete: "You are not seeing your teammates' goals as meaningful to them right now. That is worth noticing, even if your own drive is strong.", coach: "The athlete perceives teammates as disengaged from their own goals. Team climate for drive is a concern." },
      not_computed: { athlete: "Not enough check-in data on the team climate for this.", coach: "Insufficient data for this team climate signal." },
    },
    belonging: {
      high: { athlete: "You notice your teammates feeling connected to each other. That is a strong team climate for belonging.", coach: "The athlete perceives teammates as connected to each other. The team climate for belonging reads as healthy." },
      moderate: { athlete: "Your teammates seem connected to each other some of the time. Not a full picture yet.", coach: "The athlete's read of team connection is mixed. Could be fault lines inside the group." },
      low: { athlete: "You are not seeing strong connection among your teammates right now. That matters even if your own relationships are fine.", coach: "The athlete perceives teammates as disconnected from each other. Team climate for belonging is a concern." },
      not_computed: { athlete: "Not enough check-in data on the team climate for this.", coach: "Insufficient data for this team climate signal." },
    },
    craft: {
      high: { athlete: "You see your teammates growing in their skills. That reads as a healthy team climate for craft.", coach: "The athlete perceives teammates as developing. The team climate for skill growth reads as healthy." },
      moderate: { athlete: "Some of your teammates seem to be growing, others less so. Mixed picture on skill development.", coach: "The athlete's read of team skill development is mixed. Worth looking at which athletes feel stuck." },
      low: { athlete: "You are not seeing your teammates growing right now. Team climate for skill development is worth naming.", coach: "The athlete perceives teammates as stuck on skill development. Team climate for craft is a concern." },
      not_computed: { athlete: "Not enough check-in data on the team climate for this.", coach: "Insufficient data for this team climate signal." },
    },
  };

  // --- 9. Team identification ---
  NARR.teamIdentification = {
    high: { athlete: "This team feels like your team. Wins and losses land personally, and you see yourself as a real member.", coach: "The athlete identifies strongly with the team. That is a strength and also a pressure point: group events land harder when identification is this high." },
    moderate: { athlete: "You feel like part of this team some of the time. The connection is there, but not deep.", coach: "The athlete's bond with the team is in the middle range. Group events land, but not as hard as they do for someone who feels fully part of the team." },
    low: { athlete: "You are not feeling like a real member of this team right now. That is data, not a problem.", coach: "The athlete's team identification is low. Group events are unlikely to hit them as personal. Investigate whether this is by choice or by exclusion." },
    not_computed: { athlete: "Not enough check-in data yet on how you are feeling about the team overall.", coach: "Not enough data on how the athlete feels about the team yet." },
  };

  // --- 10. Empathic risk ---
  NARR.empathicRisk = {
    athlete: "You care about this team, and you are seeing your teammates struggle in one or more areas. That carries a weight even when your own check-in looks okay. Worth naming with your coach.",
    coach: "This athlete identifies strongly with the team and perceives teammates as struggling. They are exposed to a kind of carry-load that their personal scores may not show. Check in on what they are absorbing for the group.",
  };

  // --- 11. Team dispersion (coach only) ---
  NARR.teamDispersion = {
    tight: "Athletes on this team are experiencing things similarly. The team mean is the team. No hidden splits.",
    moderate: "Some spread across athletes on this team. Worth noticing which subscales show the spread; they are the places where the team mean hides a split.",
    high: "High spread across athletes on one or more subscales. The team mean is not the team: some athletes are thriving, some are struggling. The split itself is the story.",
  };

  // --- 12. Circumplex facet (coach only) ---
  NARR.circumplexFacet = {
    autonomy_support: {
      high: "Your athletes see you offering real choice, hearing them out, and explaining why. Keep watching for the moments when you move fast under pressure. That is where this slips.",
      moderate: "You give athletes some room to choose and some of the reasoning behind your calls, but not consistently. Pick one situation this week where you will name the reason out loud before you make the call.",
      low: "Your athletes are not experiencing much room for choice or input. The drills and decisions may still be right; the way they land is the issue. Start by asking one athlete for their read before a decision this week.",
      not_computed: "Not enough responses to read autonomy-support. Come back once the circumplex has more data.",
    },
    structure: {
      high: "Your athletes know what to expect from you. Expectations are clear, feedback is specific, and you follow through. The next edge is noticing when you push through a plan that is not working instead of adjusting it.",
      moderate: "Your structure is present but not consistent. One lever that usually moves this: make the goal of each session explicit in the first two minutes, every session, for a month.",
      low: "Your athletes are not getting clear expectations or specific feedback from you. Two habits usually fix this. State the goal of the session at the start. Name one specific thing in feedback, not a general judgment.",
      not_computed: "Not enough responses to read structure. Come back once the circumplex has more data.",
    },
    relatedness_support: {
      high: "Your athletes feel you care about them as people, not just as performers. That matters more than most coaches think. Protect it by guarding against days when you cut short the non-sport conversations.",
      moderate: "You show warmth sometimes and other times you stay on sport-only mode. Pick two athletes this week and ask each one something specific about their life outside sport.",
      low: "Your athletes are not experiencing you as someone who notices them beyond their performance. The fix is small and concrete: one non-sport question per athlete, one time per week, consistently.",
      not_computed: "Not enough responses to read relatedness-support. Come back once the circumplex has more data.",
    },
    controlling: {
      high: "Your athletes report pressure tactics from you: guilt, warmth withdrawal after a bad performance, or unfavorable comparisons. These tactics often work short-term and cost trust long-term. Pick one to catch yourself on this week.",
      moderate: "Controlling moments are showing up in your coaching. Not your whole style, more like episodes. Notice the trigger. Is it one athlete, one moment in the week, or one kind of pressure you are under?",
      low: "You are not showing much controlling behavior. Keep it that way when the season gets harder; this is the place pressure tactics tend to show up first.",
      not_computed: "Not enough responses to read controlling behavior. Come back once the circumplex has more data.",
    },
    chaos: {
      high: "Your athletes report inconsistency: changing plans without warning, dropped commitments, or reactions that shift day to day. This wears trust down quickly. Write down the next three commitments you make to an athlete and check you kept them.",
      moderate: "Chaos is showing up in patches. Often the source is one context: late-week practices, post-travel, high-stress weeks. Identify the pattern before trying to solve it.",
      low: "Your athletes experience you as consistent. That is a real strength that many coaches underestimate. Keep it.",
      not_computed: "Not enough responses to read consistency. Come back once the circumplex has more data.",
    },
  };

  // --- 13. Circumplex gap (coach only) ---
  NARR.circumplexGap = {
    autonomy_support: {
      coach_higher: "You see yourself as giving more choice and explanation than your athletes are reading. That gap is common and it is the place where one specific change (name the rationale out loud, or ask before deciding) tends to close it fast.",
      athlete_higher: "Your athletes read more choice and explanation from you than you give yourself credit for. That is a hidden strength. Protect the habits that are producing it.",
    },
    structure: {
      coach_higher: "You see your expectations and feedback as clearer than they are landing for athletes. The fix is usually repetition: state the goal at the start, name one specific piece of feedback each time.",
      athlete_higher: "Your athletes experience more clarity and follow-through from you than you are giving yourself credit for. Keep it.",
    },
    relatedness_support: {
      coach_higher: "You believe you are showing more care and interest in your athletes as people than they are feeling from you. This often closes with small signals: one non-sport question per athlete per week, consistently.",
      athlete_higher: "Your athletes feel you care about them as people more than you realize. That is real trust. Keep investing in the small signals that are building it.",
    },
    controlling: {
      coach_higher: "You report using more pressure than athletes report feeling. That is unusual. Either you are self-critical, or athletes are not naming what they experience. Worth a conversation that makes it safer for them to say so.",
      athlete_higher: "Your athletes experience more pressure from you than you realize. That is the most common blind spot in coaching. Pick one of the items your athletes rated high and watch yourself around it this week.",
    },
    chaos: {
      coach_higher: "You report more inconsistency in your coaching than your athletes experience. Unusual. Possibly they do not feel safe reporting, or you hold yourself to an exacting standard. Worth naming in a team conversation.",
      athlete_higher: "Your athletes experience more inconsistency from you than you are aware of. This is often context-specific: late-week, post-travel, or high-stress moments. Identify the trigger before you try to solve it.",
    },
  };

  // --- 14. Circumplex approach (coach only) ---
  NARR.circumplexApproach = {
    supportive: "Your profile sits in the need-supportive space. Athletes experience you as offering choice, structure, and warmth, with little pressure or chaos. The question for growth is not what to change, but which facet to deepen.",
    mixed: "Your profile is mixed: strong on support, and also showing meaningful pressure or chaos. Many coaches sit here. The work is to keep the support while naming the source of the controlling or inconsistent moments, one at a time.",
    "under-structured": "Your profile shows neither strong support nor strong pressure. Athletes experience you as present but neutral. The fastest move is to add one facet of support: rationales, specific feedback, or a non-sport question per athlete each week.",
    thwarting: "Your profile currently sits in the need-thwarting space. Athletes experience more pressure or chaos than support. This is worth taking seriously as a coaching-development priority, not as a judgment. The fix is usually one behavior at a time, starting with whichever facet is highest.",
    not_computed: "Not enough of the circumplex is filled in to give a profile summary yet. Once more responses are in, this will surface.",
  };

  // ===========================================================================
  // NARRATIVE GENERATORS
  // ===========================================================================

  function _fillRegulatoryTemplate(template, domain, audience) {
    var sub = DOMAIN_PLAIN[domain] || {};
    return template.replace(/\{verb\}/g, sub.athlete_verb || "")
                   .replace(/\{target\}/g, audience === "coach" ? (sub.coach_target || "") : (sub.athlete_target || ""));
  }

  function generatePassionNarrative(leaning, audience) {
    var d = NARR.passion[leaning] || NARR.passion.not_computed;
    return d[audience] || d.athlete;
  }
  function generateOverinvestmentNarrative(path, audience) {
    var d = NARR.overinvestment[path] || NARR.overinvestment.not_triggered;
    return d[audience] || d.athlete;
  }
  function generateRegulatoryNarrative(domain, style, audience) {
    var t = NARR.regulatory[style] || NARR.regulatory.not_computed;
    var raw = t[audience] || t.athlete;
    return _fillRegulatoryTemplate(raw, domain, audience);
  }
  function generateErosionNarrative(domain, audience) {
    var raw = NARR.erosion[audience] || NARR.erosion.athlete;
    return _fillRegulatoryTemplate(raw, domain, audience);
  }
  function generateSelfConcordanceTrajectoryNarrative(label, audience) {
    var d = NARR.scTrajectory[label] || NARR.scTrajectory.insufficient_data;
    return d[audience] || d.athlete;
  }
  function generateSelfConcordanceNarrative(leaning, audience) {
    var d = NARR.selfConcordance[leaning] || NARR.selfConcordance.not_computed;
    return d[audience] || d.athlete;
  }
  function generateCausalityNarrative(orientation, audience) {
    var d = NARR.causality[orientation] || NARR.causality.not_computed;
    return d[audience] || d.athlete;
  }
  function generateCollectiveSatisfactionNarrative(domain, level, audience) {
    var domNarr = NARR.collectiveSatisfaction[domain];
    if (!domNarr) return "";
    var d = domNarr[level] || domNarr.not_computed;
    return d[audience] || d.athlete;
  }
  function generateTeamIdentificationNarrative(level, audience) {
    var d = NARR.teamIdentification[level] || NARR.teamIdentification.not_computed;
    return d[audience] || d.athlete;
  }
  function generateEmpathicRiskNarrative(audience) {
    return NARR.empathicRisk[audience] || NARR.empathicRisk.athlete;
  }
  function generateTeamDispersionNarrative(band) {
    return NARR.teamDispersion[band] || "";
  }
  function generateCircumplexFacetNarrative(facet, level) {
    var f = NARR.circumplexFacet[facet];
    if (!f) return "";
    return f[level] || f.not_computed;
  }
  function generateCircumplexGapNarrative(facet, direction) {
    var f = NARR.circumplexGap[facet];
    if (!f || direction === "aligned") return "";
    return f[direction] || "";
  }
  function generateCircumplexApproachNarrative(approach) {
    return NARR.circumplexApproach[approach] || NARR.circumplexApproach.not_computed;
  }

  // ===========================================================================
  // ORCHESTRATION
  // scoreAllOptionalLayers: feed flat responses dict, get per-layer scores back
  // renderOptionalLayersHTML: turn scores + audience into HTML for the results pane
  // ===========================================================================

  function _hasAnyResponses(responses, codes) {
    for (var i = 0; i < codes.length; i++) if (responses[codes[i]] !== undefined) return true;
    return false;
  }

  function scoreAllOptionalLayers(responses, opts) {
    opts = opts || {};
    var out = {};
    if (_hasAnyResponses(responses, LAYER_ITEMS.passion)) {
      out.passion = scorePassionQuality(responses);
      out.overinvestment = evaluateOverinvestment(opts.subscales || {}, out.passion, opts.dailySignals);
    }
    if (_hasAnyResponses(responses, LAYER_ITEMS.regulatory)) {
      out.regulatory = scoreRegulatoryStyle(responses);
      if (opts.regulatoryHistory && opts.regulatoryHistory.length) {
        out.erosion = detectRegulationErosion(opts.regulatoryHistory.concat([out.regulatory]));
      } else {
        out.erosion = [];
      }
    }
    if (_hasAnyResponses(responses, LAYER_ITEMS.groupConscious)) {
      out.groupConscious = scoreGroupConscious(responses);
    }
    if (_hasAnyResponses(responses, LAYER_ITEMS.selfConcordance)) {
      out.selfConcordance = scoreSelfConcordance(responses, opts.goalText);
      if (opts.selfConcordanceHistory && opts.selfConcordanceHistory.length) {
        var pts = opts.selfConcordanceHistory.concat([{
          goal_id: opts.goalId || "current_goal",
          cycle_index: opts.selfConcordanceHistory.length,
          profile: out.selfConcordance,
        }]);
        try { out.selfConcordanceTrajectory = computeGoalTrajectory(pts); } catch (e) { out.selfConcordanceTrajectory = null; }
      }
    }
    if (_hasAnyResponses(responses, LAYER_ITEMS.causality)) {
      out.causality = scoreCausalityOrientations(responses);
    }
    if (_hasAnyResponses(responses, LAYER_ITEMS.coachCircumplex)) {
      out.coachCircumplex = scoreCircumplex(responses, "coach_self");
    }
    return out;
  }

  // ----- HTML render helpers -----

  function _esc(s) {
    return String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }
  function _fmt(x) { return x === null || x === undefined ? "—" : Number(x).toFixed(1); }

  function _facetPretty(name) {
    return ({ autonomy_support: "Autonomy support", structure: "Structure",
              relatedness_support: "Relatedness support", controlling: "Controlling",
              chaos: "Chaos" })[name] || name;
  }

  function _renderPassionSection(passion, overinv, audience) {
    if (!passion) return "";
    var html = '<div class="opt-layer-card" style="border-left:4px solid #8b5cf6;">';
    html += '<h3 style="color:#6d28d9;margin-top:0;">Passion quality (16.2)</h3>';
    if (!passion.display_gate_passed) {
      html += '<p style="color:var(--muted);font-size:0.88rem;">' + _esc(passion.gate_reason) + '</p></div>';
      return html;
    }
    html += '<p style="font-size:0.85rem;color:var(--muted);">Harmonious: ' + _fmt(passion.hp_score) +
            ' &nbsp;|&nbsp; Obsessive: ' + _fmt(passion.op_score) +
            ' &nbsp;|&nbsp; Balance: ' + _fmt(passion.balance) + '</p>';
    html += '<p style="margin:0.5rem 0;"><strong>Leaning:</strong> ' + _esc(passion.leaning) + '</p>';
    var n = generatePassionNarrative(passion.leaning, audience);
    html += '<p style="line-height:1.55;">' + _esc(n.summary) + '</p>';
    if (audience === "athlete" && n.reflection_prompt) {
      html += '<div class="reflection-prompt" style="margin-top:0.5rem;font-size:0.88rem;">' + _esc(n.reflection_prompt) + '</div>';
    }
    if (audience === "coach" && n.conversation_starter) {
      html += '<div class="reflection-prompt" style="margin-top:0.5rem;font-size:0.88rem;">' + _esc(n.conversation_starter) + '</div>';
    }
    if (overinv && overinv.triggered) {
      html += '<div style="margin-top:1rem;padding:0.75rem;background:#fef3c7;border-radius:6px;">';
      html += '<strong style="color:#92400e;">Overinvestment trigger:</strong> ' + _esc(overinv.path) + '<br>';
      html += '<span style="font-size:0.88rem;">' + _esc(generateOverinvestmentNarrative(overinv.path, audience)) + '</span>';
      html += '</div>';
    }
    html += '</div>';
    return html;
  }

  function _renderRegulatorySection(reg, erosion, audience) {
    if (!reg) return "";
    var html = '<div class="opt-layer-card" style="border-left:4px solid #0ea5e9;">';
    html += '<h3 style="color:#0369a1;margin-top:0;">Regulatory style (16.1)</h3>';
    var doms = ["ambition","belonging","craft"];
    for (var i = 0; i < doms.length; i++) {
      var d = doms[i];
      var dom = reg.domains[d];
      html += '<div style="margin-bottom:0.75rem;">';
      html += '<strong>' + d.charAt(0).toUpperCase() + d.slice(1) + ':</strong> ';
      if (!dom.display_gate_passed) {
        html += '<span style="color:var(--muted);font-size:0.85rem;">' + _esc(dom.gate_reason) + '</span>';
      } else {
        html += _esc(dom.style) + ' (RAI ' + _fmt(dom.rai) + ')';
        html += '<div style="font-size:0.88rem;line-height:1.55;margin-top:0.3rem;">' + _esc(generateRegulatoryNarrative(d, dom.style, audience)) + '</div>';
      }
      html += '</div>';
    }
    if (erosion && erosion.length) {
      html += '<div style="margin-top:1rem;padding:0.75rem;background:#fee2e2;border-radius:6px;">';
      html += '<strong style="color:#991b1b;">Erosion detected:</strong> ' + erosion.map(function (e) { return e.domain; }).join(", ") + '<br>';
      for (var k = 0; k < erosion.length; k++) {
        html += '<span style="font-size:0.88rem;">' + _esc(generateErosionNarrative(erosion[k].domain, audience)) + '</span><br>';
      }
      html += '</div>';
    }
    html += '</div>';
    return html;
  }

  function _renderSelfConcordanceSection(sc, traj, audience) {
    if (!sc) return "";
    var html = '<div class="opt-layer-card" style="border-left:4px solid #14b8a6;">';
    html += '<h3 style="color:#0f766e;margin-top:0;">Goal self-concordance (16.7)</h3>';
    if (!sc.display_gate_passed) {
      html += '<p style="color:var(--muted);font-size:0.88rem;">' + _esc(sc.gate_reason) + '</p></div>';
      return html;
    }
    html += '<p style="font-size:0.85rem;color:var(--muted);">Autonomous: ' + _fmt(sc.autonomous_score) +
            ' &nbsp;|&nbsp; Controlled: ' + _fmt(sc.controlled_score) +
            ' &nbsp;|&nbsp; Self-concordance: ' + _fmt(sc.self_concordance) + '</p>';
    html += '<p style="margin:0.5rem 0;"><strong>Leaning:</strong> ' + _esc(sc.leaning) + '</p>';
    html += '<p style="line-height:1.55;">' + _esc(generateSelfConcordanceNarrative(sc.leaning, audience)) + '</p>';
    if (traj && traj.label !== "insufficient_data") {
      html += '<div style="margin-top:1rem;padding:0.75rem;background:#ccfbf1;border-radius:6px;">';
      html += '<strong>Trajectory:</strong> ' + _esc(traj.label) + ' (' + _esc(traj.direction) + ')<br>';
      html += '<span style="font-size:0.88rem;">' + _esc(generateSelfConcordanceTrajectoryNarrative(traj.label, audience)) + '</span>';
      html += '</div>';
    }
    html += '</div>';
    return html;
  }

  function _renderGroupConsciousSection(gc, audience) {
    if (!gc) return "";
    var html = '<div class="opt-layer-card" style="border-left:4px solid #f97316;">';
    html += '<h3 style="color:#c2410c;margin-top:0;">Team climate (16.5)</h3>';
    var doms = ["ambition","belonging","craft"];
    for (var i = 0; i < doms.length; i++) {
      var d = doms[i];
      var c = gc.collective[d];
      html += '<div style="margin-bottom:0.5rem;">';
      html += '<strong>Collective ' + d + ':</strong> ';
      if (!c.display_gate_passed) html += '<span style="color:var(--muted);font-size:0.85rem;">no data</span>';
      else html += _fmt(c.score) + ' (' + c.level + ') — <span style="font-size:0.88rem;">' + _esc(generateCollectiveSatisfactionNarrative(d, c.level, audience)) + '</span>';
      html += '</div>';
    }
    var ti = gc.team_identification;
    html += '<div style="margin-top:0.5rem;"><strong>Team identification:</strong> ';
    if (!ti.display_gate_passed) html += '<span style="color:var(--muted);font-size:0.85rem;">no data</span>';
    else html += _fmt(ti.score) + ' (' + ti.level + ')<br><span style="font-size:0.88rem;line-height:1.55;">' + _esc(generateTeamIdentificationNarrative(ti.level, audience)) + '</span>';
    html += '</div>';
    if (gc.empathic_risk_domains.length) {
      html += '<div style="margin-top:0.75rem;padding:0.6rem;background:#fef3c7;border-radius:6px;font-size:0.88rem;">';
      html += '<strong style="color:#92400e;">Empathic risk:</strong> ' + gc.empathic_risk_domains.join(", ") + '<br>';
      html += _esc(generateEmpathicRiskNarrative(audience));
      html += '</div>';
    }
    html += '</div>';
    return html;
  }

  function _renderCausalitySection(c, audience) {
    if (!c) return "";
    var html = '<div class="opt-layer-card" style="border-left:4px solid #a855f7;">';
    html += '<h3 style="color:#7e22ce;margin-top:0;">Causality orientations (16.6)</h3>';
    if (!c.display_gate_passed) {
      html += '<p style="color:var(--muted);font-size:0.88rem;">' + _esc(c.gate_reason) + '</p></div>';
      return html;
    }
    html += '<p style="font-size:0.85rem;color:var(--muted);">Autonomy: ' + _fmt(c.autonomy_score) +
            ' &nbsp;|&nbsp; Controlled: ' + _fmt(c.controlled_score) +
            ' &nbsp;|&nbsp; Impersonal: ' + _fmt(c.impersonal_score) + '</p>';
    html += '<p style="margin:0.5rem 0;"><strong>Dominant:</strong> ' + _esc(c.dominant) + '</p>';
    html += '<p style="line-height:1.55;">' + _esc(generateCausalityNarrative(c.dominant, audience)) + '</p>';
    html += '</div>';
    return html;
  }

  function _renderCircumplexSection(cx, athleteAggregate) {
    if (!cx) return "";
    var html = '<div class="opt-layer-card" style="border-left:4px solid #ef4444;">';
    html += '<h3 style="color:#b91c1c;margin-top:0;">Coach circumplex (16.3)</h3>';
    html += '<p style="font-size:0.85rem;color:var(--muted);">Need-supportive composite: ' + _fmt(cx.need_supportive) +
            ' &nbsp;|&nbsp; Need-thwarting composite: ' + _fmt(cx.need_thwarting) + '</p>';
    html += '<p style="margin:0.5rem 0;"><strong>Approach:</strong> ' + _esc(cx.dominant_approach) + '</p>';
    html += '<p style="line-height:1.55;">' + _esc(generateCircumplexApproachNarrative(cx.dominant_approach)) + '</p>';
    var fnames = Object.keys(CIRCUMPLEX.FACET_ITEMS);
    html += '<div style="margin-top:0.75rem;">';
    for (var i = 0; i < fnames.length; i++) {
      var fn = fnames[i];
      var f = cx.facets[fn];
      html += '<div style="margin-bottom:0.5rem;font-size:0.88rem;">';
      html += '<strong>' + _facetPretty(fn) + ':</strong> ';
      if (!f.display_gate_passed) html += '<span style="color:var(--muted);">' + _esc(f.gate_reason) + '</span>';
      else {
        html += _fmt(f.score) + ' (' + f.level + ')';
        var n = generateCircumplexFacetNarrative(fn, f.level);
        if (n) html += '<div style="font-size:0.85rem;line-height:1.5;margin-top:0.2rem;color:#555;">' + _esc(n) + '</div>';
      }
      html += '</div>';
    }
    html += '</div>';
    if (athleteAggregate) {
      var gaps = computeCircumplexGaps(cx, athleteAggregate);
      var flagged = gaps.filter(function (g) { return g.flagged; });
      if (flagged.length) {
        html += '<div style="margin-top:0.75rem;padding:0.75rem;background:#fee2e2;border-radius:6px;">';
        html += '<strong style="color:#991b1b;">Coach/athlete gaps flagged:</strong>';
        for (var k = 0; k < flagged.length; k++) {
          var g = flagged[k];
          html += '<div style="margin-top:0.4rem;font-size:0.88rem;">';
          html += '<strong>' + _facetPretty(g.facet) + '</strong> (' + g.direction + ', gap ' + _fmt(g.gap) + '): ';
          html += _esc(generateCircumplexGapNarrative(g.facet, g.direction));
          html += '</div>';
        }
        html += '</div>';
      }
    }
    html += '</div>';
    return html;
  }

  function renderOptionalLayersHTML(scores, audience, ctx) {
    if (!scores) return "";
    audience = audience || "athlete";
    ctx = ctx || {};
    var html = '';
    var anyContent = false;
    if (scores.passion) { html += _renderPassionSection(scores.passion, scores.overinvestment, audience); anyContent = true; }
    if (scores.regulatory) { html += _renderRegulatorySection(scores.regulatory, scores.erosion, audience); anyContent = true; }
    if (scores.selfConcordance) { html += _renderSelfConcordanceSection(scores.selfConcordance, scores.selfConcordanceTrajectory, audience); anyContent = true; }
    if (scores.groupConscious) { html += _renderGroupConsciousSection(scores.groupConscious, audience); anyContent = true; }
    if (scores.causality) { html += _renderCausalitySection(scores.causality, audience); anyContent = true; }
    if (scores.coachCircumplex) { html += _renderCircumplexSection(scores.coachCircumplex, ctx.athleteAggregate); anyContent = true; }
    if (!anyContent) return "";
    return '<div class="optional-layers-block" style="margin-top:1.5rem;">' +
           '<h2 style="font-size:1.1rem;margin-bottom:0.75rem;color:#111;">Section 16 measurement layers</h2>' +
           html + '</div>';
  }

  // ===========================================================================
  // PUBLIC API
  // ===========================================================================

  return {
    // Items + tier helpers
    ITEMS: ITEMS,
    LAYER_ITEMS: LAYER_ITEMS,

    // Scoring
    scorePassionQuality: scorePassionQuality,
    evaluateOverinvestment: evaluateOverinvestment,
    scoreRegulatoryStyle: scoreRegulatoryStyle,
    detectRegulationErosion: detectRegulationErosion,
    scoreSelfConcordance: scoreSelfConcordance,
    computeGoalTrajectory: computeGoalTrajectory,
    scoreGroupConscious: scoreGroupConscious,
    computeTeamDispersion: computeTeamDispersion,
    scoreCausalityOrientations: scoreCausalityOrientations,
    scoreCircumplex: scoreCircumplex,
    aggregateAthleteRatings: aggregateAthleteRatings,
    computeCircumplexGaps: computeCircumplexGaps,

    // Narratives
    generatePassionNarrative: generatePassionNarrative,
    generateOverinvestmentNarrative: generateOverinvestmentNarrative,
    generateRegulatoryNarrative: generateRegulatoryNarrative,
    generateErosionNarrative: generateErosionNarrative,
    generateSelfConcordanceTrajectoryNarrative: generateSelfConcordanceTrajectoryNarrative,
    generateSelfConcordanceNarrative: generateSelfConcordanceNarrative,
    generateCausalityNarrative: generateCausalityNarrative,
    generateCollectiveSatisfactionNarrative: generateCollectiveSatisfactionNarrative,
    generateTeamIdentificationNarrative: generateTeamIdentificationNarrative,
    generateEmpathicRiskNarrative: generateEmpathicRiskNarrative,
    generateTeamDispersionNarrative: generateTeamDispersionNarrative,
    generateCircumplexFacetNarrative: generateCircumplexFacetNarrative,
    generateCircumplexGapNarrative: generateCircumplexGapNarrative,
    generateCircumplexApproachNarrative: generateCircumplexApproachNarrative,

    // Orchestration
    scoreAllOptionalLayers: scoreAllOptionalLayers,
    renderOptionalLayersHTML: renderOptionalLayersHTML,
  };
})();
