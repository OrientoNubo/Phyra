Produce sections §4 Critical Profile, §7 Phyra's Judgment, and §8 Open
Questions of the paper-read-notes Markdown.

# Inputs

## BIBLIO.json:
```json
{biblio_json}
```

## Paper text (full, may be truncated by length budget):

{pdf_text}

# Output

Emit ONLY these three sections in this order, no other content:

## 4. Critical Profile

### 4.1 Highlights

(7–10 specific one-sentence highlights of the paper's claimed strengths.
Include concrete numbers/results when the paper provides them. Cite the
relevant page/figure/table inline when possible.)

### 4.2 Weaknesses

#### 4.2.1 Author-acknowledged

(Limitations the authors openly admit in the paper. Cite the page/section
each one is from. If the paper has no author-acknowledged limitations,
write "the paper does not openly discuss limitations.")

#### 4.2.2 Phyra-inferred

(Structural issues that the paper does NOT openly discuss but a critical
reading reveals. One sentence each, ranked by severity. **Must be specific**:
not "experimental coverage could be wider" but "the only video-diffusion
comparison uses validation loss; no FVD or human-eval, so quality regressions
are invisible to the reported metric." If you cannot ground a Phyra-inferred
weakness in a specific section/result, omit it.)

### 4.3 Phyra's Judgment (summary)

(2–4 sentences. Phyra's overall stance: what is genuinely new, what is
engineering-only, what core question remains unresolved. The detailed
per-claim assessment goes in §7.)

## 7. Phyra's Judgment

### 7.1 Claimed vs. Supported Contributions

(For each contribution the authors claim (typically 3–5): state whether the
experiments support it, partially support it, or whether it is overclaimed.
Cite the supporting figure/table.)

### 7.2 Fundamental Limitations of the Method

(Structural problems the method cannot overcome under its current
formulation. NOT future work. One short paragraph each, 2–4 paragraphs
total.)

### 7.3 Citations Worth Tracking

(3–5 references the reader should chase. For each: citation key, why it is
worth reading next.)

## 8. Open Questions and Improvement Ideas

### 8.1 Outstanding Questions

(Markdown checklist `- [ ] question`. 4–7 questions. Specific, not generic.)

### 8.2 Improvement Directions

(Ranked by feasibility. For each: the proposed change and the logical basis
for why it should help.)
