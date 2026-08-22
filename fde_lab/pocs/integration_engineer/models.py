from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class FieldSchema:
    name: str
    type: str
    required: bool
    description: str = ""

@dataclass
class MappingRule:
    source_fields: List[str]
    target_field: str
    transformation_type: str  # e.g., "direct", "concat"

@dataclass
class Mapping:
    rules: List[MappingRule]
    unmapped_source_fields: List[str]

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]

@dataclass
class IntegrationReport:
    records_received: int
    records_transformed: int
    records_rejected: int
    mapping: Mapping
    rejected_records: Dict[str, str]  # customer_id -> reason
    output_path: str
    explanation: str
