Produce sections §1 Basic Information and §2 Research Overview of the
paper-read-notes Markdown.

# Inputs

## BIBLIO.json (use as the source of truth for §1 and the topic / argument):
```json
{biblio_json}
```

## Paper text (first 6 pages):

{pdf_text}

# Output

Emit ONLY the following Markdown, fully populated. Do not include the H1.

## 1. Basic Information

| Item | Content |
|------|---------|
| Paper short name | {short_name} |
| Paper full title | {full_title} |
| arXiv ID | {arxiv_id} |
| Release date | {release_date} |
| Conference/Journal | {venue} |
| Paper link (abs) | {abs_link} |
| PDF link | {pdf_link} |
| Code link | {code_link} |
| Project page | {project_link} |

### 1.1 Author Information

(Use the BIBLIO authors list. Columns: Author Name | Affiliation | Homepage |
Role. If a homepage is null, write `—` for that cell. If `verified_url` is
non-null and differs from `homepage`, append it in parentheses.)

### 1.2 Keywords

(Comma-separated 5–8 keywords from BIBLIO.keywords.)

### 1.3 Related Lineage

(Table from BIBLIO.related_lineage: Key | Relation | Brief.)

## 2. Research Overview

### 2.1 Research Topic

(Reuse BIBLIO.research_topic verbatim. Must be a single complete paragraph,
≤ 200 words, never truncated.)

### 2.2 Domain Tags

(Bullet list, one tag per line, from BIBLIO.domain.)

### 2.3 Core Architectures Used

(Bullet list. For each architecture, one sentence describing its role in this
paper. Include both architectures the paper proposes and those it inherits.)

### 2.4 Core Argument

(Reuse BIBLIO.core_argument verbatim. Must be a single complete paragraph,
≤ 400 words, never truncated.)
