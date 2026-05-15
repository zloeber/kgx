1. Project Summary

The project is a portable, composable knowledge packaging system for human users and AI agents, intended to represent operational knowledge about enterprise IT workloads in a structured, reusable way.

The system is not primarily a traditional knowledge graph, RAG platform, or agent harness. Instead, it is a knowledge package manager that creates reusable “knowledge packs” for vendors, services, and workloads. These packs can be mounted dynamically by agents or human-facing systems to provide contextual understanding and access to relevant capabilities.

The core concept is:

* Create vendor base packs once (e.g., for Amazon Web Services, Databricks, GitLab)
* Reuse them across many internal workloads
* Overlay organization-specific business knowledge and relationships
* Optionally bundle associated MCP servers, tool definitions, and skill references
* Expose the system via a single binary/CLI and optionally an MCP server

The envisioned end-state is:

A system where an autonomous engineering agent can inspect a repository, infer the technology stack, automatically load the correct vendor packs, and gain both:

1. domain understanding
2. actionable tool access

Example:

A repo for a data pipeline may trigger loading:

* AWS pack
* GitLab pack
* Databricks pack
* Internal data-platform overlay pack

This provides the agent a scoped operational context instead of requiring repeated ingestion of all vendor documentation.

This is effectively:

package management for organizational operational intelligence.

⸻

2. Core Objectives

Business objectives

* Reduce duplicated knowledge ingestion across teams and agents
* Preserve institutional knowledge beyond human documentation systems
* Create a human + agent shared operational intelligence platform
* Improve agent effectiveness for DevOps/platform engineering tasks
* Enable reusable enterprise-scale contextual understanding

Technical objectives

* Create portable reusable core knowledge packs
* Support composition of multiple packs per workload
* Allow local/offline operation
* Support Git-native storage
* Support machine-readable structured graph relationships
* Support capability declarations (MCP/skills)
* Enable autonomous generation of packs from vendor sources
* Allow future automated workload discovery from Git repos

⸻

3. Inferred Requirements

⸻

Functional requirements

* Generate vendor knowledge packs from official vendor documentation
* Store entities, documents, relationships, and metadata
* Support pack import/export
* Support pack composition
* Support pack versioning
* Support semantic search
* Support graph traversal
* Support workload overlays
* Support capability registration
* Support MCP integration
* Support CLI interaction
* Support API/MCP service mode
* Support repo analysis for inferred dependency loading

⸻

Non-functional requirements

* Portable across environments
* DB-agnostic pack format
* Deterministic pack structure
* Incrementally extensible
* Git-friendly
* Human-readable
* Agent-optimized
* Low token overhead
* Local-first possible
* Vendor pack immutability
* High interoperability

⸻

Operational requirements

* Pack registry
* Pack installation
* Pack dependency resolution
* Pack version locking
* Overlay merging
* Auth abstraction for capabilities
* Runtime capability injection
* Pack provenance tracking

⸻

Knowledge-management requirements

* Official vendor sources prioritized
* Secondary community sources optional
* Internal organizational overlays supported
* Source provenance retained
* Stable semantic IDs
* Cross-pack deduplication
* Shared canonical vendor ontology

⸻

AI/agent-specific requirements

* Dynamic contextual mounting
* Scoped tool availability
* Agent-readable manifests
* MCP compatibility
* Searchable local memory
* Graph-based context retrieval
* Capability-to-knowledge alignment
* Autonomous authoring support

⸻

4. Architecture Extracted from Conversation

⸻

Major system components

1. Pack generator
2. Pack format definition
3. Pack resolver
4. Graph engine
5. Document store
6. Embedding index
7. Capability registry
8. CLI binary
9. MCP adapter
10. Repo analyzer

⸻

Data flows

Vendor docs
→ crawler
→ extractor
→ graph compiler
→ pack builder
→ package registry
Git repo
→ repo analyzer
→ dependency inference
→ pack resolver
→ agent context
Agent
→ kg system
→ pack query
→ capability resolution
→ action

⸻

Interfaces

* CLI
* local SDK
* MCP server
* REST API (optional)
* pack registry interface
* Git scanner interface

⸻

Integration points

* Git repositories
* MCP servers
* vector databases
* graph databases
* OCI registries
* markdown stores
* local LLM systems

⸻

External dependencies

Potentially:

* Neo4j￼
* Qdrant￼
* Firecrawl￼
* LlamaIndex￼
* GitLab￼
* Amazon ECR￼

⸻

Trust boundaries

* external vendor docs
* community sources
* internal enterprise data
* live operational systems
* agent runtime
* capability endpoints

⸻

Security considerations

* no secrets in packs
* only capability references in manifests
* runtime credential injection
* signed pack distribution
* provenance tracking
* access-scoped overlays

⸻

Extensibility points

* new provider plugins
* new capability types
* new pack storage backends
* new graph engines
* new repo detectors
* new ingestion sources

⸻

5. Decisions Already Made

Topic	Decision	Rationale	Confidence
Core concept	Build composable knowledge packs	Avoid monolithic enterprise graph	Explicit
Runtime model	Separate from harness	Reusable by any agent framework	Explicit
Delivery	Single binary first	Simplicity and portability	Explicit
Interface	CLI + optional MCP	Supports human and agents	Explicit
Base data	Vendor packs prebuilt	Reduce repeated ingestion	Explicit
Storage	Pack-based portable artifact	Portability	Explicit
Format	Likely filesystem bundle	Easy interchange	Strongly implied
Internal overlay	Separate from vendor core	Preserve immutability	Explicit
Capability inclusion	Include MCP/skills references	Actionable context	Explicit
Repo inference	Future automatic dependency detection	Align with existing user project	Explicit
Graph strategy	Federated packs	Reusable scaling	Explicit

⸻

6. Open Questions

1. What exact pack serialization spec should be adopted?
    * SQLite bundle
    * JSONL
    * OCI only
    * hybrid
2. Should embeddings be stored inside packs or generated locally?
3. Should graph storage be:
    * internal SQLite
    * Neo4j import
    * optional adapter layer
4. How much vendor docs should be pre-ingested?
    * full corpus
    * selective service-level packs
5. How should pack update/version refresh work?
6. Should capabilities be executable definitions or references only?
7. How will trust ranking be encoded between official and community sources?
8. Should the repo analyzer be part of MVP or phase 2?

⸻

7. Risks and Assumptions

⸻

Technical risks

* graph complexity explosion
* over-engineering early
* ingestion inconsistency
* vendor documentation scale
* stale packs
* embedding incompatibility
* pack merge conflicts

⸻

Product risks

* building too broad a platform
* unclear immediate value proposition
* overlap with existing internal docs tools
* underestimating operational UX needs

⸻

Organizational risks

* governance ownership unclear
* content maintenance burden
* cross-team adoption friction
* knowledge trust disputes

⸻

Assumptions

* agents benefit from structured modular context
* vendor docs can be reliably transformed
* pack abstraction will remain stable
* capability metadata can be standardized
* Git repo signatures can infer workload accurately

⸻

8. Development Action Plan

⸻

Phase 1 — Discovery

Task: Define pack specification

* Objective: create portable spec
* Inputs: current conversation
* Outputs: .kgpack schema draft
* Dependencies: none
* Tools: YAML, JSON Schema
* Complexity: Medium

Task: Validate vendor ingestion feasibility

* Objective: test AWS docs generation
* Inputs: AWS docs source
* Outputs: prototype pack
* Dependencies: crawler
* Tools: Firecrawl, Python
* Complexity: Medium

⸻

Phase 2 — Architecture

Task: Design core package manager

* Objective: define system internals
* Inputs: pack schema
* Outputs: architecture diagrams
* Dependencies: phase 1
* Tools: Python, diagrams
* Complexity: Medium

Task: Design provider plugin system

* Objective: modular vendor adapters
* Inputs: pack schema
* Outputs: provider interface
* Dependencies: phase 1
* Tools: Python Protocols
* Complexity: Medium

⸻

Phase 3 — Prototype

Task: Build kgx binary

* Objective: create CLI
* Inputs: architecture
* Outputs: executable
* Dependencies: phase 2
* Tools: Python, Typer
* Complexity: Medium

Task: Build AWS provider

* Objective: first real pack generator
* Inputs: docs
* Outputs: aws-core pack
* Dependencies: crawler
* Tools: Python
* Complexity: High

Task: Add search

* Objective: semantic lookup
* Inputs: pack
* Outputs: local search
* Dependencies: pack loader
* Tools: SQLite + vector
* Complexity: Medium

⸻

Phase 4 — Productionization

Task: MCP adapter

* Objective: expose to agents
* Inputs: core engine
* Outputs: MCP server
* Dependencies: phase 3
* Tools: MCP Python SDK
* Complexity: Medium

Task: repo analyzer

* Objective: infer required packs
* Inputs: cloned repos
* Outputs: workload manifests
* Dependencies: phase 3
* Tools: Python, AST parsing
* Complexity: High

Task: registry

* Objective: pack sharing
* Inputs: pack artifacts
* Outputs: OCI publish flow
* Dependencies: phase 3
* Tools: OCI
* Complexity: High

⸻

9. Suggested Repository Structure

kgx/
├── cli/
├── core/
│   ├── pack/
│   ├── resolver/
│   ├── graph/
│   ├── search/
│   └── manifests/
├── providers/
│   ├── aws/
│   ├── databricks/
│   ├── gitlab/
├── mcp/
├── repo_analyzer/
├── schemas/
├── examples/
├── tests/
├── docs/
└── registry/

⸻

10. Agent Handoff Brief

Immediate next step

Define the portable .kgpack specification before writing any code.

⸻

First artifacts to create

1. pack-spec.md
2. manifest.schema.yaml
3. provider-interface.py
4. aws-provider-prototype.py

⸻

What to validate first

Validate that a single vendor pack can be generated automatically from official documentation and queried locally.

This is the architectural proof point.

⸻

What must not be changed from the original intent

Do not collapse this into:

* a generic RAG tool
* a monolithic enterprise knowledge graph
* an agent harness
* a pure wiki system

The original intent is specifically:

a portable package manager for modular operational knowledge + capabilities that can be mounted dynamically by humans and autonomous agents.