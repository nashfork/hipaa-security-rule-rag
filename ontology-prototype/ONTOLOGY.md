# Ontology-Grounded Retrieval: Addressing Synonymy Blindness in Regulatory RAG

## Status

**This is a validated local prototype, not a deployed feature.** All work described here was developed and tested against a local copy of the project's ChromaDB collection, kept separate from the live Streamlit app. The deployed app's retrieval pipeline is unchanged. Promoting this to production is a deliberate next step, not a prerequisite for this write-up.

## The Problem

Vector similarity search retrieves based on embedding proximity, which creates two failure modes in a regulatory corpus:

- **Synonymy blindness** — a query using one term (e.g., "malware") may not retrieve chunks using a different term for the same concept (e.g., "malicious software"), if the embedding model doesn't place them close enough in vector space.
- **False semantic proximity** — chunks can rank highly for sounding similar without being substantively relevant.

Regulatory text is a particularly good test case for this: the same underlying concept is often expressed differently across a proposed rule (NPRM) and the current rule, or between formal defined terms and the informal language people actually use to ask questions.

## Approach

### Scope

The ontology is deliberately scoped to the HIPAA Security Rule (45 CFR §164.302–318) only. The corpus also contains adjacent HIPAA content (e.g., Part 162 transaction/code-set standards) that is out of scope by design — those chunks correctly receive no concept tags rather than being forced into an unrelated concept map. Expanding scope to other HIPAA domains would require a second, distinct concept map rather than extending this one, since the vocabularies don't meaningfully relate to each other.

### Concept extraction

Concepts were extracted via LLM-assisted bootstrapping, one source document at a time, with a human review step:
- Each document was processed independently (not merged) so synonym candidates could be evaluated against how each source actually uses its own terminology.
- Candidate concepts were flagged by confidence (high/medium/low), with low-confidence flags concentrated on terms that looked like synonyms but weren't confirmed as such.
- Formal definitions (45 CFR §164.304, and the NPRM's proposed definitions) were used to resolve ambiguous cases — e.g., confirming "security incident" is a formal umbrella term while "cyberattack" is informal preamble language, not a defined synonym.

### Structure

Each concept is a flat JSON entry (not a graph) with:
- `candidate_label`, `definition`, `source_terms` — the concept itself and how it's expressed in the source text
- `status` — `current` (in §164.304 today) or `proposed` (introduced in the NPRM), so the ontology doesn't conflate current obligations with proposed changes
- `relates_to` / `relation_type` — an optional single relationship (e.g., `technology asset` *narrows* `information system`) for the handful of cases where a flat synonym list wasn't sufficient
- `tagging_terms` — an optional override list, used to exclude overly broad terms (see below) from automated tagging while keeping them in the ontology for reference

A graph structure (e.g., NetworkX) was considered and deliberately deferred — it would only pay for its complexity once multiple relationship types and multi-hop traversal are actually needed, which this scoped ontology doesn't yet require.

### Noise filtering via frequency analysis

Running the tagging function against all 240 chunks in the corpus surfaced six concepts (e.g., "access," "ePHI," "confidentiality") that matched 35–55% of all chunks — too common to provide any discriminating signal for retrieval boosting. These were kept as full ontology entries but excluded from automated chunk tagging, based on a natural break point in the frequency distribution (a 14-point gap between the 6th and 7th most frequent concepts). The remaining 14 concepts, with tagging frequencies between 8–21%, form the effective discriminating set used for retrieval.

## Implementation

- `tag_chunk(text, ontology)` — matches chunk or query text against concept source terms using case-insensitive, word-boundary regex matching. Used identically at indexing time (tagging chunks) and query time (tagging the user's question), so concept IDs mean the same thing on both sides of the comparison.
- Chunk-level `concept_ids` are stored as a comma-joined string in Chroma metadata (a workaround for Chroma's lack of native list-type metadata).
- `rerank_with_ontology(query, results, ontology)` — tags the incoming query, expands it via any `relates_to` relationships, and applies a flat similarity-score boost to retrieved candidates whose `concept_ids` overlap the expanded query concepts.
- The retrieval pool size was widened (from the app's default top-5 to a top-20 candidate pool) specifically so re-ranking has room to promote relevant-but-lower-similarity chunks that a tight top-5 pull would exclude before boosting ever had a chance to act.

## Evidence

Three test queries were run against the same 20-chunk candidate pool, comparing plain cosine-similarity ranking against the ontology-boosted ranking:

| Query | Result |
|---|---|
| "What counts as a security incident?" | 3 of 5 results changed; a `current_rule` chunk not present in the unboosted top 5 was correctly promoted via concept overlap. |
| "How should we handle malware?" | Top 3 results were unchanged (cosine similarity already ranked them correctly) — a more targeted, marginal correction at positions 4–5, promoting a chunk that the final generated answer directly cited. |
| "What are the requirements for malicious software?" | Confirmed bidirectional synonym resolution — both "malware" and "malicious software" tag to the same concept. The same `current_rule` chunk missed by cosine similarity in the first test was independently recovered again here. |

The recurring recovery of the same `current_rule` chunk across two different concepts and two different queries is the strongest evidence in this set: a chunk written in older regulatory language was consistently missed by embedding similarity alone, and consistently recovered by concept-tag overlap.

## Limitations

- Tagging relies on literal term matching (with manually curated variants for plurals/verb forms/synonyms) rather than semantic matching — it will not catch a paraphrase that isn't already represented in the ontology's `source_terms`.
- The flat boost applies a fixed score increment regardless of how many concepts overlap or how they're related; proportional or relation-weighted boosting was considered and deliberately deferred until this simpler version is proven insufficient.
- The ontology has not yet been validated against the full text of every source document — extraction so far covers roughly 19 concepts from the current definitions section and preamble discussion, not an exhaustive pass.

## Next steps

- Extract and tag additional concepts from the remaining, not-yet-processed sections of both source documents.
- Apply the validated write-back process to the live app's production Chroma collection, and wire `rerank_with_ontology` into the deployed retrieval path.
- Evaluate whether proportional or relation-weighted boosting produces measurably better results than the current flat-boost approach.