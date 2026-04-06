# AI Vocabulary Whitelist

Curated from best-paper-awarded works at CVPR, ICCV, ECCV, NeurIPS, AAAI, ICML, ACL, EMNLP, and related top venues. Intended as a usage reference when writing or revising academic manuscripts.

Each entry follows the format: **term/phrase** -- usage note.

---

## 1. Contribution Verbs

Verbs for claiming what the paper does. Choose precision over novelty; the verb should match the actual nature of the contribution.

| # | Term | Usage Note |
|---|------|-----------|
| 1 | **propose** | The default for a new method or framework. Safe and universally accepted. |
| 2 | **introduce** | Slightly softer than "propose"; good for new concepts, datasets, or benchmarks. |
| 3 | **present** | Neutral; suits system descriptions or empirical studies that are not purely methodological. |
| 4 | **demonstrate** | Use when the contribution is primarily empirical evidence, not a new algorithm. Emphasizes "showing/proving." |
| 5 | **establish** | For foundational results: a new theoretical bound, a new benchmark protocol. Carries weight; requires strong support. |
| 6 | **formulate** | When you cast a problem into a formal mathematical framework. |
| 7 | **derive** | For proofs, closed-form solutions, or analytical results. |
| 8 | **devise** | Slightly more inventive tone than "propose"; fits clever algorithmic designs. |
| 9 | **achieve** | For a concrete result (e.g., state-of-the-art accuracy). Always pair with data. |
| 10 | **attain** | Synonym for "achieve"; useful to avoid repetition. |
| 11 | **enable** | When your method makes something previously infeasible now possible. |
| 12 | **alleviate** | Partially reduce a known problem. Honest hedging -- does not claim full resolution. |
| 13 | **mitigate** | Close synonym of "alleviate"; common in robustness/fairness contexts. |
| 14 | **unify** | When a single framework subsumes multiple prior approaches. |
| 15 | **bridge** | Connecting two previously separate lines of work or modalities. |
| 16 | **reveal** | For an analysis contribution: your experiments uncover a previously unknown phenomenon. |
| 17 | **identify** | Pinpointing a specific failure mode, bottleneck, or overlooked factor. |
| 18 | **extend** | Building on a prior method with non-trivial additions. |
| 19 | **generalize** | Broadening a method to more settings (e.g., from 2D to 3D, from supervised to unsupervised). |
| 20 | **instantiate** | Concretely realizing an abstract idea as a specific model or module. |
| 21 | **validate** | Confirming a hypothesis via experiments. Cautious tone. |
| 22 | **advocate** | Arguing for a design choice or perspective; common in position/analysis papers. |
| 23 | **shed light on** | Provide new understanding of a phenomenon. Semi-formal. |
| 24 | **pinpoint** | Precisely locate or identify (a cause, a failure mode). |
| 25 | **streamline** | Simplify a pipeline or procedure while preserving effectiveness. |

## 2. Comparison and Contrast Vocabulary

Use when positioning your method against baselines or prior art. Always attach quantitative evidence.

| # | Term | Usage Note |
|---|------|-----------|
| 1 | **outperform** | The standard verb for beating a baseline. Requires specific numbers. |
| 2 | **surpass** | Slightly more emphatic; reserve for clear, large-margin improvements. |
| 3 | **exceed** | Works well with thresholds (e.g., "exceeds 90% for the first time"). |
| 4 | **rival** | Approaches the performance of a much more expensive/complex method. |
| 5 | **fall short of** | Honest acknowledgment of a gap. Reviewers appreciate candour. |
| 6 | **lag behind** | Similar to "fall short of"; slightly more informal but acceptable. |
| 7 | **on par with** | Comparable performance, often with an orthogonal advantage (speed, memory). |
| 8 | **comparable to** | Neutral equivalence. Less idiomatic than "on par with" but perfectly clear. |
| 9 | **in contrast to** | Highlights a methodological or empirical difference. |
| 10 | **as opposed to** | Presents an alternative design choice. |
| 11 | **at the expense of** | Improvement in one metric comes with degradation in another. Implies a trade-off. |
| 12 | **with negligible overhead** | The added cost is trivially small. Only claim if profiling supports it. |
| 13 | **without bells and whistles** | Plain, unadorned baseline without tricks. Common in detection/segmentation papers. |
| 14 | **narrows the gap** | Reduces the distance to an upper bound or oracle. |
| 15 | **sets a new state of the art** | Use sparingly; must be backed by comprehensive benchmarks. |
| 16 | **trades off A for B** | Explicit acknowledgment of a design trade-off. |
| 17 | **degrades gracefully** | Performance declines slowly under adverse conditions. |
| 18 | **scales favorably** | Efficiency grows well with input size, model size, or data size. |
| 19 | **remains competitive** | Does not win, but stays close. Useful for ablation context. |
| 20 | **closes the performance gap** | Stronger than "narrows"; implies near-elimination of the gap. |
| 21 | **yields diminishing returns** | Further effort produces smaller gains. Useful in scaling analysis. |
| 22 | **is orthogonal to and compatible with** | Can be combined with another method for additive gains. |
| 23 | **under the same computational budget** | Fair comparison controlling for resources. |
| 24 | **with no additional training cost** | The improvement is free at training time. |
| 25 | **for a fraction of the cost** | Much cheaper while achieving comparable results. |

## 3. Hedging Expressions

Academic writing requires calibrated uncertainty. Over-hedging sounds weak; under-hedging invites reviewer pushback.

| # | Term | Usage Note |
|---|------|-----------|
| 1 | **arguably** | Signals a claim that is reasonable but debatable. |
| 2 | **presumably** | When the ground-truth cause is not directly observable. |
| 3 | **to some extent** | Partial effect; avoids an absolute claim. |
| 4 | **under certain conditions** | Limits the scope of a claim. Always specify which conditions. |
| 5 | **with the caveat that** | Flags an important exception or limitation. |
| 6 | **it remains to be seen whether** | For future work implications; honest about current limitations. |
| 7 | **we conjecture that** | Stronger than speculation, weaker than a proven claim. |
| 8 | **empirical evidence suggests** | Lets data speak without over-claiming causality. |
| 9 | **we hypothesize that** | Sets up a testable statement. |
| 10 | **one plausible explanation is** | Offers an interpretation without asserting it as fact. |
| 11 | **this observation is consistent with** | Links a result to a known phenomenon without claiming causation. |
| 12 | **to the best of our knowledge** | Use once, typically for novelty claims. Overuse weakens credibility. |
| 13 | **a potential limitation is** | Preempts reviewer criticism with honest disclosure. |
| 14 | **we attribute this to** | Proposes a cause for an observed effect. |
| 15 | **while promising, these results** | Balances optimism with realism. |
| 16 | **it is worth noting that** | Draws attention to a non-obvious point. Semi-formal. |
| 17 | **in principle** | Theoretically true, but practical caveats may apply. |
| 18 | **as a first approximation** | Acknowledges simplification in modeling. |
| 19 | **this does not necessarily imply** | Prevents readers from drawing an unwarranted conclusion. |
| 20 | **the extent to which** | Frames an open quantitative question. |
| 21 | **we leave a thorough investigation to future work** | Scopes out what is not addressed. Honest boundary-setting. |
| 22 | **a more nuanced picture emerges when** | Invites deeper analysis beyond headline numbers. |
| 23 | **strictly speaking** | Tightens a loose claim to its precise scope. |
| 24 | **in the absence of ground truth** | Acknowledges evaluation limitation. |
| 25 | **we do not claim that** | Preemptive scope limitation; prevents misinterpretation. |

## 4. Transition and Connection Phrases

Phrases that link ideas, motivate choices, and guide the reader through the narrative.

| # | Term | Usage Note |
|---|------|-----------|
| 1 | **building upon** | Extends prior work. Signals respectful continuation. |
| 2 | **motivated by** | Explains why a design choice was made. |
| 3 | **in light of** | Given a recent finding or observation. |
| 4 | **to this end** | Transitions from a stated goal to the proposed approach. |
| 5 | **towards this goal** | Variant of "to this end"; slightly softer. |
| 6 | **along this line** | Continues a thread of reasoning from prior work. |
| 7 | **orthogonal to** | Independent and complementary; can be combined. |
| 8 | **in a complementary fashion** | Two methods address different aspects and combine well. |
| 9 | **from a different perspective** | Introduces an alternative viewpoint or formulation. |
| 10 | **a natural question arises** | Transitions to the next research question in the narrative. |
| 11 | **this naturally leads to** | One result motivates the next step. |
| 12 | **in a similar vein** | Draws a parallel with a related approach or finding. |
| 13 | **it is therefore natural to** | Justifies a design decision as the logical next step. |
| 14 | **with this in mind** | Keeps a stated constraint or observation active while moving forward. |
| 15 | **armed with this insight** | Slightly informal; transitions from an analysis finding to a design. |
| 16 | **concretely** | Moves from abstract description to specific implementation. |
| 17 | **more precisely** | Refines a loose statement into a formal one. |
| 18 | **without loss of generality** | Simplification that does not restrict the result. Mathematical register. |
| 19 | **unless otherwise stated** | Sets a default assumption for the remainder of the text. |
| 20 | **in what follows** | Previews upcoming content. Formal. |
| 21 | **taken together** | Synthesizes multiple observations into a joint conclusion. |
| 22 | **viewed through this lens** | Reinterprets a situation using the newly introduced framework. |
| 23 | **at a high level** | Gives the intuition before the formal details. |
| 24 | **the key insight is that** | Highlights the core intellectual contribution. Use once per paper. |
| 25 | **put differently** | Restates the same idea for clarity. |

## 5. Problem Framing

Vocabulary for the Introduction and Related Work sections: describing the landscape and positioning the gap.

| # | Term | Usage Note |
|---|------|-----------|
| 1 | **remains an open challenge** | The problem is unsolved. Strong motivator. |
| 2 | **is far from solved** | Emphatic variant; implies existing methods are insufficient. |
| 3 | **has received limited attention** | Under-explored area. Verify with a literature search before claiming. |
| 4 | **suffers from** | A known, documented drawback (e.g., mode collapse, catastrophic forgetting). |
| 5 | **is plagued by** | Stronger than "suffers from"; implies persistent, widespread failure. |
| 6 | **poses a significant barrier** | A specific obstacle blocking progress. |
| 7 | **hinders** | Prevents or slows down a desirable outcome. |
| 8 | **prohibits** | Makes something effectively impossible (e.g., prohibitive computational cost). |
| 9 | **a long-standing problem** | Emphasizes the problem's history and difficulty. |
| 10 | **a fundamental limitation** | Core, not superficial; changing it requires rethinking the approach. |
| 11 | **an inherent trade-off between** | Two desirable properties that are in tension by design. |
| 12 | **is non-trivial** | The task is harder than it first appears. Avoid overuse. |
| 13 | **calls for** | The situation demands a new approach. |
| 14 | **necessitates** | A stronger version of "calls for"; a hard requirement. |
| 15 | **the gap between ... and ... remains large** | Quantifiable distance between current and desired performance. |
| 16 | **is often overlooked** | A factor that matters but is typically ignored. |
| 17 | **existing approaches tend to** | Generalizes a common pattern across prior methods. |
| 18 | **at the cost of** | Existing solutions work but sacrifice something important. |
| 19 | **the bottleneck lies in** | Pinpoints where the main difficulty or inefficiency resides. |
| 20 | **this discrepancy stems from** | Explains the root cause of a gap or inconsistency. |
| 21 | **remains under-explored** | Variant of "has received limited attention"; slightly softer. |
| 22 | **scales poorly to** | Current solutions break when the problem grows. |
| 23 | **lacks theoretical grounding** | The method works empirically but has no formal justification. |
| 24 | **introduces undesirable artifacts** | A side effect of existing methods. Common in generation/synthesis. |
| 25 | **is sensitive to** | Performance varies with a specific hyperparameter or condition. |

## 6. Method Description

Verbs and phrases for the Methodology section. Precision matters: each verb implies a different kind of operation.

| # | Term | Usage Note |
|---|------|-----------|
| 1 | **leverage** | Use an existing resource or property to advantage. |
| 2 | **exploit** | Neutral in academic English; means "make full use of." No negative connotation here. |
| 3 | **capitalize on** | Similar to "exploit"; slightly more emphatic. |
| 4 | **incorporate** | Add a component into an existing framework. |
| 5 | **integrate** | Combine components into a cohesive whole. Emphasizes unity. |
| 6 | **disentangle** | Separate entangled factors (e.g., content and style). Core term in representation learning. |
| 7 | **factorize** | Decompose into multiplicative components (e.g., matrix factorization). |
| 8 | **decompose** | Break into additive or structural sub-parts. |
| 9 | **aggregate** | Combine multiple signals into one (e.g., feature aggregation). |
| 10 | **distill** | Transfer knowledge from a larger model to a smaller one; or extract the essence. |
| 11 | **parameterize** | Express a quantity as a function of learnable parameters. |
| 12 | **condition on** | Make a computation dependent on an auxiliary input (e.g., class label). |
| 13 | **regularize** | Add a constraint or penalty to prevent overfitting or enforce structure. |
| 14 | **augment** | Expand training data or features via transformations. |
| 15 | **encode / decode** | Map to and from a latent space. Foundational in generative models. |
| 16 | **propagate** | Pass information through layers, graphs, or time steps. |
| 17 | **attend to** | Apply attention mechanism to focus on relevant parts. |
| 18 | **project** | Map from one space to another (usually lower-dimensional). |
| 19 | **align** | Bring two representations or distributions into correspondence. |
| 20 | **fuse** | Combine multi-modal or multi-scale features. |
| 21 | **modulate** | Adjust feature responses based on a conditioning signal (e.g., FiLM, AdaIN). |
| 22 | **decouple** | Separate two coupled processes so they can be optimized independently. |
| 23 | **instantiate as** | Realize an abstract formulation as a concrete architecture or loss. |
| 24 | **cast ... as** | Reformulate one problem type as another (e.g., cast detection as set prediction). |
| 25 | **amortize** | Spread a cost across many instances (e.g., amortized inference). |

## 7. Result Reporting

Vocabulary for the Experiments section. Accuracy of language is critical: do not use "significantly" without a statistical test.

| # | Term | Usage Note |
|---|------|-----------|
| 1 | **yield** | Neutral; a method produces a certain result. |
| 2 | **obtain** | We get a specific number. Pair with the actual value. |
| 3 | **achieve** | Slightly more emphatic than "obtain"; suits headline results. |
| 4 | **lead to** | A design choice causes an observed improvement. |
| 5 | **result in** | Close synonym of "lead to." |
| 6 | **translate to** | An improvement in one metric corresponds to a real-world benefit. |
| 7 | **amount to** | Quantifies the magnitude of an effect (e.g., "amounts to a 3% gain"). |
| 8 | **correspond to** | Links two related quantities. |
| 9 | **consistently** | The effect holds across datasets, seeds, or settings. Requires multi-run support. |
| 10 | **marginally** | A small, possibly not meaningful improvement. Honest when the gap is thin. |
| 11 | **substantially** | A large, meaningful improvement. Must be paired with concrete data. |
| 12 | **notably** | Draws attention to a specific, interesting result. |
| 13 | **interestingly** | Flags a surprising or counter-intuitive finding. Use sparingly. |
| 14 | **as expected** | The result aligns with the stated hypothesis. |
| 15 | **contrary to expectations** | The result contradicts what was predicted; analysis should follow. |
| 16 | **across all benchmarks** | Emphasizes breadth of evaluation. Only use if literally true. |
| 17 | **with diminishing returns** | Further scaling/tuning helps less and less. |
| 18 | **the gain is most pronounced when** | Identifies the condition under which the method shines. |
| 19 | **accounts for** | Explains how much of the overall improvement a component contributes (ablation). |
| 20 | **we observe a clear trend** | Pattern is visually or numerically obvious in the results. |
| 21 | **statistically significant (p < ...)** | Only use with an actual test and reported p-value. |
| 22 | **within the margin of error** | Differences are not meaningful given variance. |
| 23 | **we report the mean and standard deviation over N runs** | Gold standard for stochastic experiments. |
| 24 | **the improvement is consistent across** | Robustness claim; enumerate the axes (datasets, architectures, seeds). |
| 25 | **to isolate the effect of** | Ablation language: changing one factor while fixing others. |

## Usage Guidelines

- **Pair strong claims with evidence.** Verbs like "surpass" or "establish" carry weight; unsubstantiated use erodes credibility.
- **Vary vocabulary across sections.** Repeating "leverage" five times in one page signals autopilot writing.
- **Match register to venue.** NeurIPS and ICML tolerate slightly more formal/mathematical language; CVPR and ECCV accept semi-informal phrasing like "without bells and whistles."
- **Hedging is not weakness.** Calibrated uncertainty (Category 3) signals scientific maturity, not lack of confidence.
- **Check the blacklist.** After drafting, cross-reference `ai-vocab-blacklist.md` to remove banned vocabulary before finalizing.
- **"Significant" requires a test.** Do not write "significant improvement" without a statistical significance test and p-value. Use "substantial" or "considerable" for large but untested gains.
- **Active voice first.** "We propose X" is stronger than "X is proposed." Reserve passive for cases where the agent is genuinely irrelevant.
- **One strong verb per claim.** "We propose and introduce a novel framework" is redundant. Pick one.

## Quick Reference: Common Pitfalls

| Instead of | Consider | Reason |
|-----------|---------|--------|
| "We significantly outperform" | "We outperform ... by X%" | "significantly" needs a stat test |
| "A novel and innovative approach" | "We propose an approach that ..." | Redundant adjectives; let the method speak |
| "Leverages ... to exploit ..." | Pick one: "leverages" or "exploits" | Stacking near-synonyms adds no information |
| "It is interesting to note that" | "Notably, ..." or just state the fact | Filler; get to the point |
| "Due to the fact that" | "Because" or "since" | Unnecessary padding |
| "In order to" | "To" | Shorter, same meaning |
| "A large body of work" | "Extensive prior work" or cite specifics | Vague without citations |
| "Has shown great promise" | "Has achieved X on Y" | Vague; quantify instead |
