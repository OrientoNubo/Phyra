Produce section §5 Methodology Deep Dive of the paper-read-notes Markdown.

You have a multimodal attachment: the main pipeline figure (page {fig_page},
{fig_label}). Use it to ground the §5.2 tensor-shape pipeline diagram.

# Inputs

## BIBLIO.json (for figure caption):
```json
{biblio_json}
```

## Paper text (method section pages):

{pdf_text}

# Output

Emit ONLY this section:

## 5. Methodology Deep Dive

### 5.1 Method Overview

(2–3 paragraphs in technical voice. Detailed enough that a reader who skipped
the §3.4 narrative can still follow.)

### 5.2 Pipeline Diagram with Tensor Shapes

Render the full forward path as a Markdown text diagram inside a fenced code
block. Annotate every arrow with the tensor shape using the convention
`[B, ..., d]`. If a shape cannot be inferred from the paper, mark the missing
dimension as `?` and note it under the relevant module's "Implementation
Details" in §5.3.

```
Input: ...
   ├→ ...
   └→ ...
```

### 5.3 Per-Module Breakdown

For every major module (typically 3–7), repeat the block:

#### 5.3.N {{Module Name}}

**Function:** [One sentence.]

**Input:**
- Name: [variable name]
- Shape: [tensor shape]
- Source: [from which module or data]

**Output:**
- Name: [variable name]
- Shape: [tensor shape]
- Consumer: [next module]

**Processing:**

[Step-by-step transform, including dimension changes and key operations.
Cite the equation number if the paper has one.]

**Key Formulas:**

$$
[LaTeX formula]
$$

**Implementation Details:**

[Activation, normalization, initialization, learning rate, etc. — only what
the paper actually discloses.]
