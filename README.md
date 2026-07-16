<<<<<<< HEAD
---
title: Hipaa Security Rule Rag
emoji: 🦀
colorFrom: gray
colorTo: pink
sdk: gradio
sdk_version: 6.20.0
python_version: '3.12'
app_file: app.py
pinned: false
license: mit
---

# HIPAA Security Rule Changes RAG Assistant

This RAG application enables healthcare IT professionals to query the 2025 HIPAA Security Rule NPRM against the existing rule in plain English, receiving cited answers that identify what is changing and how to implement those changes.

---

## Background

The proposed updates to the HIPAA Security Rule represent the most significant changes to healthcare cybersecurity requirements since 2013. For community hospitals and smaller health systems who are operating under the existing rule, adapting to a new regulatory environment can be a costly, time-consuming process with the potential for significant disruption to operations. These teams need to not only carefully read nearly 300 pages of dense legal text, but also translate that regulatory language into an action plan that keeps the organization compliant under new requirements without impacting the delivery of care.

---

## Features

This tool allows healthcare IT professionals to ask plain-English questions about the proposed HIPAA Security Rule changes and receive grounded, cited answers drawn directly from the regulatory text.

**What you can do:**
- Query the proposed NPRM and current Security Rule simultaneously
- Identify specific differences between current requirements and proposed changes
- Receive cited answers tied to specific sections of the regulatory text
- Where applicable, get actionable steps to implement proposed changes

**Example queries:**
- *"What are the proposed changes to multi-factor authentication requirements, and how do they differ from the current rule?"*
- *"Does the NPRM introduce new requirements for incident response planning?"*
- *"What does the proposed rule say about encryption of data at rest?"*

Questions outside the scope of the two source documents will be declined.

---

## Architecture

| Component | Technology | Rationale |
|---|---|---|
| Development Environment | Google Colab | Accessible; no local setup required |
| PDF Parsing | PyMuPDF (fitz) | Reliable text extraction from dense regulatory PDFs |
| Embedding Model | all-MiniLM-L6-v2 (sentence-transformers) | Lightweight; well-suited for semantic similarity on technical text |
| Vector Store | ChromaDB | Simple to implement; persistent across sessions via Google Drive |
| Generation Model | Gemini 2.5 Flash | Strong instruction-following; accessible via Google AI Studio API |
| Persistence | Google Drive | Eliminates re-ingestion on every session |

**Pipeline:**

```
[PDFs] --> [Parse: PyMuPDF] --> [Embed: all-MiniLM-L6-v2] --> [Store: ChromaDB] --> [Retrieve: ChromaDB] --> [Generate: Gemini 2.5 Flash] --> [Cited Response]
```

---

## Design Decisions

**Google Colab:** Colab provides a cloud-based development environment that requires minimal setup while providing the ease of incremental development through cells. Developing in the cloud also allows for direct cloud-to-cloud API calls, reducing latency and avoiding routing sensitive information through a local device. Integration with Google Drive for ChromaDB persistence was an additional factor.

**Frameworkless Design:** This application is built with pure Python and direct API calls instead of an abstraction framework like LangChain. This was a deliberate choice to maintain full visibility into the pipeline and understand what is happening at each step, rather than relying on a framework.

**Gemini over OpenAI:** While OpenAI's API dominates the market, Gemini presents a more practical path from development to HIPAA-compliant deployment. Google AI Studio's free tier provides sufficient usage for development, and transitioning from AI Studio to Gemini Enterprise Agent Platform — for BAA coverage — is more straightforward than navigating OpenAI's enterprise tier.

**Free-Tier API:** Google AI Studio's free tier provides more than enough usage for development, meaning a lower barrier to entry for replication and experimentation.

**Page-Level Chunking:** Chunking at the page level is a pragmatic starting point for dense legal documents, where smaller chunks may not provide enough context to answer queries meaningfully. It is also quick to implement without domain-specific parsing logic. More granular chunking strategies are a logical next step before deployment.

---

## Getting Started

**Prerequisites:**
- Google account with access to Google Colab, Google AI Studio, and Google Drive
- API key from Google AI Studio

**Steps:**

1. Add your Google AI Studio API key to Colab secrets.
2. Install requirements (`requirements.txt`) and import packages.
3. Mount Google Drive and initialize the ChromaDB client.
4. Import PDFs from URLs *(first time only)*.
5. Run the ingestion function to parse PDFs, embed chunks, and store in ChromaDB *(first time only — subsequent sessions will load the persistent vector store)*.
6. Run the `retrieve_chunks` and `generate_response` function definition cells.
7. Update the query variable with your question and run the query cell to get a cited response.

```python
query = "What are the two most disruptive changes to the HIPAA rule?"
results = retrieve_chunks(query)
answer = generate_response(query, results)
print(answer)
```

> **Note:** Function definition cells only need to be run once per session. Re-run the query cell with a new question to get additional responses.

---

## Limitations

**PHI and Production Use:** This application routes queries through the Google AI Studio API, which is not covered by a BAA in its free development tier, meaning it is not suitable for use with real PHI in any form. Any production deployment would need to migrate to a platform that provides BAA coverage and HIPAA-eligible infrastructure.

**Scope:** The application only has two source documents in its vector store — the HIPAA Security Rule NPRM (90 FR 800) and the current Security Rule (45 CFR Part 164). Questions outside that scope are declined. Expanding the corpus to include related guidance documents, HHS FAQs, or OCR enforcement decisions would meaningfully improve coverage.

**Chunking at Scale:** Page-level chunking is effective for this corpus but may degrade in precision as the document set grows. A page from a dense regulatory document can contain multiple distinct topics, meaning a retrieved chunk may include more context than is relevant to a specific query.

**No Conversation History:** Each query is processed independently. The application has no memory of prior questions within a session, which limits its usefulness for multi-turn investigative queries where a user is building on previous answers.

**Rate Limits:** The free tier of the Google AI Studio API is subject to rate limits that may affect responsiveness under concurrent usage.

---

## Future Work

The following enhancements are planned or under consideration for future development:

- Conversation history to support multi-turn queries
- Reranking of retrieved chunks for improved retrieval precision
- Expanded corpus to include HHS guidance documents, OCR FAQs, and enforcement decisions
- More granular chunking strategy to improve retrieval specificity
- Local model deployment to enable PHI-safe production use
- More refined front-end interface beyond the initial Streamlit implementation

---

## License

This project is licensed under the MIT License. See `LICENSE` for details.

## Disclaimer

This application is a research and portfolio project and is not intended for production use. It is not a substitute for legal or compliance advice. Organizations should consult qualified legal counsel and compliance professionals before making decisions based on any output generated by this tool. This application is not designed or approved for use with real protected health information (PHI) in any form.
=======

