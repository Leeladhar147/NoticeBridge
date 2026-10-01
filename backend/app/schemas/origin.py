from enum import Enum
from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel, Field

class DataOrigin(str, Enum):
    CONTRACT_DERIVED = "contract-derived"
    USER_PROVIDED = "user-provided"
    CALCULATED = "calculated"

T = TypeVar("T")

class TaggedValue(BaseModel, Generic[T]):
    """
    Explicitly tags a field with its provenance origin:
    contract-derived, user-provided, or calculated.
    """
    value: T
    origin: DataOrigin
    source_reference: Optional[str] = Field(
        default=None,
        description="Clause reference, UI input name, or calculation formula name"
    )

def contract_derived(value: Any, source: Optional[str] = None) -> TaggedValue:
    return TaggedValue(value=value, origin=DataOrigin.CONTRACT_DERIVED, source_reference=source)

def user_provided(value: Any, source: Optional[str] = None) -> TaggedValue:
    return TaggedValue(value=value, origin=DataOrigin.USER_PROVIDED, source_reference=source)

def calculated(value: Any, source: Optional[str] = None) -> TaggedValue:
    return TaggedValue(value=value, origin=DataOrigin.CALCULATED, source_reference=source)
