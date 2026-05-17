from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from kgx.core.pack.loader import load_pack_directory
from kgx.core.pack.model import (
    CapabilitiesFile,
    EntityRecord,
    LoadedPack,
    Manifest,
    PackKind,
    ProvenanceFile,
    RelationshipRecord,
)
from kgx.core.pack.writer import default_document_rel_path, save_pack_directory


class PackEditor:
    """In-memory editor for a kgpack directory with explicit save."""

    def __init__(self, pack: LoadedPack) -> None:
        self._pack = pack

    @property
    def pack(self) -> LoadedPack:
        return self._pack

    @property
    def root(self) -> Path:
        return self._pack.root

    @classmethod
    def open(cls, path: Path) -> PackEditor:
        return cls(load_pack_directory(path))

    @classmethod
    def create_empty(
        cls,
        out_dir: Path,
        *,
        name: str,
        pack_id: str,
        kind: PackKind = "overlay",
        version: str = "0.1.0",
        documents_root: str = "documents/",
    ) -> PackEditor:
        """Create a new empty pack directory and return an editor for it."""
        created = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        manifest = Manifest(
            name=name,
            version=version,
            kind=kind,
            pack_id=pack_id,
            created_at=created,
            documents_root=documents_root,
        )
        pack = LoadedPack(
            root=Path(out_dir).resolve(),
            manifest=manifest,
            entities=[],
            relationships=[],
            provenance=ProvenanceFile(),
            capabilities=CapabilitiesFile(),
            document_paths=[],
        )
        editor = cls(pack)
        editor.save(validate=False)
        return editor

    def save(self, *, validate: bool = True) -> None:
        """Persist all pack files to disk."""
        save_pack_directory(self._pack, validate=validate)
        self._pack.document_paths = self._refresh_document_paths()

    def _refresh_document_paths(self) -> list[Path]:
        doc_root_name = self._pack.manifest.documents_root or "documents/"
        doc_dir = (self._pack.root / doc_root_name).resolve()
        if not doc_dir.is_dir():
            return []
        return sorted(
            p.relative_to(self._pack.root.resolve())
            for p in doc_dir.rglob("*")
            if p.is_file()
        )

    def _documents_root(self) -> str:
        return self._pack.manifest.documents_root or "documents/"

    def update_manifest(self, **fields: Any) -> None:
        """Update allowed manifest fields (name, version, kind, pack_id, dependencies, documents_root)."""
        allowed = {"name", "version", "kind", "pack_id", "dependencies", "documents_root", "created_at"}
        unknown = set(fields) - allowed
        if unknown:
            msg = f"unsupported manifest fields: {sorted(unknown)}"
            raise ValueError(msg)
        data = self._pack.manifest.model_dump()
        data.update(fields)
        self._pack.manifest = Manifest.model_validate(data)

    def get_entity(self, entity_id: str) -> EntityRecord | None:
        for entity in self._pack.entities:
            if entity.id == entity_id:
                return entity
        return None

    def upsert_entity(
        self,
        entity: EntityRecord,
        *,
        body_md: str | None = None,
    ) -> None:
        """Add or replace an entity; optional ``body_md`` writes/updates its document file."""
        metadata = dict(entity.metadata or {})
        if body_md is not None:
            rel = default_document_rel_path(entity.id, self._documents_root())
            doc_path = self._pack.root / rel
            doc_path.parent.mkdir(parents=True, exist_ok=True)
            doc_path.write_text(body_md, encoding="utf-8")
            metadata["document"] = rel

        updated = entity.model_copy(update={"metadata": metadata or None})
        for i, existing in enumerate(self._pack.entities):
            if existing.id == entity.id:
                self._pack.entities[i] = updated
                return
        self._pack.entities.append(updated)

    def remove_entity(self, entity_id: str) -> bool:
        """Remove an entity and any relationships that reference it."""
        before = len(self._pack.entities)
        self._pack.entities = [e for e in self._pack.entities if e.id != entity_id]
        self._pack.relationships = [
            r
            for r in self._pack.relationships
            if r.from_id != entity_id and r.to_id != entity_id
        ]
        return len(self._pack.entities) < before

    def set_entity_document(self, entity_id: str, body_md: str) -> None:
        """Write document bytes for an existing entity (updates metadata.document)."""
        entity = self.get_entity(entity_id)
        if entity is None:
            msg = f"unknown entity id: {entity_id}"
            raise KeyError(msg)
        self.upsert_entity(entity, body_md=body_md)

    def read_entity_document(self, entity_id: str) -> str | None:
        entity = self.get_entity(entity_id)
        if entity is None or not entity.metadata:
            return None
        rel = entity.metadata.get("document")
        if not isinstance(rel, str):
            return None
        path = self._pack.root / rel
        if not path.is_file():
            return None
        return path.read_text(encoding="utf-8")

    def upsert_relationship(self, relationship: RelationshipRecord) -> None:
        for i, existing in enumerate(self._pack.relationships):
            if existing.id == relationship.id:
                self._pack.relationships[i] = relationship
                return
        self._pack.relationships.append(relationship)

    def remove_relationship(self, relationship_id: str) -> bool:
        before = len(self._pack.relationships)
        self._pack.relationships = [
            r for r in self._pack.relationships if r.id != relationship_id
        ]
        return len(self._pack.relationships) < before
