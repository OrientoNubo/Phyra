# AI Vocabulary Blacklist

Vocabulary and expressions to avoid in academic writing. Cross-reference this list after drafting to remove or replace banned items. Each entry explains why it should be avoided and suggests alternatives.

## 1. Hyperbolic Adjectives

Overstatement undermines credibility. Replace with precise, evidence-backed language.

| # | Banned Term | Why | Replacement |
|---|------------|-----|-------------|
| 1 | **groundbreaking** | Implies historical significance without evidence | "novel", "new" (with concrete novelty claim) |
| 2 | **revolutionary** | Almost never warranted in incremental science | "a departure from", "fundamentally different from X in that" |
| 3 | **game-changing** | Informal and hyperbolic | "enables X for the first time", "reduces Y by Z%" |
| 4 | **cutting-edge** | Vague; what edge? | "current state-of-the-art", name the specific advance |
| 5 | **paradigm-shifting** | Reserved for Kuhn-level events, not a +2% mAP gain | "introduces a new perspective on", "reframes X as" |
| 6 | **unprecedented** | Rarely true; check the literature | "to the best of our knowledge, the first to" |
| 7 | **remarkable** | Subjective; the reader should decide | state the result and let numbers speak |
| 8 | **extraordinary** | Same as "remarkable" | quantify the improvement instead |
| 9 | **drastically** | Vague magnitude | "by X%" or "by a factor of X" |
| 10 | **pivotal** | Opinion disguised as fact | "important for X because Y" |

## 2. AI-Generated Filler Phrases

Phrases that add no information and signal AI-generated or lazy writing.

| # | Banned Phrase | Why | Replacement |
|---|-------------|-----|-------------|
| 1 | **It is worth noting that** | Filler; if it's worth noting, just note it | State the fact directly |
| 2 | **It should be noted that** | Same as above | State the fact directly |
| 3 | **It is important to mention that** | Same pattern | State it |
| 4 | **In this paper, we** (as opening) | Every paper is "this paper"; wastes the reader's first impression | Lead with the problem or result |
| 5 | **The rest of the paper is organized as follows** | Wastes space in short papers; acceptable in 15+ page papers only | Remove or shorten to one sentence |
| 6 | **In recent years** | Vague temporal reference | Name the year or cite the work that started the trend |
| 7 | **With the rapid development of** | Cliche; says nothing specific | Cite the actual development |
| 8 | **Has attracted increasing attention** | Vague; how much attention? | "N papers have addressed X since YEAR" or cite specific works |
| 9 | **Plays a crucial role in** | Vague; explain the actual mechanism | Describe the dependency: "X requires Y because Z" |
| 10 | **In summary** / **To summarize** (mid-paper) | Redundant if the section is well-written | Remove; let the structure speak |
| 11 | **As shown in Table/Figure X** (as sentence opener) | Passive structure; the result should lead | "Method A outperforms B by X% (Table 3)" |
| 12 | **Comprehensive experiments** | Self-praise; the reader judges comprehensiveness | "We evaluate on N benchmarks across M settings" |
| 13 | **Extensive experiments** | Same as above | Specify what was tested |
| 14 | **State-of-the-art results** (without specifying) | Must name the benchmark and metric | "X.X% mAP on COCO, surpassing [prior] by Y%" |
| 15 | **Various** / **a variety of** | Vague | Name the specific items |

## 3. Unsupported Magnitude Words

These words imply a quantitative claim but provide no data. Only use with supporting evidence.

| # | Banned (without data) | Why | When Acceptable |
|---|----------------------|-----|-----------------|
| 1 | **significantly** | Implies statistical significance (p-value) | Only with a statistical test result |
| 2 | **substantially** | Implies large effect | Only when paired with numbers |
| 3 | **dramatically** | Informal and vague | "by X%", "by a factor of X" |
| 4 | **considerably** | Vague magnitude | Attach specific numbers |
| 5 | **greatly** | Informal | Quantify instead |
| 6 | **vastly** | Extreme claim | Justify with data |
| 7 | **much better** | Informal, vague | "X% higher" or "X points above" |
| 8 | **far superior** | Hyperbolic | "outperforms by X% across N benchmarks" |

## 4. Inappropriate Anthropomorphism

AI models do not think, understand, or want. Use precise mechanistic language.

| # | Banned Phrase | Why | Replacement |
|---|-------------|-----|-------------|
| 1 | **the model understands** | Models compute; they do not understand | "the model encodes", "the model captures" |
| 2 | **the network learns to** | Acceptable in casual context, but imprecise | "the network is trained to", "the loss drives the network to" |
| 3 | **the model thinks** | Never appropriate | "the model predicts", "the model outputs" |
| 4 | **the model knows** | Models store parameters, not knowledge | "the model has been trained on", "the model represents" |
| 5 | **the model sees** | Informal anthropomorphism | "the model receives as input", "the model processes" |
| 6 | **the model struggles with** | Informal | "performance degrades on", "the model fails to generalize to" |
| 7 | **the model is confused by** | Anthropomorphism | "the model misclassifies", "prediction confidence drops for" |
| 8 | **intelligent** (describing a model) | Marketing language | Describe the capability: "achieves X without Y" |

## 5. Redundant Modifiers and Padding

Words that add syllables but not meaning.

| # | Banned | Why | Replacement |
|---|--------|-----|-------------|
| 1 | **novel and innovative** | Redundant pair | Pick one: "novel" |
| 2 | **new and unique** | Redundant pair | "novel" or explain what is unique |
| 3 | **very unique** | "Unique" is already absolute | "unique" alone |
| 4 | **in order to** | Three words where one suffices | "to" |
| 5 | **due to the fact that** | Five words for one | "because" or "since" |
| 6 | **for the purpose of** | Padding | "to" or "for" |
| 7 | **a large body of work** | Vague without citations | Cite specific works, or "extensive prior work [1-5]" |
| 8 | **has shown great promise** | Vague | "has achieved X on Y" |
| 9 | **the proposed method** (repeated) | Acceptable once; repetition is robotic | Use the method's name after introducing it |
| 10 | **utilize** | Pretentious synonym of "use" | "use" |
| 11 | **methodology** (when meaning "method") | "Methodology" is the study of methods | "method" or "approach" |
| 12 | **leverage** (overuse) | Acceptable once per paper; overuse is a cliche signal | Vary: "use", "exploit", "build on" |

## 6. False Precision and Overconfidence

Claims that sound precise but lack substance.

| # | Banned Pattern | Why | Replacement |
|---|---------------|-----|-------------|
| 1 | **proves that** (for empirical results) | Experiments do not prove; they provide evidence | "provides evidence that", "supports the hypothesis that" |
| 2 | **clearly demonstrates** | "Clearly" is the author's opinion | "demonstrates" (let the reader judge clarity) |
| 3 | **obviously** / **clearly** / **undoubtedly** | Rhetorical crutch; if it were obvious, you wouldn't need to say it | Remove the adverb; state the evidence |
| 4 | **always** / **never** (without proof) | Absolute claims require formal proof | "in all tested settings", "in none of the N cases" |
| 5 | **perfectly** | Almost nothing is perfect | "accurately", "with less than X% error" |
| 6 | **optimal** (without proof) | Optimality requires a formal proof | "effective", "efficient", "near-optimal (within X% of the bound)" |
| 7 | **solves the problem** | Most papers alleviate, not solve | "addresses", "mitigates", "reduces the impact of" |
| 8 | **the best** (without qualification) | Best on which metric, dataset, and setting? | "achieves the highest X on Y under Z" |

## Usage Guidelines

- Run this blacklist check **after** completing a draft, not during writing. Over-filtering during writing kills flow.
- Context matters: "significantly" is fine when a p-value follows. "Novel" is fine when novelty is clearly defined.
- The goal is not to ban words absolutely, but to flag patterns that weaken academic writing when used carelessly.
- When in doubt, replace with a quantitative statement or a specific citation.
- Cross-reference with `ai-vocab-whitelist.md` for recommended alternatives.
