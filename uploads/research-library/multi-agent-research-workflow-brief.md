# Research Brief: Multi-Agent Research Workflows

## Document Metadata

- Topic: Multi-agent orchestration for research and decision support
- Evidence type: Research brief and workflow design notes
- Prepared for: AI Council
- Source links:
  - https://langchain-ai.github.io/langgraph/
  - https://python.langchain.com/docs/concepts/architecture/

## Executive Summary

A multi-agent research system delegates different analytical responsibilities to specialist agents, collects their outputs, reviews the evidence, and synthesizes a final report. The orchestration layer should make state transitions explicit and should preserve the original question, evidence, intermediate outputs, errors, and source references.

A reviewer and a synthesizer serve different purposes. The reviewer checks for contradictions, unsupported claims, missing evidence, and assumptions. The synthesizer turns the reviewed material into a structured answer while retaining source attribution and uncertainty.

## Recommended Workflow

```text
Validate request
  -> Discover external sources when enabled
  -> Retrieve private documents when enabled
  -> Build shared research context
  -> Run selected specialist agents
  -> Review agent outputs
  -> Synthesize final report
  -> Persist report and execution records
  -> Emit completion event
```

## State Requirements

A typed workflow state should include:

- session id
- authenticated user id
- question and title
- category and priority
- research mode
- selected agents
- private retrieval context
- external research sources
- agent outputs and statuses
- reviewer output
- final report
- errors and event history
- timestamps and metadata

## Reliability Principles

- Each agent should have a timeout and captured exception path.
- A failed agent should produce a visible failed status rather than fake output.
- Workflow progress should come from real state transitions.
- Background tasks must be tracked and their exceptions persisted.
- Cancellation should prevent future nodes from starting where practical.
- Retry should increment a retry count and execute the actual failed work again.
- The final report should distinguish evidence, inference, and assumption.

## Review and Synthesis

The reviewer should identify:

- contradictions between agents
- unsupported or weakly supported claims
- duplicate findings
- missing evidence
- source conflicts
- hidden assumptions

The synthesizer should produce an executive summary, methodology, key findings, domain analyses, risks, limitations, practical options, final synthesis, and sources.

## Application Relevance

AI Council already contains specialist, reviewer, synthesizer, and LangGraph modules. The missing integration work is to connect the research start endpoint to a tracked background workflow, persist each execution in SQLite, publish authenticated SSE events, and save the final report.
