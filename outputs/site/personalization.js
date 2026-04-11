/**
 * ABC Personalization Engine
 *
 * JavaScript port of the Python scoring modules:
 *   - bayesian_scorer.py  (conjugate normal update, archetype probabilities)
 *   - narrative_engine.py (narrative text for archetypes, states, signatures)
 *   - transition_engine.py (growth hierarchy, transition classification)
 *   - onboarding_scorer.py (6-item tier, suppressed labels)
 *
 * All classes and data are exported via the global ABCPersonalization object.
 */

const ABCPersonalization = (function () {
  "use strict";

  // =========================================================================
  // Constants
  // =========================================================================

  const SUBSCALE_NAMES = [
    "a_sat",
    "a_frust",
    "b_sat",
    "b_frust",
    "c_sat",
    "c_frust",
  ];

  const DOMAIN_PAIRS = {
    ambition: ["a_sat", "a_frust"],
    belonging: ["b_sat", "b_frust"],
    craft: ["c_sat", "c_frust"],
  };

  const SAT_THRESHOLD = 6.46;
  const FRUST_THRESHOLD = 4.38;
  const TYPE_ACTIVATION_THRESHOLD = 5.5;

  // (A_strong, B_strong, C_strong) -> archetype name
  // Encoded as "TTT", "TTF", etc. for lookup
  const ARCHETYPE_PATTERNS = {
    TTT: "Integrator",
    TTF: "Captain",
    TFT: "Architect",
    FTT: "Mentor",
    TFF: "Pioneer",
    FTF: "Anchor",
    FFT: "Artisan",
    FFF: "Seeker",
  };

  // =========================================================================
  // Normal CDF: Abramowitz & Stegun approximation (formula 7.1.26)
  // Maximum error < 1.5e-7. Adequate for classification probabilities.
  // =========================================================================

  function normalCDF(x, mu, sigma) {
    if (mu === undefined) mu = 0.0;
    if (sigma === undefined) sigma = 1.0;

    var z = (x - mu) / sigma;
    var sign = 1;
    if (z < 0) {
      z = -z;
      sign = -1;
    }

    var p = 0.2316419;
    var b1 = 0.31938153;
    var b2 = -0.356563782;
    var b3 = 1.781477937;
    var b4 = -1.821255978;
    var b5 = 1.330274429;

    var t = 1.0 / (1.0 + p * z);
    var t2 = t * t;
    var t3 = t2 * t;
    var t4 = t3 * t;
    var t5 = t4 * t;

    var pdf = Math.exp(-0.5 * z * z) / Math.sqrt(2.0 * Math.PI);
    var upperTail = pdf * (b1 * t + b2 * t2 + b3 * t3 + b4 * t4 + b5 * t5);

    if (sign < 0) {
      return upperTail;
    }
    return 1.0 - upperTail;
  }

  // =========================================================================
  // BayesianScorer: single-subscale sequential estimator
  // =========================================================================

  function BayesianScorer(priorMean, priorSD) {
    this.priorMean = priorMean !== undefined ? priorMean : 5.0;
    this.priorSD = priorSD !== undefined ? priorSD : 2.0;
    this.posteriorMean = this.priorMean;
    this.posteriorSD = this.priorSD;
    this._history = [];
  }

  BayesianScorer.prototype.measurementsIncorporated = function () {
    return this._history.length;
  };

  /**
   * Incorporate a new observation via conjugate normal updating.
   *
   * Conjugate update formulae:
   *   precision_prior = 1 / sigma_prior^2
   *   precision_data  = 1 / sigma_e^2
   *   precision_post  = precision_prior + precision_data
   *   mu_post    = (mu_prior * precision_prior + x * precision_data) / precision_post
   *   sigma_post = sqrt(1 / precision_post)
   *
   * @param {number} newScore - Observed subscale score (0-10 scale).
   * @param {number} [measurementSE=0.8] - Standard error of measurement.
   * @returns {object} Posterior summary.
   */
  BayesianScorer.prototype.update = function (newScore, measurementSE) {
    if (measurementSE === undefined) measurementSE = 0.8;

    var priorPrecision = 1.0 / (this.posteriorSD * this.posteriorSD);
    var dataPrecision = 1.0 / (measurementSE * measurementSE);
    var postPrecision = priorPrecision + dataPrecision;

    var postMean =
      (this.posteriorMean * priorPrecision + newScore * dataPrecision) /
      postPrecision;
    var postSD = Math.sqrt(1.0 / postPrecision);

    this.posteriorMean = postMean;
    this.posteriorSD = postSD;

    this._history.push({
      score: newScore,
      measurementSE: measurementSE,
      posteriorMean: postMean,
      posteriorSD: postSD,
    });

    var priorWeight = priorPrecision / postPrecision;
    var dataWeight = dataPrecision / postPrecision;

    // 90% credible interval: mean +/- 1.645 * sd
    var z90 = 1.6449;
    var ciLow = postMean - z90 * postSD;
    var ciHigh = postMean + z90 * postSD;

    return {
      posteriorMean: postMean,
      posteriorSD: postSD,
      credibleInterval90: [ciLow, ciHigh],
      measurementsIncorporated: this.measurementsIncorporated(),
      priorWeight: priorWeight,
      dataWeight: dataWeight,
    };
  };

  /**
   * Compute a personalized lower-bound threshold.
   * Returns null if fewer than 6 measurements.
   *
   * @param {number} [k=1.5] - SDs below mean.
   * @param {number} [floor=3.0] - Absolute minimum.
   * @returns {number|null}
   */
  BayesianScorer.prototype.getPersonalizedThreshold = function (k, floor) {
    if (k === undefined) k = 1.5;
    if (floor === undefined) floor = 3.0;
    if (this.measurementsIncorporated() < 6) return null;
    return Math.max(this.posteriorMean - k * this.posteriorSD, floor);
  };

  // =========================================================================
  // Domain state classification with uncertainty
  // =========================================================================

  /**
   * Classify a domain into one of four states using full posteriors.
   *
   * P(Thriving)   = P(sat >= t_s) * P(frust <  t_f)
   * P(Vulnerable) = P(sat >= t_s) * P(frust >= t_f)
   * P(Mild)       = P(sat <  t_s) * P(frust <  t_f)
   * P(Distressed) = P(sat <  t_s) * P(frust >= t_f)
   *
   * @param {BayesianScorer} satScorer
   * @param {BayesianScorer} frustScorer
   * @param {number} [satThreshold=6.46]
   * @param {number} [frustThreshold=4.38]
   * @returns {object} Posterior probabilities for each state.
   */
  function classifyWithUncertainty(
    satScorer,
    frustScorer,
    satThreshold,
    frustThreshold
  ) {
    if (satThreshold === undefined) satThreshold = SAT_THRESHOLD;
    if (frustThreshold === undefined) frustThreshold = FRUST_THRESHOLD;

    var pSatHigh =
      1.0 -
      normalCDF(satThreshold, satScorer.posteriorMean, satScorer.posteriorSD);
    var pSatLow = 1.0 - pSatHigh;

    var pFrustHigh =
      1.0 -
      normalCDF(
        frustThreshold,
        frustScorer.posteriorMean,
        frustScorer.posteriorSD
      );
    var pFrustLow = 1.0 - pFrustHigh;

    var states = {
      posteriorThriving: pSatHigh * pFrustLow,
      posteriorVulnerable: pSatHigh * pFrustHigh,
      posteriorMild: pSatLow * pFrustLow,
      posteriorDistressed: pSatLow * pFrustHigh,
    };

    var stateLabels = {
      posteriorThriving: "Thriving",
      posteriorVulnerable: "Vulnerable",
      posteriorMild: "Mild",
      posteriorDistressed: "Distressed",
    };

    var bestKey = null;
    var bestVal = -1;
    for (var key in states) {
      if (states[key] > bestVal) {
        bestVal = states[key];
        bestKey = key;
      }
    }

    states.mostLikelyState = stateLabels[bestKey];
    states.confidence = states[bestKey];

    return states;
  }

  // =========================================================================
  // ABCBayesianProfile: full 6-subscale wrapper
  // =========================================================================

  function ABCBayesianProfile(baseRatePrior) {
    this.scorers = {};
    for (var i = 0; i < SUBSCALE_NAMES.length; i++) {
      var name = SUBSCALE_NAMES[i];
      if (baseRatePrior && baseRatePrior[name]) {
        var prior = baseRatePrior[name];
        var mean =
          typeof prior === "object" ? prior.mean || 5.0 : prior;
        var sd =
          typeof prior === "object" ? prior.sd || 2.0 : 2.0;
        this.scorers[name] = new BayesianScorer(mean, sd);
      } else {
        this.scorers[name] = new BayesianScorer();
      }
    }
  }

  /**
   * Update all six subscale scorers with a new set of observations.
   *
   * @param {object} subscales - Map of subscale name to observed score (0-10).
   * @param {object} [measurementSEs] - Optional map of subscale name to SE.
   * @returns {object} Subscale posteriors and domain states.
   */
  ABCBayesianProfile.prototype.updateAll = function (
    subscales,
    measurementSEs
  ) {
    var subscaleResults = {};
    for (var i = 0; i < SUBSCALE_NAMES.length; i++) {
      var name = SUBSCALE_NAMES[i];
      var se =
        measurementSEs && measurementSEs[name] !== undefined
          ? measurementSEs[name]
          : 0.8;
      subscaleResults[name] = this.scorers[name].update(subscales[name], se);
    }

    var domainStates = {};
    for (var domain in DOMAIN_PAIRS) {
      var satKey = DOMAIN_PAIRS[domain][0];
      var frustKey = DOMAIN_PAIRS[domain][1];
      domainStates[domain] = classifyWithUncertainty(
        this.scorers[satKey],
        this.scorers[frustKey]
      );
    }

    return {
      subscales: subscaleResults,
      domainStates: domainStates,
    };
  };

  /**
   * Compute the probability of each of the 8 archetypes.
   *
   * P(strong) for each domain = P(sat >= threshold) from posterior.
   * Under independence, P(archetype) = product across domains.
   *
   * @param {number} [activationThreshold=5.5]
   * @returns {object} Map of archetype name to probability summing to 1.0.
   */
  ABCBayesianProfile.prototype.getArchetypeProbabilities = function (
    activationThreshold
  ) {
    if (activationThreshold === undefined)
      activationThreshold = TYPE_ACTIVATION_THRESHOLD;

    var pA =
      1.0 -
      normalCDF(
        activationThreshold,
        this.scorers.a_sat.posteriorMean,
        this.scorers.a_sat.posteriorSD
      );
    var pB =
      1.0 -
      normalCDF(
        activationThreshold,
        this.scorers.b_sat.posteriorMean,
        this.scorers.b_sat.posteriorSD
      );
    var pC =
      1.0 -
      normalCDF(
        activationThreshold,
        this.scorers.c_sat.posteriorMean,
        this.scorers.c_sat.posteriorSD
      );

    var domainProbs = { a: pA, b: pB, c: pC };
    var domainKeys = ["a", "b", "c"];

    var result = {};
    for (var patternKey in ARCHETYPE_PATTERNS) {
      var archName = ARCHETYPE_PATTERNS[patternKey];
      var prob = 1.0;
      for (var d = 0; d < 3; d++) {
        var isStrong = patternKey.charAt(d) === "T";
        var pStrong = domainProbs[domainKeys[d]];
        prob *= isStrong ? pStrong : 1.0 - pStrong;
      }
      result[archName] = prob;
    }

    return result;
  };

  /**
   * Return a comprehensive summary of the current Bayesian profile.
   */
  ABCBayesianProfile.prototype.getSummary = function () {
    var posteriors = {};
    var weightBalance = {};
    var z90 = 1.6449;

    for (var name in this.scorers) {
      var scorer = this.scorers[name];
      posteriors[name] = {
        mean: scorer.posteriorMean,
        sd: scorer.posteriorSD,
        credibleInterval90: [
          scorer.posteriorMean - z90 * scorer.posteriorSD,
          scorer.posteriorMean + z90 * scorer.posteriorSD,
        ],
      };

      var priorPrecision = 1.0 / (scorer.priorSD * scorer.priorSD);
      var totalPrecision = 1.0 / (scorer.posteriorSD * scorer.posteriorSD);
      var priorW = priorPrecision / totalPrecision;
      weightBalance[name] = {
        priorWeight: priorW,
        dataWeight: 1.0 - priorW,
      };
    }

    var domainStates = {};
    for (var domain in DOMAIN_PAIRS) {
      var satKey = DOMAIN_PAIRS[domain][0];
      var frustKey = DOMAIN_PAIRS[domain][1];
      domainStates[domain] = classifyWithUncertainty(
        this.scorers[satKey],
        this.scorers[frustKey]
      );
    }

    var archetypes = this.getArchetypeProbabilities();

    var firstScorer = this.scorers[SUBSCALE_NAMES[0]];
    var n = firstScorer.measurementsIncorporated();

    return {
      posteriors: posteriors,
      domainStates: domainStates,
      archetypes: archetypes,
      measurementsIncorporated: n,
      weightBalance: weightBalance,
    };
  };

  // =========================================================================
  // Standalone getArchetypeProbabilities (from three sat scorers)
  // =========================================================================

  /**
   * Compute archetype probabilities from three satisfaction scorers.
   *
   * @param {BayesianScorer} aSatScorer
   * @param {BayesianScorer} bSatScorer
   * @param {BayesianScorer} cSatScorer
   * @param {number} [activationThreshold=5.5]
   * @returns {object} Map of archetype name to probability.
   */
  function getArchetypeProbabilities(
    aSatScorer,
    bSatScorer,
    cSatScorer,
    activationThreshold
  ) {
    if (activationThreshold === undefined)
      activationThreshold = TYPE_ACTIVATION_THRESHOLD;

    var pA =
      1.0 -
      normalCDF(
        activationThreshold,
        aSatScorer.posteriorMean,
        aSatScorer.posteriorSD
      );
    var pB =
      1.0 -
      normalCDF(
        activationThreshold,
        bSatScorer.posteriorMean,
        bSatScorer.posteriorSD
      );
    var pC =
      1.0 -
      normalCDF(
        activationThreshold,
        cSatScorer.posteriorMean,
        cSatScorer.posteriorSD
      );

    var domainProbs = { a: pA, b: pB, c: pC };
    var domainKeys = ["a", "b", "c"];

    var result = {};
    for (var patternKey in ARCHETYPE_PATTERNS) {
      var archName = ARCHETYPE_PATTERNS[patternKey];
      var prob = 1.0;
      for (var d = 0; d < 3; d++) {
        var isStrong = patternKey.charAt(d) === "T";
        var pStrong = domainProbs[domainKeys[d]];
        prob *= isStrong ? pStrong : 1.0 - pStrong;
      }
      result[archName] = prob;
    }

    return result;
  }

  // =========================================================================
  // NARRATIVE_DATA: complete port of all narrative text
  // =========================================================================

  var NARRATIVE_DATA = {
    // -------------------------------------------------------------------
    // Archetype narratives: 8 archetypes x 2 audiences
    // -------------------------------------------------------------------
    archetypeNarratives: {
      Integrator: {
        athlete: {
          identity_description:
            "You draw energy from all three domains: ambition, belonging, " +
            "and craft. You pursue goals, invest in relationships, and care " +
            "about the quality of your work. This balance gives you range. " +
            "Where others specialize, you connect.",
          strengths: [
            "You adapt to different situations because you draw from " +
              "multiple sources of motivation.",
            "You see how individual goals, team dynamics, and skill development fit together.",
            "You sustain engagement even when one domain dips, because " +
              "the others provide lift.",
            "You bring perspective that specialists sometimes miss.",
          ],
          growth_edge:
            "Your range is real, but it can also scatter your focus. " +
            "Pick one domain to push from strong to exceptional. " +
            "Depth in one area sharpens the others.",
        },
        coach: {
          identity_description:
            "This athlete draws energy from all three domains: ambition, " +
            "belonging, and craft. They pursue goals, invest in relationships, " +
            "and care about quality. This balance creates resilience. " +
            "Where others specialize, this athlete connects.",
          strengths: [
            "Adapts across situations by drawing from multiple sources of motivation.",
            "Sees how goals, team dynamics, and skill development fit together.",
            "Sustains engagement when one domain dips, because the others provide lift.",
            "Brings perspective that specialists sometimes miss.",
          ],
          growth_edge:
            "This athlete's range can scatter focus. Help them choose one " +
            "domain to push from strong to exceptional. Depth in one area " +
            "will sharpen the others.",
        },
      },
      Captain: {
        athlete: {
          identity_description:
            "You lead through people. Ambition and belonging fuel you: you " +
            "set goals and bring others along. You want to win, and you " +
            "want everyone in the room when it happens. Craft is your " +
            "developing frontier.",
          strengths: [
            "You rally people around a shared objective.",
            "You build coalitions. Others follow because they trust " +
              "your direction and your investment in them.",
            "You translate competitive drive into collective energy.",
            "You read group dynamics and adjust your leadership accordingly.",
          ],
          growth_edge:
            "Your leadership earns trust. Your next step is deepening one " +
            "technical skill that reinforces your credibility. The best " +
            "captains lead and do.",
        },
        coach: {
          identity_description:
            "This athlete leads through people. Ambition and belonging are " +
            "both strong: they set goals and bring others along. They want " +
            "to win and want the team present for it. Craft is their " +
            "developing frontier.",
          strengths: [
            "Rallies people around a shared objective.",
            "Builds coalitions through trust and relational investment.",
            "Translates competitive drive into collective energy.",
            "Reads group dynamics and adjusts leadership style.",
          ],
          growth_edge:
            "Help this athlete invest in one technical skill that deepens " +
            "their leadership credibility. Their relational strength is " +
            "established. Craft development is the next lever.",
        },
      },
      Architect: {
        athlete: {
          identity_description:
            "You build with purpose. Ambition and craft drive you: you set " +
            "high standards and develop the skills to meet them. You think " +
            "strategically about how performance fits together. Belonging " +
            "is your developing frontier.",
          strengths: [
            "You combine drive with technical depth. Your goals are backed by skill.",
            "You hold high standards and do the work to justify them.",
            "You think in systems. You see how the parts connect.",
            "You produce quality output under pressure.",
          ],
          growth_edge:
            "Your work speaks for itself, but work alone does not build " +
            "teams. Bring one collaborator into your next project early. " +
            "Shared craft strengthens belonging.",
        },
        coach: {
          identity_description:
            "This athlete builds with purpose. Ambition and craft are both " +
            "strong: they set high standards and develop the skills to meet " +
            "them. They think strategically about performance. Belonging " +
            "is their developing frontier.",
          strengths: [
            "Combines drive with technical depth. Goals are backed by skill.",
            "Holds high standards and does the work to justify them.",
            "Thinks in systems. Sees how the parts connect.",
            "Produces quality output under pressure.",
          ],
          growth_edge:
            "This athlete's work speaks for itself, but work alone does not " +
            "build teams. Create opportunities for them to collaborate " +
            "early in a process, not just deliver at the end.",
        },
      },
      Mentor: {
        athlete: {
          identity_description:
            "You grow others through what you know. Belonging and craft " +
            "fuel you: you build deep expertise and share it generously. " +
            "You teach, guide, and build trust through competence. " +
            "Ambition is your developing frontier.",
          strengths: [
            "You build trust through demonstrated competence. People " +
              "listen because you know your craft.",
            "You share knowledge without holding it back. Others improve around you.",
            "You bring patience to complexity. You simplify hard things for others.",
            "You create psychological safety through consistent, reliable presence.",
          ],
          growth_edge:
            "Your expertise and generosity are clear. The next step is " +
            "making your work visible beyond your immediate circle. " +
            "Expertise scales when it reaches a wider audience.",
        },
        coach: {
          identity_description:
            "This athlete grows others through their knowledge. Belonging " +
            "and craft are both strong: they build deep expertise and share " +
            "it generously. They teach, guide, and build trust through " +
            "competence. Ambition is their developing frontier.",
          strengths: [
            "Builds trust through demonstrated competence. Others " +
              "listen because they know their craft.",
            "Shares knowledge without holding it back. Others improve around them.",
            "Brings patience to complexity. Simplifies hard things for others.",
            "Creates psychological safety through consistent, reliable presence.",
          ],
          growth_edge:
            "Help this athlete claim credit for their contributions. " +
            "They give freely but may avoid the visibility that ambition " +
            "requires. Small steps toward public recognition build the " +
            "ambition domain without forcing it.",
        },
      },
      Pioneer: {
        athlete: {
          identity_description:
            "You know where you want to go. Ambition is your engine. " +
            "You set goals, chase them, and clear obstacles. Belonging and " +
            "craft are developing. Your drive is your foundation. The " +
            "question is what you build on it.",
          strengths: [
            "You set clear goals and pursue them with focus.",
            "You take initiative when others wait.",
            "You bring competitive energy that raises the bar.",
            "You make decisions and commit.",
          ],
          growth_edge:
            "Your drive is powerful, but drive alone narrows. Pick one " +
            "relationship or one skill to invest in alongside your goals. " +
            "Ambition lasts longer when it is supported.",
        },
        coach: {
          identity_description:
            "This athlete knows where they want to go. Ambition is their " +
            "engine. They set goals, chase them, and clear obstacles. " +
            "Belonging and craft are both developing. Their drive is real. " +
            "The question is what they build around it.",
          strengths: [
            "Sets clear goals and pursues them with focus.",
            "Takes initiative when others wait.",
            "Brings competitive energy that raises the bar.",
            "Makes decisions and commits.",
          ],
          growth_edge:
            "Help this athlete invest in one relationship or one skill " +
            "that supports their goals. Their drive is not the issue. " +
            "A broader base will sustain it.",
        },
      },
      Anchor: {
        athlete: {
          identity_description:
            "You ground the people around you. Belonging is your strength. " +
            "You build trust, hold space, and keep groups stable. Ambition " +
            "and craft are developing. Your relational presence is what " +
            "others rely on.",
          strengths: [
            "You create stability in your environment. Others feel settled around you.",
            "You build trust through consistency and empathy.",
            "You hold groups together during difficult stretches.",
            "You notice when someone is struggling before they say it.",
          ],
          growth_edge:
            "Your relational strength is clear. The next step is using " +
            "it to grow: learn from someone you admire, or push into a " +
            "skill that excites you. Growth does not require leaving " +
            "your relationships behind.",
        },
        coach: {
          identity_description:
            "This athlete grounds the people around them. Belonging is " +
            "their strength. They build trust, hold space, and keep " +
            "groups stable. Ambition and craft are both developing. " +
            "Others rely on their relational presence.",
          strengths: [
            "Creates stability in the environment. Others feel settled around them.",
            "Builds trust through consistency and empathy.",
            "Holds groups together during difficult stretches.",
            "Notices when someone is struggling before they say it.",
          ],
          growth_edge:
            "Help this athlete use their relationships as a platform for " +
            "growth. They will not pursue goals or skills at the expense " +
            "of connection, but they can pursue them through it. Frame " +
            "development as something the team needs from them.",
        },
      },
      Artisan: {
        athlete: {
          identity_description:
            "You lead with craft. Quality and mastery drive you. You go " +
            "deep where others stay on the surface. Ambition and belonging " +
            "are developing. Your foundation is what you can do, and how " +
            "well you can do it.",
          strengths: [
            "You build deep expertise. You know your craft at a level others do not reach.",
            "You hold yourself to high standards without needing external validation.",
            "You bring patience to problems that demand it.",
            "You find satisfaction in the process, not just the result.",
          ],
          growth_edge:
            "Your skill is real. The next step is sharing it. Teach one " +
            "thing you have mastered. Teaching builds belonging from " +
            "craft, and it makes your work visible.",
        },
        coach: {
          identity_description:
            "This athlete leads with craft. Quality and mastery are their " +
            "drivers. They go deep where others stay on the surface. " +
            "Ambition and belonging are both developing. Their foundation " +
            "is competence.",
          strengths: [
            "Builds deep expertise. Knows their craft at a level others do not reach.",
            "Holds high standards without needing external validation.",
            "Brings patience to problems that demand it.",
            "Finds satisfaction in the process, not just the result.",
          ],
          growth_edge:
            "Help this athlete share their expertise. They may resist " +
            "visibility, but teaching creates belonging without requiring " +
            "social performance. Pair them with someone who wants to learn " +
            "what they know.",
        },
      },
      Seeker: {
        athlete: {
          identity_description:
            "You are in an open phase. No single domain dominates your " +
            "profile right now. This is not a deficit: it is a starting " +
            "point. You have room to explore what drives you and where " +
            "your energy wants to go.",
          strengths: [
            "You bring fresh eyes. You are not locked into patterns that no longer serve you.",
            "You are open to change in ways that established profiles are not.",
            "You have the capacity for real transformation.",
            "You can choose your direction rather than inherit it.",
          ],
          growth_edge:
            "Openness is a strength, but it needs direction. Pick one " +
            "domain and invest deliberately. It does not have to be the " +
            "right one forever. Commitment creates momentum, and momentum " +
            "reveals what matters.",
        },
        coach: {
          identity_description:
            "This athlete is in an open phase. No single domain dominates " +
            "their profile. This is not a deficit: it is a starting point. " +
            "The frustration levels reveal whether this is peaceful " +
            "exploration or distressed searching.",
          strengths: [
            "Brings fresh eyes. Not locked into patterns that no longer serve them.",
            "Open to change in ways that established profiles are not.",
            "Has the capacity for real transformation.",
            "Can choose direction rather than inherit it.",
          ],
          growth_edge:
            "Help this athlete pick one domain and invest. Do not force " +
            "all three at once. If frustration is high, start by reducing " +
            "it in one domain before building satisfaction. If frustration " +
            "is low, explore what genuinely excites them.",
        },
      },
    },

    // -------------------------------------------------------------------
    // Domain state narratives: 4 states x 3 domains x 2 audiences
    // Templates use {domain} and {domain_lower} placeholders
    // -------------------------------------------------------------------
    domainStateNarratives: {
      Thriving: {
        athlete: {
          state_description:
            "Your {domain} is strong and the effort feels worth it. " +
            "This domain is fueling you right now. The conditions around " +
            "you are supporting what you need.",
          reflection_prompt:
            "What is it about your current environment that makes " +
            "{domain_lower} feel this good? Name it, so you can protect it.",
        },
        coach: {
          state_description:
            "This athlete's {domain} is strong, and the effort cost is low. " +
            "The domain is fueling them. The current environment supports " +
            "what they need here.",
          conversation_starter:
            "Ask them what about their current situation makes " +
            "{domain_lower} feel sustainable. Understanding the conditions " +
            "that support this state helps you protect them.",
        },
      },
      Vulnerable: {
        athlete: {
          state_description:
            "Your {domain} scores high, but the cost of maintaining it is " +
            "rising. You are performing, yet something about the effort " +
            "feels harder than it should. This is not a failure. It is a " +
            "signal that the balance between effort and reward is shifting.",
          reflection_prompt:
            "Where does the effort around {domain_lower} feel heaviest? " +
            "What part of maintaining it is costing you the most right now?",
        },
        coach: {
          state_description:
            "This athlete's {domain} is high, but the effort cost is also " +
            "high. They are performing, yet the strain is real. This is " +
            "the highest-priority state for intervention because the " +
            "athlete is still engaged and the window to act is open.",
          conversation_starter:
            "Open with recognition: they are doing well in {domain_lower}. " +
            "Then ask what part of maintaining it feels heaviest. " +
            "The goal is to reduce effort cost, not to add more.",
        },
      },
      Mild: {
        athlete: {
          state_description:
            "Your {domain} is quiet right now. It is neither strong nor " +
            "blocked. This domain is not causing problems, but it is not " +
            "giving you energy either. It sits idle.",
          reflection_prompt:
            "Is {domain_lower} quiet because you have chosen to focus " +
            "elsewhere, or because the opportunity to engage it is " +
            "missing? The distinction matters.",
        },
        coach: {
          state_description:
            "This athlete's {domain} is low, but frustration is also low. " +
            "The domain is dormant rather than distressed. The need is " +
            "not being engaged, but it is not being blocked either.",
          conversation_starter:
            "Explore whether the low engagement in {domain_lower} is a " +
            "choice or a gap. Ask whether the environment offers " +
            "opportunities to engage this need. Sometimes dormancy " +
            "reflects a missing context, not a missing desire.",
        },
      },
      Distressed: {
        athlete: {
          state_description:
            "Your {domain} is low, and the cost of effort here is high. " +
            "This domain is not just unfulfilled: something in your " +
            "environment is actively working against it. This is hard, " +
            "and it is not your fault that it feels hard.",
          reflection_prompt:
            "What is blocking your {domain_lower} right now? Is it a " +
            "person, a structure, a situation? Naming the source is the " +
            "first step toward changing it.",
        },
        coach: {
          state_description:
            "This athlete's {domain} is low, and frustration is high. " +
            "The need is actively thwarted. This is the most urgent state. " +
            "Sustained thwarting predicts burnout, disengagement, and " +
            "dropout.",
          conversation_starter:
            "Lead with care, not diagnosis. Ask what is making " +
            "{domain_lower} difficult right now. Focus on removing " +
            "blockers before adding positive experiences. Reducing " +
            "frustration matters more than boosting satisfaction here.",
        },
      },
    },

    // -------------------------------------------------------------------
    // Frustration signature narratives: 6 signatures x 2 audiences
    // -------------------------------------------------------------------
    signatureNarratives: {
      "Blocked Drive": {
        athlete: {
          description:
            "You have strong ambition, but something is raising the cost " +
            "of pursuing your goals. You want to push forward, and the " +
            "resistance is real. The drive is intact. The environment is " +
            "not matching it.",
          action_prompt:
            "What specific obstacle is standing between you and your " +
            "goals right now? Is it something you can influence, or " +
            "something you need help with?",
        },
        coach: {
          description:
            "This athlete has strong ambition with high frustration. They " +
            "want to pursue goals, but something in the environment is " +
            "raising the effort cost. The drive is not the problem. The " +
            "conditions around it are.",
          action_prompt:
            "Ask what is getting in the way of their goals. Listen for " +
            "structural barriers: playing time, role clarity, feedback " +
            "gaps. These are often coachable.",
        },
      },
      "Conditional Belonging": {
        athlete: {
          description:
            "You feel connected, but the connection has conditions. " +
            "Something about belonging here requires ongoing effort that " +
            "feels heavier than it should. You are not failing to belong. " +
            "You are paying a high price to belong.",
          action_prompt:
            "What part of fitting in feels like it takes the most energy? " +
            "Is there a version of belonging here that costs less?",
        },
        coach: {
          description:
            "This athlete reports strong belonging with high frustration. " +
            "They feel connected, but the connection is conditional or " +
            "costly. Watch for performance-contingent acceptance, " +
            "exclusionary group norms, or social effort that drains " +
            "rather than restores.",
          action_prompt:
            "Explore what the athlete feels they must do to maintain " +
            "their place. Belonging should restore energy, not consume " +
            "it. Ask what would make the team feel safer.",
        },
      },
      "Evaluated Mastery": {
        athlete: {
          description:
            "Your skills are strong, but the way they are judged is " +
            "raising the effort cost. You care about quality, and the " +
            "evaluation pressure is making the craft feel heavier. " +
            "The skill is not the problem. The conditions around " +
            "performing it are.",
          action_prompt:
            "When does your craft feel lightest? When does it feel " +
            "heaviest? The gap between those moments often points to " +
            "the evaluation pressure.",
        },
        coach: {
          description:
            "This athlete has strong craft with high frustration. Their " +
            "skills are solid, but the evaluation context is raising " +
            "effort cost. Watch for perfectionism driven by fear of " +
            "judgment, or environments where mistakes are punished " +
            "rather than used for learning.",
          action_prompt:
            "Create low-stakes practice opportunities. Ask when their " +
            "craft feels most natural and when it feels most pressured. " +
            "Reduce the evaluation load without lowering the standard.",
        },
      },
      "Controlled Motivation": {
        athlete: {
          description:
            "Your goals feel imposed rather than chosen. The effort " +
            "cost of pursuing ambition is high because the direction " +
            "is not yours. This is not a lack of drive. It is drive " +
            "pointed somewhere you did not pick.",
          action_prompt:
            "Whose goals are you chasing right now? What would you " +
            "pursue if the choice were entirely yours?",
        },
        coach: {
          description:
            "This athlete shows low ambition satisfaction with high " +
            "frustration. Their goal pursuit feels controlled rather " +
            "than autonomous. The motivation is external: pressure, " +
            "obligation, or expectations they did not set. This is a " +
            "high-risk pattern for burnout.",
          action_prompt:
            "Start by asking what they want, not what they should want. " +
            "Look for places where you can offer choice within " +
            "structure. Autonomy does not mean no rules. It means " +
            "genuine input into direction.",
        },
      },
      "Active Exclusion": {
        athlete: {
          description:
            "You do not feel like you belong, and the environment is " +
            "actively making that harder. This is not about your social " +
            "skills or effort. Something in the culture or structure " +
            "around you is blocking connection.",
          action_prompt:
            "Where do you feel most excluded? Is there one relationship " +
            "or setting where you do feel accepted? Start there.",
        },
        coach: {
          description:
            "This athlete shows low belonging satisfaction with high " +
            "frustration. They do not just lack connection: something in " +
            "the environment is actively excluding them. This requires " +
            "immediate attention. Look at team culture, cliques, and " +
            "structural barriers to inclusion.",
          action_prompt:
            "Do not ask the athlete to try harder to fit in. The " +
            "environment must change, not just the individual. Examine " +
            "team norms, social dynamics, and your own role in who gets " +
            "included.",
        },
      },
      "Competence Threat": {
        athlete: {
          description:
            "Your skills feel inadequate, and the environment is making " +
            "that worse. The cost of effort in craft is high because " +
            "every attempt feels like it confirms the gap. This is not " +
            "about a lack of talent. The conditions around skill " +
            "development are working against you.",
          action_prompt:
            "What is one small skill you could improve this week where " +
            "you control the process? Start where success is possible, " +
            "not where the pressure is highest.",
        },
        coach: {
          description:
            "This athlete shows low craft satisfaction with high " +
            "frustration. Their competence feels threatened. Every " +
            "performance situation raises the effort cost because " +
            "failure feels confirming rather than informative. This is " +
            "the highest-risk craft pattern.",
          action_prompt:
            "Provide structured, low-stakes skill-building opportunities. " +
            "Separate development from evaluation. Give specific, " +
            "process-focused feedback rather than outcome judgment. " +
            "Rebuild confidence through small, visible wins.",
        },
      },
    },

    // -------------------------------------------------------------------
    // Transition narratives: 5 types x 2 audiences
    // Templates use {previous} and {current} placeholders
    // -------------------------------------------------------------------
    transitionNarratives: {
      growth: {
        athlete:
          "Your profile has shifted from {previous} to {current}. This is " +
          "growth. A domain that was developing has strengthened, and your " +
          "motivational base is broader now. The work you put in is showing.",
        coach:
          "This athlete's profile has shifted from {previous} to {current}. " +
          "This represents growth: a developing domain has strengthened. " +
          "Recognize the progress. Reinforcement here sustains the trajectory.",
      },
      exploration: {
        athlete:
          "Your profile has shifted from {previous} to {current}. This " +
          "looks like exploration. You are trying new patterns, investing " +
          "energy in different places. This is healthy. New ground does not " +
          "feel settled, and that is fine.",
        coach:
          "This athlete's profile has shifted from {previous} to {current}. " +
          "This appears to be exploration rather than decline. They are " +
          "testing new motivational patterns. Normalize the shift and keep " +
          "the conversation open.",
      },
      regression: {
        athlete:
          "Your profile has shifted from {previous} to {current}. A domain " +
          "that was strong is now developing. This does not erase what you " +
          "built. Context changes, demands shift, and your profile reflects " +
          "that. The question is whether this shift matches what is " +
          "happening in your environment.",
        coach:
          "This athlete's profile has shifted from {previous} to {current}. " +
          "A previously strong domain is now developing. Before interpreting " +
          "this as decline, ask what has changed in their environment: " +
          "new demands, role changes, or life events. Regression in the " +
          "profile often reflects context, not capability.",
      },
      fluctuation: {
        athlete:
          "Your profile has moved from {previous} to {current}. Profiles " +
          "shift between measurements. Some movement is normal variation, " +
          "not meaningful change. If your experience feels stable, trust " +
          "that over the numbers.",
        coach:
          "This athlete's profile has moved from {previous} to {current}. " +
          "Some variation between measurements is expected. Before acting " +
          "on this change, check whether the athlete's lived experience " +
          "matches the shift. If it does not, treat this as measurement " +
          "noise rather than a signal.",
      },
      sustained: {
        athlete:
          "Your profile remains {current}. Consistency over time means your " +
          "motivational pattern is stable. This does not mean static: the " +
          "same type can feel different depending on frustration levels and " +
          "context. Check in with how it feels, not just what it is called.",
        coach:
          "This athlete's profile remains {current}. A sustained type " +
          "suggests motivational stability. Use the frustration scores and " +
          "domain states to track change within the type. Stability in the " +
          "label does not mean nothing is moving underneath.",
      },
    },

    // -------------------------------------------------------------------
    // Measurement disclosure: 3 tiers x 2 audiences
    // Templates use {count} and {s} placeholders
    // -------------------------------------------------------------------
    measurementDisclosure: {
      early: {
        athlete:
          "This profile is based on {count} self-report measurement{s}. " +
          "It is a starting point, not a verdict. Self-report captures how " +
          "you see yourself right now. It does not capture everything. " +
          "As you take more measurements, the picture will sharpen.",
        coach:
          "This profile is based on {count} self-report measurement{s}. " +
          "Treat it as a conversation starter, not a conclusion. " +
          "Self-report reflects the athlete's perception, which matters, " +
          "but it is one lens. Early profiles are useful for opening " +
          "dialogue, not for making decisions.",
      },
      developing: {
        athlete:
          "This profile is based on {count} measurements. The picture is " +
          "becoming clearer. Patterns that appear across multiple " +
          "measurements carry more weight than any single snapshot. " +
          "You can start trusting the broad strokes.",
        coach:
          "This profile is based on {count} measurements. With repeated " +
          "data, patterns become more reliable. Consistent signals across " +
          "measurements deserve attention. Changes between measurements " +
          "are worth exploring. The profile is developing real diagnostic " +
          "value.",
      },
      established: {
        athlete:
          "This profile is based on {count} measurements. It is well " +
          "calibrated. The patterns here reflect sustained tendencies, " +
          "not one-time snapshots. You can trust this as a reliable picture " +
          "of your motivational profile, while remembering that profiles " +
          "can and do change.",
        coach:
          "This profile is based on {count} measurements. At this depth, " +
          "the profile is well calibrated. Stable patterns are trustworthy. " +
          "Changes from established baselines are meaningful signals that " +
          "warrant conversation. Self-report limitations remain, but " +
          "repeated measurement reduces their impact.",
      },
    },
  };

  // =========================================================================
  // Narrative helper functions
  // =========================================================================

  var DOMAIN_NAMES = {
    ambition: "Ambition",
    belonging: "Belonging",
    craft: "Craft",
  };

  /**
   * Return a confidence qualifier word.
   * >0.7: "likely", 0.5-0.7: "appears to be", <0.5: "may be", null: ""
   */
  function confidenceQualifier(posteriorConfidence) {
    if (posteriorConfidence == null) return "";
    if (posteriorConfidence > 0.7) return "likely";
    if (posteriorConfidence >= 0.5) return "appears to be";
    return "may be";
  }

  /**
   * Fill {domain}, {domain_lower}, {previous}, {current}, {count}, {s}
   * placeholders in a template string.
   */
  function fillTemplate(template, vars) {
    var result = template;
    for (var key in vars) {
      result = result.split("{" + key + "}").join(vars[key]);
    }
    return result;
  }

  /**
   * Generate archetype narrative for a given type and audience.
   *
   * @param {string} typeName - One of 8 archetype names.
   * @param {string} audience - "athlete" or "coach".
   * @returns {object} {identity_description, strengths[], growth_edge}
   */
  function generateArchetypeNarrative(typeName, audience) {
    var data = NARRATIVE_DATA.archetypeNarratives[typeName];
    if (!data) throw new Error("Unknown archetype: " + typeName);
    var content = data[audience];
    if (!content) throw new Error("Unknown audience: " + audience);
    return {
      identity_description: content.identity_description,
      strengths: content.strengths.slice(),
      growth_edge: content.growth_edge,
    };
  }

  /**
   * Generate domain state narrative.
   *
   * @param {string} domain - "ambition", "belonging", or "craft"
   * @param {string} state - "Thriving", "Vulnerable", "Mild", or "Distressed"
   * @param {number} score - Domain satisfaction score (0-10)
   * @param {string} audience - "athlete" or "coach"
   * @param {number|null} [posteriorConfidence] - Optional confidence for qualifier
   * @returns {object}
   */
  function generateDomainStateNarrative(
    domain,
    state,
    score,
    audience,
    posteriorConfidence
  ) {
    var stateData = NARRATIVE_DATA.domainStateNarratives[state];
    if (!stateData) throw new Error("Unknown state: " + state);
    var content = stateData[audience];
    if (!content) throw new Error("Unknown audience: " + audience);

    var domainLabel = DOMAIN_NAMES[domain];
    if (!domainLabel) throw new Error("Unknown domain: " + domain);

    var vars = { domain: domainLabel, domain_lower: domain };

    var stateDescription = fillTemplate(content.state_description, vars);

    // Insert confidence qualifier if provided
    var qualifier = confidenceQualifier(posteriorConfidence);
    if (qualifier) {
      stateDescription = stateDescription
        .replace(
          "Your " + domainLabel + " is",
          "Your " + domainLabel + " " + qualifier
        )
        .replace(
          "This athlete's " + domainLabel + " is",
          "This athlete's " + domainLabel + " " + qualifier
        );
    }

    var result = { state_description: stateDescription };

    if (audience === "athlete") {
      result.reflection_prompt = fillTemplate(content.reflection_prompt, vars);
    } else {
      result.conversation_starter = fillTemplate(
        content.conversation_starter,
        vars
      );
    }

    return result;
  }

  /**
   * Generate frustration signature narrative.
   *
   * @param {object} signature - {label, domain, risk}
   * @param {string} audience - "athlete" or "coach"
   * @returns {object} {description, action_prompt}
   */
  function generateSignatureNarrative(signature, audience) {
    var label = signature.label || "";
    var data = NARRATIVE_DATA.signatureNarratives[label];
    if (!data) throw new Error("Unknown signature: " + label);
    var content = data[audience];
    if (!content) throw new Error("Unknown audience: " + audience);
    return {
      description: content.description,
      action_prompt: content.action_prompt,
    };
  }

  /**
   * Generate transition narrative.
   *
   * @param {string} previousType
   * @param {string} currentType
   * @param {string} transitionType - "growth", "exploration", "regression", "fluctuation", "sustained"
   * @param {string} audience
   * @returns {string}
   */
  function generateTransitionNarrative(
    previousType,
    currentType,
    transitionType,
    audience
  ) {
    var data = NARRATIVE_DATA.transitionNarratives[transitionType];
    if (!data) throw new Error("Unknown transition type: " + transitionType);
    var template = data[audience];
    if (!template) throw new Error("Unknown audience: " + audience);
    return fillTemplate(template, { previous: previousType, current: currentType });
  }

  /**
   * Generate measurement disclosure text.
   *
   * @param {number} measurementCount - Number of measurements (>= 1).
   * @param {string} audience - "athlete" or "coach".
   * @returns {string}
   */
  function generateMeasurementDisclosure(measurementCount, audience) {
    if (measurementCount < 1)
      throw new Error("measurementCount must be >= 1");

    var tier;
    if (measurementCount <= 2) tier = "early";
    else if (measurementCount <= 5) tier = "developing";
    else tier = "established";

    var template = NARRATIVE_DATA.measurementDisclosure[tier][audience];
    var s = measurementCount === 1 ? "" : "s";
    return fillTemplate(template, {
      count: String(measurementCount),
      s: s,
    });
  }

  // =========================================================================
  // Transition Engine
  // =========================================================================

  var ARCHETYPE_LEVELS = {
    Seeker: 0,
    Pioneer: 1,
    Anchor: 1,
    Artisan: 1,
    Captain: 2,
    Architect: 2,
    Mentor: 2,
    Integrator: 3,
  };

  var ARCHETYPE_DOMAINS = {
    Seeker: [],
    Pioneer: ["ambition"],
    Anchor: ["belonging"],
    Artisan: ["craft"],
    Captain: ["ambition", "belonging"],
    Architect: ["ambition", "craft"],
    Mentor: ["belonging", "craft"],
    Integrator: ["ambition", "belonging", "craft"],
  };

  /**
   * Return the confidence threshold for a given measurement window.
   * Shorter windows require higher confidence.
   */
  function confidenceThresholdForWindow(weeksElapsed) {
    if (weeksElapsed <= 4) return 0.75;
    if (weeksElapsed <= 8) return 0.65;
    return 0.6;
  }

  /**
   * Classify an archetype transition.
   *
   * @param {string} previousType
   * @param {string} currentType
   * @param {number} [posteriorConfidence=1.0]
   * @param {number} [weeksElapsed=2]
   * @returns {string} "sustained", "fluctuation", "growth", "exploration", or "regression"
   */
  function classifyTransition(
    previousType,
    currentType,
    posteriorConfidence,
    weeksElapsed
  ) {
    if (posteriorConfidence === undefined) posteriorConfidence = 1.0;
    if (weeksElapsed === undefined) weeksElapsed = 2;

    if (ARCHETYPE_LEVELS[previousType] === undefined)
      throw new Error("Unknown archetype: " + previousType);
    if (ARCHETYPE_LEVELS[currentType] === undefined)
      throw new Error("Unknown archetype: " + currentType);

    if (previousType === currentType) return "sustained";

    var threshold = confidenceThresholdForWindow(weeksElapsed);
    if (posteriorConfidence < threshold) return "fluctuation";

    var prevLevel = ARCHETYPE_LEVELS[previousType];
    var currLevel = ARCHETYPE_LEVELS[currentType];

    if (currLevel > prevLevel) return "growth";
    if (currLevel < prevLevel) return "regression";
    return "exploration";
  }

  /**
   * Return domains gained in a transition.
   */
  function getDomainsGained(previousType, currentType) {
    var prev = ARCHETYPE_DOMAINS[previousType] || [];
    var curr = ARCHETYPE_DOMAINS[currentType] || [];
    var gained = [];
    for (var i = 0; i < curr.length; i++) {
      if (prev.indexOf(curr[i]) === -1) gained.push(curr[i]);
    }
    return gained.sort();
  }

  /**
   * Return domains lost in a transition.
   */
  function getDomainsLost(previousType, currentType) {
    var prev = ARCHETYPE_DOMAINS[previousType] || [];
    var curr = ARCHETYPE_DOMAINS[currentType] || [];
    var lost = [];
    for (var i = 0; i < prev.length; i++) {
      if (curr.indexOf(prev[i]) === -1) lost.push(prev[i]);
    }
    return lost.sort();
  }

  // =========================================================================
  // TransitionTracker
  // =========================================================================

  function TransitionTracker() {
    this.history = [];
  }

  /**
   * Record a new measurement and classify the transition.
   *
   * @param {string} typeName - Current archetype name.
   * @param {number} [posteriorConfidence=1.0]
   * @param {number} [weeksSinceLast=2]
   * @returns {object} Entry with transition classification and metadata.
   */
  TransitionTracker.prototype.record = function (
    typeName,
    posteriorConfidence,
    weeksSinceLast
  ) {
    if (posteriorConfidence === undefined) posteriorConfidence = 1.0;
    if (weeksSinceLast === undefined) weeksSinceLast = 2;

    var entry = {
      typeName: typeName,
      posteriorConfidence: posteriorConfidence,
      measurementNumber: this.history.length + 1,
    };

    if (this.history.length === 0) {
      entry.transition = null;
      entry.transitionType = null;
    } else {
      var previous = this.history[this.history.length - 1];
      var transType = classifyTransition(
        previous.typeName,
        typeName,
        posteriorConfidence,
        weeksSinceLast
      );
      entry.transition = {
        from: previous.typeName,
        to: typeName,
        type: transType,
        domainsGained: getDomainsGained(previous.typeName, typeName),
        domainsLost: getDomainsLost(previous.typeName, typeName),
      };
      entry.transitionType = transType;
    }

    this.history.push(entry);
    return entry;
  };

  /**
   * Return how many consecutive measurements the current type has been held.
   */
  TransitionTracker.prototype.getSustainedCount = function () {
    if (this.history.length === 0) return 0;
    var currentType = this.history[this.history.length - 1].typeName;
    var count = 0;
    for (var i = this.history.length - 1; i >= 0; i--) {
      if (this.history[i].typeName === currentType) {
        count++;
      } else {
        break;
      }
    }
    return count;
  };

  /**
   * Return the sequence of archetype levels over time.
   */
  TransitionTracker.prototype.getGrowthTrajectory = function () {
    var trajectory = [];
    for (var i = 0; i < this.history.length; i++) {
      trajectory.push(ARCHETYPE_LEVELS[this.history[i].typeName] || 0);
    }
    return trajectory;
  };

  /**
   * Return counts of each transition type.
   */
  TransitionTracker.prototype.getTransitionCounts = function () {
    var counts = {
      growth: 0,
      exploration: 0,
      regression: 0,
      fluctuation: 0,
      sustained: 0,
    };
    for (var i = 0; i < this.history.length; i++) {
      var tt = this.history[i].transitionType;
      if (tt !== null && counts[tt] !== undefined) {
        counts[tt]++;
      }
    }
    return counts;
  };

  /**
   * Return the most frequently occurring archetype.
   */
  TransitionTracker.prototype.getMostCommonType = function () {
    if (this.history.length === 0) return null;
    var typeCounts = {};
    for (var i = 0; i < this.history.length; i++) {
      var name = this.history[i].typeName;
      typeCounts[name] = (typeCounts[name] || 0) + 1;
    }
    var best = null;
    var bestCount = -1;
    for (var t in typeCounts) {
      if (typeCounts[t] > bestCount) {
        bestCount = typeCounts[t];
        best = t;
      }
    }
    return best;
  };

  /**
   * Return the most recent archetype.
   */
  TransitionTracker.prototype.getCurrentType = function () {
    if (this.history.length === 0) return null;
    return this.history[this.history.length - 1].typeName;
  };

  /**
   * Return a comprehensive summary of the trajectory.
   */
  TransitionTracker.prototype.getSummary = function () {
    if (this.history.length === 0) {
      return {
        currentType: null,
        mostCommonType: null,
        measurementCount: 0,
        sustainedCount: 0,
        growthTrajectory: [],
        transitionCounts: {
          growth: 0,
          exploration: 0,
          regression: 0,
          fluctuation: 0,
          sustained: 0,
        },
        currentLevel: null,
        highestLevelReached: null,
      };
    }

    var trajectory = this.getGrowthTrajectory();
    return {
      currentType: this.getCurrentType(),
      mostCommonType: this.getMostCommonType(),
      measurementCount: this.history.length,
      sustainedCount: this.getSustainedCount(),
      growthTrajectory: trajectory,
      transitionCounts: this.getTransitionCounts(),
      currentLevel: trajectory[trajectory.length - 1],
      highestLevelReached: Math.max.apply(null, trajectory),
    };
  };

  // =========================================================================
  // Onboarding Scorer
  // =========================================================================

  var ONBOARDING_ITEMS = {
    a_sat: ["AS1"],
    a_frust: ["AF1"],
    b_sat: ["BS1"],
    b_frust: ["BF1"],
    c_sat: ["CS1"],
    c_frust: ["CF1"],
  };

  var ONBOARDING_SE = 1.5;

  var DOMAIN_LABELS = {
    ambition: "Ambition",
    belonging: "Belonging",
    craft: "Craft",
  };

  /**
   * Normalize a 1-7 Likert value to 0-10 scale.
   * Formula: (value - 1) / (7 - 1) * 10
   */
  function normalizeTo10(value) {
    return ((value - 1) / 6) * 10;
  }

  /**
   * Score a 6-item onboarding assessment.
   *
   * Returns directional signals, archetype probability distributions,
   * and narrative invitations. Does NOT return hard type labels,
   * domain states, frustration signatures, or Belbin roles.
   *
   * @param {object} responses - Map of item codes (AS1, AF1, BS1, BF1, CS1, CF1)
   *                             to 1-7 Likert scale integers.
   * @returns {object} Onboarding results with suppressed labels.
   */
  function scoreOnboarding(responses) {
    // Validate
    var required = ["AS1", "AF1", "BS1", "BF1", "CS1", "CF1"];
    for (var r = 0; r < required.length; r++) {
      var item = required[r];
      if (responses[item] === undefined)
        throw new Error("Missing onboarding item: " + item);
      var val = responses[item];
      if (typeof val !== "number" || val !== Math.floor(val))
        throw new Error("Response for " + item + " must be an integer");
      if (val < 1 || val > 7)
        throw new Error("Response for " + item + " must be 1-7, got " + val);
    }

    // Compute single-item subscale scores
    var subscales = {};
    for (var subscaleKey in ONBOARDING_ITEMS) {
      var items = ONBOARDING_ITEMS[subscaleKey];
      var rawValue = responses[items[0]];
      subscales[subscaleKey] = normalizeTo10(rawValue);
    }

    // Create Bayesian profile with wide priors
    var profile = new ABCBayesianProfile();
    var ses = {};
    for (var sk in subscales) {
      ses[sk] = ONBOARDING_SE;
    }
    var bayesian = profile.updateAll(subscales, ses);

    // Archetype probabilities
    var archetypeProbs = profile.getArchetypeProbabilities();

    // Sort by probability
    var sortedProbs = [];
    for (var archName in archetypeProbs) {
      sortedProbs.push({ name: archName, probability: archetypeProbs[archName] });
    }
    sortedProbs.sort(function (a, b) {
      return b.probability - a.probability;
    });

    // Directional signals
    var satScores = {
      ambition: subscales.a_sat,
      belonging: subscales.b_sat,
      craft: subscales.c_sat,
    };

    var strongest = null;
    var strongestVal = -1;
    for (var dom in satScores) {
      if (satScores[dom] > strongestVal) {
        strongestVal = satScores[dom];
        strongest = dom;
      }
    }

    var developing = [];
    for (var d in satScores) {
      if (d !== strongest) developing.push(d);
    }

    var strongestLabel = DOMAIN_LABELS[strongest];
    var developingLabels = developing
      .map(function (dd) {
        return DOMAIN_LABELS[dd];
      })
      .join(" and ");

    var directionalNarrative =
      "Your responses suggest " +
      strongestLabel +
      " is your strongest " +
      "area right now. " +
      developingLabels +
      " are still developing.";

    var top1 = sortedProbs[0];
    var top2 = sortedProbs[1];

    var archetypeNarrative =
      "Based on your initial responses, you are most likely " +
      "a " +
      top1.name +
      " (" +
      Math.round(top1.probability * 100) +
      "%) or " +
      "a " +
      top2.name +
      " (" +
      Math.round(top2.probability * 100) +
      "%). " +
      "Take the full assessment for a clearer picture.";

    var invitation =
      "This is a starting point, not a label. " +
      "Six questions give a directional signal. " +
      "The full 36-item assessment takes about 8 minutes and " +
      "provides a complete profile with confidence bands.";

    // Build archetype probabilities as sorted object
    var sortedProbsObj = {};
    for (var sp = 0; sp < sortedProbs.length; sp++) {
      sortedProbsObj[sortedProbs[sp].name] = sortedProbs[sp].probability;
    }

    return {
      tier: "onboarding",
      itemsAnswered: 6,
      subscales: subscales,
      directional: {
        strongestDomain: strongest,
        developingDomains: developing,
        narrative: directionalNarrative,
      },
      archetypeProbabilities: sortedProbsObj,
      topCandidates: [
        { name: top1.name, probability: top1.probability },
        { name: top2.name, probability: top2.probability },
      ],
      narratives: {
        directional: directionalNarrative,
        archetypeCandidates: archetypeNarrative,
        invitation: invitation,
      },
      bayesian: bayesian,
      suppressed: [
        "typeName",
        "domainStates",
        "frustrationSignatures",
        "belbinRoles",
      ],
    };
  }

  // =========================================================================
  // Fatigue Timescale Classification
  // =========================================================================

  /**
   * Compute OLS slope for a sequence of values.
   * Port of transition_engine.py _compute_slope.
   *
   * @param {number[]} values - Chronological float values.
   * @returns {number} Slope (change per measurement period).
   */
  function _computeSlope(values) {
    var n = values.length;
    if (n < 2) return 0.0;

    var xMean = (n - 1) / 2.0;
    var ySum = 0;
    for (var i = 0; i < n; i++) ySum += values[i];
    var yMean = ySum / n;

    var numerator = 0.0;
    var denominator = 0.0;
    for (var j = 0; j < n; j++) {
      var xDiff = j - xMean;
      numerator += xDiff * (values[j] - yMean);
      denominator += xDiff * xDiff;
    }

    if (denominator === 0) return 0.0;
    return numerator / denominator;
  }

  /**
   * Classify frustration as acute, chronic, or mixed.
   * Port of transition_engine.py classify_fatigue_timescale (lines 152-206).
   *
   * Acute fatigue is a single spike (recoverable with rest).
   * Chronic fatigue is a sustained trend (requires structural change).
   * Based on Muller et al. (2021): two hidden fatigue states on different timescales.
   *
   * @param {number[]} frustrationHistory - Frustration scores (0-10), most recent last.
   * @param {object} [opts] - Optional parameters.
   * @param {number} [opts.windowShort=2] - Recent measurements for spike detection.
   * @param {number} [opts.windowLong=6] - Measurements for trend detection.
   * @param {number} [opts.spikeThreshold=1.5] - Minimum score increase for a spike.
   * @param {number} [opts.slopeThreshold=0.3] - Minimum slope for a trend.
   * @returns {string} "acute", "chronic", or "mixed"
   */
  function classifyFatigueTimescale(frustrationHistory, opts) {
    opts = opts || {};
    var windowShort = opts.windowShort !== undefined ? opts.windowShort : 2;
    var windowLong = opts.windowLong !== undefined ? opts.windowLong : 6;
    var spikeThreshold = opts.spikeThreshold !== undefined ? opts.spikeThreshold : 1.5;
    var slopeThreshold = opts.slopeThreshold !== undefined ? opts.slopeThreshold : 0.3;

    if (frustrationHistory.length < 3) return "acute";

    var recent = frustrationHistory.slice(-windowShort);
    var hasSpike = false;
    if (recent.length >= 2) {
      var change = recent[recent.length - 1] - recent[0];
      hasSpike = change >= spikeThreshold;
    }

    var history = frustrationHistory.slice(-windowLong);
    var hasTrend = false;
    if (history.length >= 3) {
      var slope = _computeSlope(history);
      hasTrend = slope >= slopeThreshold;
    }

    if (hasSpike && hasTrend) return "mixed";
    if (hasTrend) return "chronic";
    return "acute";
  }

  // =========================================================================
  // Domain Contexts
  // =========================================================================

  var DOMAIN_CONTEXTS = {
    sport: {
      label: "Athletic Context",
      domains: {
        ambition: { label: "Ambition" },
        belonging: { label: "Belonging" },
        craft: { label: "Craft" },
      },
    },
    professional: {
      label: "Professional Context",
      domains: {
        ambition: { label: "Drive" },
        belonging: { label: "Connection" },
        craft: { label: "Mastery" },
      },
    },
    transition: {
      label: "Transition Context",
      domains: {
        ambition: { label: "Purpose" },
        belonging: { label: "Community" },
        craft: { label: "Growth" },
      },
    },
    military: {
      label: "Military Context",
      domains: {
        ambition: { label: "Mission" },
        belonging: { label: "Unit Cohesion" },
        craft: { label: "Proficiency" },
      },
    },
    healthcare: {
      label: "Healthcare Context",
      domains: {
        ambition: { label: "Calling" },
        belonging: { label: "Team Trust" },
        craft: { label: "Clinical Skill" },
      },
    },
  };

  /**
   * Get domain labels for a given context.
   *
   * @param {string} context - One of: sport, professional, transition, military, healthcare.
   * @returns {object} Map of domain key to label, e.g. {ambition: "Drive", belonging: "Connection", craft: "Mastery"}.
   */
  function getDomainLabels(context) {
    var ctx = DOMAIN_CONTEXTS[context];
    if (!ctx) throw new Error("Unknown context: " + context);
    var labels = {};
    for (var dom in ctx.domains) {
      labels[dom] = ctx.domains[dom].label;
    }
    return labels;
  }

  // =========================================================================
  // Public API
  // =========================================================================

  return {
    // Classes
    BayesianScorer: BayesianScorer,
    ABCBayesianProfile: ABCBayesianProfile,
    TransitionTracker: TransitionTracker,

    // Functions
    normalCDF: normalCDF,
    classifyWithUncertainty: classifyWithUncertainty,
    getArchetypeProbabilities: getArchetypeProbabilities,
    classifyTransition: classifyTransition,
    getDomainsGained: getDomainsGained,
    getDomainsLost: getDomainsLost,
    scoreOnboarding: scoreOnboarding,
    normalizeTo10: normalizeTo10,

    // Narrative generators
    generateArchetypeNarrative: generateArchetypeNarrative,
    generateDomainStateNarrative: generateDomainStateNarrative,
    generateSignatureNarrative: generateSignatureNarrative,
    generateTransitionNarrative: generateTransitionNarrative,
    generateMeasurementDisclosure: generateMeasurementDisclosure,
    confidenceQualifier: confidenceQualifier,
    fillTemplate: fillTemplate,

    // Fatigue timescale
    classifyFatigueTimescale: classifyFatigueTimescale,

    // Domain contexts
    DOMAIN_CONTEXTS: DOMAIN_CONTEXTS,
    getDomainLabels: getDomainLabels,

    // Data
    NARRATIVE_DATA: NARRATIVE_DATA,
    ARCHETYPE_LEVELS: ARCHETYPE_LEVELS,
    ARCHETYPE_DOMAINS: ARCHETYPE_DOMAINS,
    ARCHETYPE_PATTERNS: ARCHETYPE_PATTERNS,
    DOMAIN_PAIRS: DOMAIN_PAIRS,
    DOMAIN_NAMES: DOMAIN_NAMES,
    SUBSCALE_NAMES: SUBSCALE_NAMES,
    SAT_THRESHOLD: SAT_THRESHOLD,
    FRUST_THRESHOLD: FRUST_THRESHOLD,
    TYPE_ACTIVATION_THRESHOLD: TYPE_ACTIVATION_THRESHOLD,
    ONBOARDING_SE: ONBOARDING_SE,
  };
})();
