/**
 * Enhanced submitAssessment() - replaces the original in index.html.
 * Requires personalization.js to be loaded first.
 *
 * Reference: improvement-plan-personalization-engine Section 11
 */

// Persistent state across assessments (simulates longitudinal tracking)
window._bayesianProfileScorers = window._bayesianProfileScorers || {};
window._transitionTracker = window._transitionTracker || null;
window._measurementCount = window._measurementCount || 0;
window._currentAudience = 'athlete'; // toggle via UI
window._frustrationHistory = window._frustrationHistory || {ambition: [], belonging: [], craft: []};
window._currentContext = window._currentContext || 'sport';


function submitAssessmentEnhanced() {
    const P = window.ABCPersonalization;
    if (!P) {
        // Fallback to original if personalization.js not loaded
        return submitAssessment();
    }

    const result = scoreAssessment();
    const audience = window._currentAudience || 'athlete';
    window._measurementCount++;

    // Track frustration history per domain
    window._frustrationHistory.ambition.push(result.subscales.a_frust);
    window._frustrationHistory.belonging.push(result.subscales.b_frust);
    window._frustrationHistory.craft.push(result.subscales.c_frust);
    const measurementCount = window._measurementCount;

    // Initialize transition tracker on first use
    if (!window._transitionTracker) {
        window._transitionTracker = new P.TransitionTracker();
    }

    // --- Bayesian update ---
    const subscaleKeys = ['a_sat', 'a_frust', 'b_sat', 'b_frust', 'c_sat', 'c_frust'];
    if (!window._bayesianProfileScorers.a_sat) {
        subscaleKeys.forEach(k => {
            window._bayesianProfileScorers[k] = new P.BayesianScorer(5.0, 2.0);
        });
    }
    const posteriors = {};
    subscaleKeys.forEach(k => {
        const se = currentTier === 'onboarding' ? 1.5 : 0.8;
        posteriors[k] = window._bayesianProfileScorers[k].update(result.subscales[k], se);
    });

    // Domain state probabilities
    const domainStateProbs = {};
    const domainPairsForBayes = [
        ['ambition', 'a_sat', 'a_frust'],
        ['belonging', 'b_sat', 'b_frust'],
        ['craft', 'c_sat', 'c_frust']
    ];
    domainPairsForBayes.forEach(([dom, satK, frustK]) => {
        domainStateProbs[dom] = P.classifyWithUncertainty(
            window._bayesianProfileScorers[satK],
            window._bayesianProfileScorers[frustK]
        );
    });

    // Archetype probabilities
    const archetypeProbs = P.getArchetypeProbabilities(
        window._bayesianProfileScorers.a_sat,
        window._bayesianProfileScorers.b_sat,
        window._bayesianProfileScorers.c_sat
    );
    const sortedArchetypes = Object.entries(archetypeProbs)
        .sort((a, b) => b[1] - a[1]);

    // Type confidence
    const typeConfidence = archetypeProbs[result.typeName] || 0;

    // Transition tracking
    const transition = window._transitionTracker.record(
        result.typeName, typeConfidence, 2
    );

    // --- Narratives ---
    const archNarr = P.generateArchetypeNarrative(result.typeName, audience) || {};
    const disclosure = P.generateMeasurementDisclosure(measurementCount, audience);

    // Confidence qualifier
    function confLabel(prob) {
        if (prob >= 0.75) return { text: 'high', cls: 'confidence-high' };
        if (prob >= 0.50) return { text: 'moderate', cls: 'confidence-moderate' };
        return { text: 'low', cls: 'confidence-low' };
    }

    // --- RENDER ---
    const typeDesc = TYPE_DESCS[result.typeName] || {};
    const domColour = DOMAIN_COLOURS[result.domDomain] || '#555';
    let html = '';

    // === Onboarding tier: suppressed labels ===
    if (currentTier === 'onboarding') {
        html += '<div class="result-type-card">';
        html += `<div class="result-type-header" style="background:${domColour}">`;
        html += '<div class="result-type-name" style="font-size:1.3rem;">Your Initial Signal</div>';
        html += '<div class="result-type-tagline">Based on 6 questions. Take the full assessment for a complete profile.</div>';
        html += '</div>';
        html += '<div class="result-body">';

        // Directional signal
        const sats = { ambition: result.subscales.a_sat, belonging: result.subscales.b_sat, craft: result.subscales.c_sat };
        const strongest = Object.entries(sats).sort((a, b) => b[1] - a[1])[0][0];
        const strongLabel = strongest.charAt(0).toUpperCase() + strongest.slice(1);
        html += `<div class="narrative-body" style="margin-bottom:1.5rem;">`;
        html += `<p>Your responses suggest <strong>${strongLabel}</strong> is your strongest area right now. The other domains are still developing.</p>`;
        html += '</div>';

        // Archetype probability bars
        html += '<h4 style="font-size:0.8rem;text-transform:uppercase;letter-spacing:0.06em;color:var(--muted);margin-bottom:0.8rem;">Most Likely Profiles</h4>';
        sortedArchetypes.slice(0, 4).forEach(([name, prob]) => {
            html += '<div class="archetype-prob-bar">';
            html += `<span class="archetype-prob-label">${name}</span>`;
            html += `<div class="archetype-prob-track"><div class="archetype-prob-fill" style="width:${(prob * 100).toFixed(0)}%"></div></div>`;
            html += `<span class="archetype-prob-val">${(prob * 100).toFixed(0)}%</span>`;
            html += '</div>';
        });

        // Invitation
        html += '<div style="margin-top:1.5rem;padding:1rem;background:#f0f4ff;border-radius:8px;text-align:center;">';
        html += '<p style="font-size:0.95rem;font-weight:600;margin-bottom:0.3rem;">This is a starting point, not a label.</p>';
        html += '<p style="font-size:0.88rem;color:var(--muted);">The full 36-item assessment takes about 8 minutes and provides a complete profile with confidence bands.</p>';
        html += '</div>';

        html += '</div></div>';

    } else {
        // === Standard/Full tier: narrative-first results ===
        var contextLabels = P.getDomainLabels(window._currentContext);
        var contextInfo = P.DOMAIN_CONTEXTS[window._currentContext];
        html += '<div class="result-type-card">';

        // Context label
        html += `<div style="text-align:center;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.08em;color:var(--muted);padding:0.5rem 0 0;">${contextInfo ? contextInfo.label : 'Athletic Context'}</div>`;

        // Header
        html += `<div class="result-type-header" style="background:${domColour}">`;
        html += `<div class="result-type-name">${result.typeName}</div>`;
        const conf = confLabel(typeConfidence);
        html += `<div class="result-type-tagline"><span class="confidence-badge ${conf.cls}">${conf.text} confidence</span></div>`;
        html += `<div class="result-type-profile">Profile: ${result.profileCode}</div>`;
        html += '</div>';

        html += '<div class="result-body">';

        // Narrative (the product)
        if (archNarr.identity_description) {
            html += `<div class="narrative-body" style="margin-bottom:1.5rem;">`;
            html += `<p>${archNarr.identity_description}</p>`;
            html += '</div>';
        }

        // Domain cards with posterior confidence
        html += '<div class="result-domains">';
        domainPairsForBayes.forEach(([dom, satK, frustK]) => {
            const label = contextLabels[dom] || (dom.charAt(0).toUpperCase() + dom.slice(1));
            const state = result.domainStates[dom];
            const stateProb = domainStateProbs[dom];
            const stateConf = confLabel(stateProb.confidence);
            const stateCol = STATE_COLOURS[state] || '#aaa';
            const domNarr = P.generateDomainStateNarrative(dom, state, result.subscales[satK], audience, stateProb.confidence) || {};

            html += `<div class="result-domain" style="border-top:3px solid ${DOMAIN_COLOURS[dom]}">`;
            html += `<h4 style="color:${DOMAIN_COLOURS[dom]}">${label}</h4>`;
            html += `<div class="domain-scores">Sat: ${result.subscales[satK].toFixed(1)} / Frust: ${result.subscales[frustK].toFixed(1)}</div>`;
            html += `<span class="state-badge" style="background:${stateCol}">${state}</span> `;
            html += `<span class="confidence-badge ${stateConf.cls}">${(stateProb.confidence * 100).toFixed(0)}%</span>`;

            // Fatigue timescale badge (after 3+ measurements)
            if (window._frustrationHistory[dom] && window._frustrationHistory[dom].length >= 3) {
                const fatigueType = P.classifyFatigueTimescale(window._frustrationHistory[dom]);
                const fatigueColors = {acute: '#22c55e', chronic: '#f59e0b', mixed: '#ef4444'};
                html += ` <span style="display:inline-block;font-size:0.7rem;padding:0.15rem 0.4rem;border-radius:3px;color:#fff;background:${fatigueColors[fatigueType] || '#888'};margin-left:0.3rem;">${fatigueType}</span>`;
            }

            if (domNarr.state_description) {
                html += `<div style="margin-top:0.5rem;font-size:0.85rem;line-height:1.5;color:#555;">${domNarr.state_description}</div>`;
            }
            if (domNarr.reflection_prompt && audience === 'athlete') {
                html += `<div class="reflection-prompt" style="margin-top:0.5rem;font-size:0.85rem;">${domNarr.reflection_prompt}</div>`;
            }
            if (domNarr.conversation_starter && audience === 'coach') {
                html += `<div class="reflection-prompt" style="margin-top:0.5rem;font-size:0.85rem;border-left-color:var(--craft);">${domNarr.conversation_starter}</div>`;
            }

            // Personalized threshold (after 6+ measurements)
            if (window._bayesianProfileScorers[satK]) {
                const persThresh = window._bayesianProfileScorers[satK].getPersonalizedThreshold(1.5, 3.0);
                if (persThresh !== null) {
                    html += `<div style="margin-top:0.4rem;font-size:0.78rem;color:var(--muted);">Personal threshold: ${persThresh.toFixed(1)}</div>`;
                }
            }

            html += '</div>';
        });
        html += '</div>';

        // Archetype probability distribution
        html += '<div style="margin-bottom:1.5rem;">';
        html += '<h4 style="font-size:0.8rem;text-transform:uppercase;letter-spacing:0.06em;color:var(--muted);margin-bottom:0.8rem;">Profile Probability</h4>';
        sortedArchetypes.forEach(([name, prob]) => {
            if (prob < 0.01) return;
            const highlight = name === result.typeName ? 'font-weight:700;' : '';
            html += '<div class="archetype-prob-bar">';
            html += `<span class="archetype-prob-label" style="${highlight}">${name}</span>`;
            html += `<div class="archetype-prob-track"><div class="archetype-prob-fill" style="width:${(prob * 100).toFixed(0)}%;${name === result.typeName ? 'background:' + domColour : ''}"></div></div>`;
            html += `<span class="archetype-prob-val" style="${highlight}">${(prob * 100).toFixed(0)}%</span>`;
            html += '</div>';
        });
        html += '</div>';

        // Strengths
        if (archNarr.strengths && archNarr.strengths.length > 0) {
            html += '<div class="result-strengths"><h4>Strengths</h4><ul>';
            archNarr.strengths.forEach(s => html += `<li>${s}</li>`);
            html += '</ul></div>';
        }

        // Growth edge
        if (archNarr.growth_edge) {
            html += '<div class="result-growth"><h4>Growth Edge</h4><p>' + archNarr.growth_edge + '</p></div>';
        }

        // Frustration signatures with narratives
        if (result.frustSigs.length > 0) {
            html += '<div class="result-sigs"><h4>Frustration Signals</h4>';
            result.frustSigs.forEach(sig => {
                const cls = sig.risk === 'high' ? 'sig-badge-high' : 'sig-badge-medium';
                const sigNarr = P.generateSignatureNarrative(sig, audience) || {};
                html += `<div style="margin-bottom:1rem;">`;
                html += `<span class="sig-badge ${cls}" style="margin-right:0.5rem;">${sig.label} (${sig.risk} risk)</span>`;
                if (sigNarr.description) {
                    html += `<div style="font-size:0.88rem;line-height:1.5;margin-top:0.4rem;">${sigNarr.description}</div>`;
                }
                if (sigNarr.action_prompt) {
                    html += `<div class="reflection-prompt" style="margin-top:0.4rem;font-size:0.85rem;">${sigNarr.action_prompt}</div>`;
                }
                html += '</div>';
            });
            html += '</div>';
        }

        // Transition narrative (if not first measurement)
        if (transition.transition && transition.transition.type !== 'sustained') {
            const transNarr = P.generateTransitionNarrative(transition.transition.from, transition.transition.to, transition.transition.type, audience) || '';
            if (transNarr) {
                html += '<div style="margin-bottom:1.5rem;padding:1rem;background:#f0faf4;border-radius:8px;border-left:3px solid var(--craft);">';
                html += '<h4 style="font-size:0.8rem;text-transform:uppercase;color:#1f7a35;margin-bottom:0.4rem;">Profile Change</h4>';
                html += `<p style="font-size:0.88rem;line-height:1.5;">${transNarr}</p>`;
                html += '</div>';
            }
        }

        // Trajectory summary
        if (window._transitionTracker && window._transitionTracker.history.length > 0) {
            const trajSummary = window._transitionTracker.getSummary();
            html += '<div style="margin-bottom:1.5rem;padding:0.6rem 1rem;background:#f8f8f8;border-radius:6px;font-size:0.8rem;color:var(--muted);">';
            html += `Measurement ${trajSummary.measurementCount} | Type stability: ${trajSummary.sustainedCount} sustained | Highest level reached: ${trajSummary.highestLevelReached}`;
            html += '</div>';
        }

        html += '</div></div>';
    }

    // Measurement disclosure (always shown)
    html += `<div class="measurement-disclosure">${disclosure}</div>`;

    // Audience toggle
    html += '<div style="text-align:center;margin-top:1rem;font-size:0.82rem;color:var(--muted);">';
    html += `Viewing as: <strong>${audience}</strong> `;
    const otherAudience = audience === 'athlete' ? 'coach' : 'athlete';
    html += `<button onclick="window._currentAudience='${otherAudience}';submitAssessmentEnhanced();" style="background:none;border:1px solid var(--border);border-radius:4px;padding:0.2rem 0.5rem;font-size:0.8rem;cursor:pointer;margin-left:0.3rem;">Switch to ${otherAudience}</button>`;
    html += '</div>';

    // Action buttons
    html += '<div style="text-align:center;margin-top:1rem;display:flex;gap:0.75rem;justify-content:center;flex-wrap:wrap;">';
    html += '<button class="assess-back" onclick="backToTierPicker()">Take Another Assessment</button>';
    html += `<button class="assess-submit" onclick="sendAssessToTrajectory()" style="font-size:0.9rem;padding:0.6rem 1.5rem;">Track My Trajectory</button>`;
    html += '</div>';

    // Store for trajectory
    window._lastAssessResult = result;

    document.getElementById('assess-results').innerHTML = html;
    document.getElementById('assess-questions').style.display = 'none';
    document.getElementById('assess-results').style.display = 'block';
    document.getElementById('assess-results').scrollIntoView({ behavior: 'smooth', block: 'start' });
    // Focus management: move focus to the results container for screen readers
    var resultsEl = document.getElementById('assess-results');
    resultsEl.setAttribute('tabindex', '-1');
    resultsEl.focus();

    // Persist to IndexedDB: save result, clear in-progress, save Bayesian state
    if (window.ABCOfflineStorage) {
        ABCOfflineStorage.saveResult(result);
        ABCOfflineStorage.clearInProgress();
        // Serialize Bayesian posteriors for cross-session persistence
        if (window._bayesianProfileScorers) {
            var bayesState = {};
            Object.keys(window._bayesianProfileScorers).forEach(function(k) {
                var scorer = window._bayesianProfileScorers[k];
                if (scorer && typeof scorer.getMean === 'function') {
                    bayesState[k] = { mean: scorer.getMean(), variance: scorer.getVariance ? scorer.getVariance() : null };
                }
            });
            ABCOfflineStorage.saveBayesianState(bayesState);
        }
        // Persist frustration history
        if (typeof ABCOfflineStorage.saveFrustrationHistory === 'function') {
            ABCOfflineStorage.saveFrustrationHistory(window._frustrationHistory);
        }
    }

    // If this was a reassessment triggered from the trajectory tab,
    // update the trajectory baseline and switch back
    if (window._trajReassessmentPending && typeof completeReassessment === 'function') {
        completeReassessment(result);
    }
}
