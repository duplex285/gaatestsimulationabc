# Outmatched and Under Pressure: A New Approach to Student-Athlete Wellbeing

## One Athlete, Invisible

A transfer athlete arrives in August. She attends every practice, hits her benchmarks, and passes her wellness screening. But she eats alone more often now. She stopped lingering after practice two weeks ago. She has not initiated a conversation with a teammate since she arrived. No coach, responsible for 44 athletes, notices. By October, she is in the transfer portal again. The system will ask what went wrong. The answer is that nothing in the system was designed to see it.

Her case is not unusual. It is the architecture working as designed. Screening questionnaires, wellness check-ins, open-door policies, the entire apparatus depends on a single channel: the athlete choosing to disclose. When that channel fails, the system treats it as a personal failure rather than what it is: a design failure. It assumes athletes possess the emotional awareness to monitor their own distress, the language to articulate it, and the trust to share it with figures who control their playing time, their scholarship, and their future.

## A System That Cannot See

Seventy-four percent of Division I athletic departments have no embedded mental health providers (Jones et al., 2022). That is a staffing gap. The consequences are measurable: mental health concerns among NCAA athletes remain 1.5 to 2 times above pre-pandemic baselines (NCAA, 2023), and the proportion of NCAA athlete deaths attributable to suicide doubled from 7.6% to 15.3% over two decades (Whelan et al., 2024).

The detection failure is equally stark. Chang et al. (2020) and Wolanin et al. (2016) found a five-fold gap between instrument-detected depression (21% of athletes screened) and self-reported depression (4%), meaning the vast majority of athletes experiencing clinical symptoms do not disclose them. Erickson et al. (2023) found a 67.5% false-negative rate on the IOC's screening tool: two out of three at-risk athletes pass undetected. These are not measurement errors. They reflect a system in which vulnerability carries professional consequences, and the person who holds the most authority over an athlete's competitive life also controls the environment in which help would be sought.

Then three disruptions arrived within three years. Legal sports betting (*Murphy v. NCAA*, 2018) converts athletes into involuntary betting lines. The transfer portal compresses team-building into free agency without guardrails. Name, Image, and Likeness (NIL, 2019) introduces financial stratification that fractures locker rooms. The market responded with generic wellness apps and AI chatbots built on the same broken assumption: the athlete engaging alone. The median 30-day retention rate for these tools is 3.3% (Baumel et al., 2019). The architecture fails because it assigns responsibility to the person with the least structural power (Rhoden, 2006).

## A Framework That Sees What's Coming

Self-Determination Theory (Deci & Ryan, 2000) identifies three basic psychological needs: autonomy, competence, and relatedness, and proposes that their satisfaction or frustration produces distinct outcomes. Supported needs produce intrinsic motivation and engagement. Frustrated needs produce burnout, depression, and disengagement. Bartholomew et al. (2011) demonstrated that need frustration uniquely predicts depression beyond low need satisfaction alone. The dark pathway is not the absence of the bright one.

Most psychological measures tell you what is happening. SDT shows you what is coming. Lonsdale and Hodge (2011) established that declining self-determination preceded increases in burnout; SDT constructs behave as leading indicators, not lagging ones. The predictive power is substantial: Lonsdale et al. (2009) reported that SDT variables accounted for up to 74% of the variance in global burnout, a figure that dwarfs the explanatory power of standard mood screenings.

The three disruptions press on the full infrastructure SDT identifies. Sports betting undermines autonomy by converting athletes into financial instruments and competence by redefining success through point spreads. NIL fractures relatedness by creating financial castes within teams. The transfer portal severs the relational bonds on which need satisfaction depends.

An athlete targeted by bettors, underpaid relative to teammates, and considering the portal is not experiencing three separate frustrations. She is experiencing one compounding environment. If need satisfaction predicts sustained competitive performance, and it does, then SDT is not exclusively a wellness tool. It is a competitive advantage.

## Distributing the Burden

Any honest proposal must confront the obvious objection: coaches are already overwhelmed. They manage NIL advising, transfer portal retention, betting-related athlete protection, compliance mandates, recruiting, and the actual job of coaching. The current system places the entire burden of detection on two parties who cannot carry it: the athlete, who must self-disclose, and the coach, who must notice. Both are set up to fail.

A system designed for reality distributes this burden across three levels. First, athletes need the capacity to understand their own psychological needs, not as a prerequisite for seeking help, but as a skill built over time. An athlete who recognizes that declining motivation is linked to a loss of autonomy, not laziness, gains self-leadership. She can name what is shifting before anyone else needs to. Second, coaches need a system that does the pattern recognition they cannot do at scale. A coach responsible for 44 athletes cannot track the relational dynamics of each one through observation alone. But a system that surfaces the three athletes whose belonging dropped sharply this week turns an impossible task into a focused one. Third, institutions need visibility into patterns no single person can see. When freshman belonging scores are 23% below the team average across three sports, that is not a coaching problem. It is an onboarding design problem.

The answer to the coaching constraint is not that coaches do more. It is that the system asks less of any single person.

## The ABC Assessment: Operationalising SDT for Athletes

The framework described above requires an instrument. We built one. The ABC assessment is a 36-item self-report questionnaire that measures satisfaction and frustration across three psychological need domains adapted from SDT for the sport context:

- **Ambition** (autonomy-directed goal pursuit): the drive to set and pursue personally meaningful goals in sport
- **Belonging** (relational connection): the experience of trust, inclusion, and unconditional regard within the team
- **Craft** (skill-directed competence): the drive to develop, refine, and demonstrate athletic skill

Each domain is measured by two subscales (satisfaction and frustration), with 6 items per subscale. Satisfaction and frustration are treated as independent constructs, not opposite ends of a single continuum (Vansteenkiste & Ryan, 2013; Chen et al., 2015). This matters because it allows detection of the "Vulnerable" state: an athlete whose satisfaction is high but whose frustration is also high. SDT identifies this as the burnout precursor, the "successful but suffering" pattern where performance is maintained but the cost is accumulating.

The instrument produces 8 motivational archetypes (Integrator, Captain, Architect, Mentor, Pioneer, Anchor, Artisan, Seeker) based on which domains are activated, with continuous frustration scores that preserve the full signal without the instability of categorical labels. Three measurement tiers (6, 18, and 36 items) allow progressive assessment that earns trust over time rather than demanding 12 minutes of a new user's attention before delivering any value.

This is not a licensed adaptation of any existing SDT instrument. It is a purpose-built assessment developed through AI-assisted research, iterative simulation, and the scientific literature. We are transparent about this. The analytic infrastructure has been validated on synthetic data; the item content requires empirical validation with real athletes. The gap between these two states is documented in full (see Validity Argument, below).

## What the Simulation Found

Before administering the instrument to athletes, we built a computational simulation to test whether the scoring infrastructure works under controlled conditions. The simulation generates synthetic populations, scores them through the full pipeline, and measures the psychometric properties of every output. All code is open source, all tests pass (493 of 493), and all parameters are documented for auditor review.

**The cascade signal is real in simulation.** The Vulnerable-to-Distressed cascade model confirms the SDT prediction: when an athlete's frustration begins to rise while satisfaction is still high, frustration leads satisfaction decline by an average of 1.5 measurement points. This is the detection window. A system monitoring frustration trajectories would see the signal before performance breaks down.

**The alert system achieves 81% sensitivity with 1.5 timepoints of lead time.** Using the Jacobson-Truax Reliable Change Index (Jacobson & Truax, 1991) to distinguish genuine change from measurement noise, the alert system detects 81% of simulated burnout transitions before they occur, at the cost of a 16% false-positive rate. The tradeoff is explicit: earlier detection requires accepting some false alerts. A differential evolution optimizer (analogous to R's rgenoud) searches across subscale weights, alert thresholds, and observation windows simultaneously to find the configuration that maximizes lead time subject to the false-positive constraint.

**The six subscales carry independent variance.** Bifactor analysis (Reise, 2012) on synthetic data produced an omega hierarchical of 0.246, meaning the six subscales are not dominated by a single general factor. Each subscale contributes unique information. This is important because it means that Ambition frustration, Belonging frustration, and Craft frustration are measuring different things, not the same thing three times. Murphy et al. (2023) raised concerns that the satisfaction/frustration distinction in the BPNSFS may be a method artifact from item-keying direction; the simulation includes a method-factor model that correctly detects this artifact when it is present and does not flag it when it is absent.

**Type stability reaches 90% with 6 items per subscale.** Classification reliability was the primary engineering challenge. With the original 4 items per subscale (24 total), per-domain classification agreement across simulated readministrations was only 67%, and type agreement was 31%. Expanding to 6 items per subscale (36 total) raised mean type stability to 90%, with a median of 100% (more than half of all simulated athletes receive the same type every time). The 7% of athletes who remain below 50% stability are identified and flagged as boundary cases whose classifications should be treated as provisional.

**Empirical thresholds will differ from assumed ones, but the infrastructure to derive them is built.** ROC analysis on simulated criterion data produced satisfaction and frustration thresholds (6.09 and 4.82, respectively) that differ from the fixed simulation thresholds (6.46 and 4.38) but fall within the bootstrap 95% confidence intervals. The Athlete Burnout Questionnaire (Raedeke & Smith, 2001; validated by Grugan et al., 2024, with ESEM providing superior fit and measurement invariance across gender, sport type, and age) is the planned criterion measure. When paired ABC and ABQ data reach N >= 200, the ROC infrastructure produces empirical thresholds that replace the assumed ones.

## What Could Go Wrong

The evidence linking environments to athlete wellbeing is strong. Deploying SDT as a practical leading indicator across diverse populations remains in its early stages, and the hardest objections deserve direct answers.

The first is surveillance. Any system that measures psychological states risks becoming a monitoring tool dressed as care, regardless of its designer's intentions. If an institution uses belonging data to justify cutting an athlete, the system has been weaponized. If relatedness scores become a proxy for "culture fit," the tool reproduces the very power dynamics it was built to counteract. The values must be non-negotiable: development, not surveillance, and every insight must function as a lens, not a label. Measurement must be indirect, captured through channels athletes already use. For example, text-based interventions retain 94% of young users at 30 days, compared to just 74% of app-based tools (Prior et al., 2024). The medium matters as much as the model.

The second is capacity. If the coaching staff lacks the ability to respond to what a system surfaces, the result is better-documented neglect. Detection without response is worse than no detection at all, because it removes the excuse of ignorance. The three-level distribution must include actionable guidance at each level, or it creates three burdens where there was one.

The third is equity. Can SDT-based measures distinguish clinical risk from normal fluctuation? Does indirect measurement work equally well across racial, cultural, and developmental contexts? If athletes are given a self-leadership vocabulary without psychological safety to use it, the tool becomes another performance expectation layered onto those least equipped to absorb it.

The fourth is honest uncertainty about AI-developed instruments. The ABC assessment was developed through AI-assisted research, not through the traditional process of expert item writing, focus groups, and multi-year validation studies. We believe this approach can produce a sound instrument, but we have not yet proved it. The simulation validates the analytic infrastructure; it does not validate the items themselves. That requires real athletes giving real responses, and the results may show that some items do not measure what we intended. We have built the infrastructure to detect that failure. The question is whether we have the discipline to act on it when the data arrives.

## What Comes Next

The case for investing despite these limitations is straightforward: the alternative, depending entirely on self-disclosure and coach intuition, does not work. The evidence says so. The athletes say so. The suicide data says so.

What is needed is a system grounded in SDT that tracks the three basic needs dynamically, distributes detection across athletes, coaches, and administrators, and treats every data point as a development tool owned by the athlete. It must be indirect enough to capture what self-report misses, specific enough to guide action, and honest enough to flag its own blind spots.

The measure of success is the moment a coach says, "I caught that early," and the moment an athlete says, "I knew something was off before anyone had to tell me."

## Further Research

The simulation provides the analytic infrastructure. Empirical validation requires the following programme of research, organized by the five sources of validity evidence specified in the *Standards for Educational and Psychological Testing* (APA, AERA, & NCME, 2014).

### Evidence based on test content

The 36 items were drafted through AI-assisted research using the SDT literature as the content domain. Three studies are needed:

1. **Expert panel review.** A panel of 5-7 sport psychologists and SDT researchers rates each item for domain alignment, construct representativeness, and absence of construct-irrelevant features. Items that fail to achieve >= 80% agreement on domain assignment are revised or replaced.

2. **Cognitive pretesting.** Think-aloud protocols with 10-15 athletes from diverse sports, competitive levels, genders, and cultural backgrounds. The key question: do athletes interpret "ambition" items as sport-relevant goal pursuit or as general life ambition? Do "belonging" items function differently for athletes in individual sports where "team" has a different meaning?

3. **Item-keying artifact analysis.** Murphy et al. (2023) demonstrated that the BPNSFS's satisfaction/frustration distinction may reflect item-wording direction rather than substantive constructs. The ABC assessment addresses this by reverse-coding two items per subscale and mixing positive and negative keying within each subscale. Bifactor-ESEM analysis on empirical data must confirm that the frustration subscales load on their intended factors after controlling for a method factor.

### Evidence based on response processes

Two studies address whether athletes engage the intended cognitive processes when responding:

4. **Social desirability assessment.** Administer the ABC alongside a brief social desirability scale (e.g., the Balanced Inventory of Desirable Responding) to test whether frustration subscales are suppressed by impression management, particularly in team settings where coaches may have access to aggregate data.

5. **Response time analysis.** Examine whether athletes who take unusually long or short on specific items produce different factor structures, which would suggest construct-irrelevant processing.

### Evidence based on internal structure

Three studies validate the measurement model:

6. **Confirmatory factor analysis on empirical data.** The simulation achieves perfect CFA fit because the data was generated to match the model. Empirical CFA on N >= 300 real athlete responses is the true test. Both CFA and ESEM should be reported, following Grugan et al. (2024), who demonstrated that ESEM provides superior fit for the ABQ.

7. **Longitudinal measurement invariance.** The 6-factor structure must hold across repeated administrations over a season. If the structure changes under fatigue or burnout, scores at different timepoints are not comparable, and trajectory analysis is invalid.

8. **Measurement invariance across groups.** Configural, metric, and scalar invariance testing across gender (female, male), sport type (team, individual), competitive level (elite, club, youth), and age (under 18, over 18), following Chen (2007) criteria (delta-CFI < 0.01, delta-RMSEA < 0.015). The infrastructure for this testing is built and demonstrated on synthetic multi-group data. Differential item functioning analysis per item identifies any items that operate differently across groups.

### Evidence based on relations to other variables

Four studies anchor ABC scores to external criteria:

9. **Convergent and discriminant validity.** ABC satisfaction subscales should correlate at r > 0.50 with the corresponding BPNSFS satisfaction subscales (Chen et al., 2015), and ABC frustration subscales should correlate at r > 0.40 with ABQ burnout subscales (Raedeke & Smith, 2001). ABC domains should show greater distinctiveness than BPNSFS domains if the relabelling from autonomy/competence/relatedness to Ambition/Belonging/Craft improves domain separation.

10. **Criterion-predictive validity.** The central hypothesis: ABC frustration trajectories predict burnout onset as measured by the ABQ. This requires a prospective longitudinal design with N >= 200 athletes assessed at 5+ timepoints over a season. The simulation's ROC infrastructure derives empirical thresholds from this data. The cascade model predicts that frustration rises before satisfaction drops; the empirical study tests whether this holds in real trajectories.

11. **Incremental validity beyond existing measures.** Does the ABC trajectory analysis predict burnout beyond what a single-timepoint ABQ administration can predict? If the leading indicator hypothesis is correct, the longitudinal ABC signal should add predictive power beyond the concurrent ABQ score.

12. **Coach rating convergence.** Structured coach ratings (3 items per athlete per week: ambition engagement, belonging engagement, craft engagement) serve as an independent criterion that does not share self-report method variance with the ABC. Convergence between ABC self-report and coach observation strengthens the validity argument; divergence identifies blind spots in either channel.

### Evidence based on consequences of testing

Three studies address whether the instrument produces the intended outcomes without unintended harm:

13. **Outcome study.** Does longitudinal ABC monitoring, combined with the three-level distribution system described above, reduce burnout incidence compared to standard care (self-disclosure + coach observation)? This is the ultimate test of the central hypothesis. A cluster-randomized design with teams as the unit of randomization would provide the strongest evidence, though ethical constraints may require a stepped-wedge design.

14. **Iatrogenic effect assessment.** Does labelling an athlete's domain state as "Distressed" worsen their state? Does the monitoring itself create test fatigue that contaminates subsequent responses? Does receiving a type label ("Seeker") produce identity foreclosure that limits development? These are consequences that the simulation cannot predict and that only longitudinal empirical data can reveal.

15. **Equity audit.** Do classification accuracy, false-positive rates, and false-negative rates differ across racial, ethnic, and socioeconomic subgroups? If the instrument is more accurate for some groups than others, the three-level distribution system amplifies existing inequities rather than correcting them. DIF analysis per item across subgroups is necessary but not sufficient; system-level outcome disparities must also be monitored.

### Transparency commitments

This instrument is in its pre-empirical phase. We commit to the following:

- Every threshold will report its derivation method, criterion variable, AUC, sensitivity, specificity, and confidence interval.
- Every classification will report its decision consistency estimate and the measurement tier at which it was derived.
- The Validity Argument document will be updated publicly as each empirical study completes, with negative findings reported alongside positive ones.
- If empirical data shows that any of the three testable parts of the central hypothesis fails (the cascade signal does not exist in real data, the instrument cannot detect it with adequate reliability, or detection does not happen early enough to change outcomes), that finding will be published.

The simulation demonstrates that the infrastructure works. Whether the instrument works is a question only athletes can answer.

## Bibliography

APA, AERA, & NCME. (2014). *Standards for Educational and Psychological Testing.*

Baker, F. B., & Kim, S.-H. (2004). *Item Response Theory: Parameter Estimation Techniques* (2nd ed.). Marcel Dekker.

Bartholomew, K. J., et al. (2011). Self-determination theory and diminished functioning. *Personality and Social Psychology Bulletin, 37*(11), 1459-1473.

Baumel, A., et al. (2019). Objective user engagement with mental health apps. *Journal of Medical Internet Research, 21*(9), e14567.

Chang, C. J., et al. (2020). Mental health issues and psychological factors in athletes. *American Journal of Sports Medicine, 48*(9), 2303-2314.

Chen, B., et al. (2015). Basic psychological need satisfaction, need frustration, and need strength across four cultures. *Motivation and Emotion, 39*, 216-236.

Chen, F. F. (2007). Sensitivity of goodness of fit indexes. *Structural Equation Modeling, 14*(3), 464-504.

Deci, E. L., & Ryan, R. M. (2000). The "what" and "why" of goal pursuits. *Psychological Inquiry, 11*(4), 227-268.

Erickson, J. L., et al. (2023). Validity of the APSQ for mental health screening. *British Journal of Sports Medicine, 57*(21), 1389-1394.

Grugan, M. C., et al. (2024). Factorial validity and measurement invariance of the ABQ. *Psychology of Sport and Exercise, 73*, 102638.

Hu, L., & Bentler, P. M. (1999). Cutoff criteria for fit indexes. *Structural Equation Modeling, 6*(1), 1-55.

Jabir, A. I., et al. (2024). Attrition in conversational agent-delivered mental health interventions. *Journal of Medical Internet Research, 26*(1), e48168.

Jacobson, N. S., & Truax, P. (1991). Clinical significance. *Journal of Consulting and Clinical Psychology, 59*(1), 12-19.

Jones, M., et al. (2022). Mental performance and mental health services in NCAA DI athletic departments. *Journal for Advancing Sport Psychology in Research, 2*(1), 4-18.

Lonsdale, C., & Hodge, K. (2011). Temporal ordering of motivational quality and athlete burnout. *Medicine & Science in Sports & Exercise, 43*(5), 913-921.

Lonsdale, C., et al. (2009). Athlete burnout in elite sport: A self-determination perspective. *Journal of Sports Sciences, 27*(8), 785-795.

Murphy, J., et al. (2023). The BPNSFS probably does not validly measure need frustration. *Motivation and Emotion, 47*, 899-919.

NCAA Student-Athlete Health and Wellness Study, 2022-23. December 2023.

Prior, E., et al. (2024). Attrition in psychological mHealth interventions for young people. *Journal of Technology in Behavioral Science, 9*, 639-651.

Raedeke, T. D., & Smith, A. L. (2001). Development and preliminary validation of an athlete burnout measure. *Journal of Sport & Exercise Psychology, 23*(4), 281-306.

Reise, S. P. (2012). The rediscovery of bifactor measurement models. *Multivariate Behavioral Research, 47*(5), 667-696.

Rhoden, W. C. (2006). *$40 Million Slaves: The Rise, Fall, and Redemption of the Black Athlete.* Crown Publishers.

Samejima, F. (1969). *Estimation of Latent Ability Using a Response Pattern of Graded Scores.* Psychometrika Monograph No. 17.

Vansteenkiste, M., & Ryan, R. M. (2013). On psychological growth and vulnerability. *Journal of Psychotherapy Integration, 23*(3), 263-280.

Whelan, B. M., et al. (2024). Suicide in NCAA athletes: A 20-year analysis. *British Journal of Sports Medicine, 58*(10), 531-537.

Wolanin, A., et al. (2016). Prevalence of clinically elevated depressive symptoms in college athletes. *British Journal of Sports Medicine, 50*(3), 167-171.

Youden, W. J. (1950). Index for rating diagnostic tests. *Cancer, 3*(1), 32-35.
