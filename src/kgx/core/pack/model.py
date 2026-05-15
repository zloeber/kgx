from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

PackKind = Literal["vendor_core", "overlay", "workload"]


class Manifest(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str
    version: str
    kind: PackKind
    pack_id: str
    created_at: str
    dependencies: list[str] | None = None
    documents_root: str | None = None


class EntityRecord(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    type: str
    label: str
    aliases: list[str] | None = None
    metadata: dict[str, Any] | None = None


class RelationshipRecord(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    from_id: str
    to_id: str
    type: str
    metadata: dict[str, Any] | None = None


class SourceTier(str, Enum):
    vendor_official = "vendor_official"
    vendor_generated = "vendor_generated"
    community = "community"
    internal_overlay = "internal_overlay"


class ProvenanceSource(BaseModel):
    model_config = ConfigDict(extra="allow")

    source_tier: SourceTier
    uri: str | None = None


class ProvenanceFile(BaseModel):
    model_config = ConfigDict(extra="allow")

    sources: list[ProvenanceSource] = Field(default_factory=list)


class McpServerCapability(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str


class CapabilitiesFile(BaseModel):
    model_config = ConfigDict(extra="allow")

    mcp_servers: list[McpServerCapability] = Field(default_factory=list)
    tool_ids: list[str] = Field(default_factory=list)
    skill_paths: list[str] = Field(default_factory=list)


class LoadedPack(BaseModel):
    root: Path
    manifest: Manifest
    entities: list[EntityRecord]
    relationships: list[RelationshipRecord]
    provenance: ProvenanceFile
    capabilities: CapabilitiesFile
    document_paths: list[Path] = Field(default_factory=list)
