from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum

class RecordStatus(str, Enum):
    MIGRATED = "MIGRATED"
    QUARANTINED = "QUARANTINED"
    REJECTED = "REJECTED"

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]

@dataclass
class MigrationRecord:
    legacy_id: str
    source_data: Dict[str, Any]
    target_data: Dict[str, Any]
    status: RecordStatus
    reason: Optional[str] = None
    affected_fields: List[str] = field(default_factory=list)
    transformations: List[str] = field(default_factory=list)

@dataclass
class MigrationReport:
    source: str
    target: str
    records_inspected: int
    migrated_records: int
    rejected_records: int
    quarantined_records: int
    warnings: List[str]
    transformations: List[str]
    schema_conflicts: List[str]
    status: str

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "target": self.target,
            "records_inspected": self.records_inspected,
            "migrated_records": self.migrated_records,
            "rejected_records": self.rejected_records,
            "quarantined_records": self.quarantined_records,
            "warnings": self.warnings,
            "transformations": self.transformations,
            "schema_conflicts": self.schema_conflicts,
            "status": self.status
        }
