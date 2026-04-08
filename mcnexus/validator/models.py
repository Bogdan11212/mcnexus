from dataclasses import dataclass
from typing import Optional

@dataclass
class YAMLValidationError:
    """Detailed information about a YAML syntax error."""
    message: str
    line: int
    column: int
    snippet: Optional[str] = None
    
    def __str__(self) -> str:
        return f"Error at line {self.line}, column {self.column}: {self.message}"

@dataclass
class YAMLValidationResult:
    """The result of a YAML validation check."""
    is_valid: bool
    error: Optional[YAMLValidationError] = None
    
    @property
    def summary(self) -> str:
        if self.is_valid:
            return "Validation successful: No errors found."
        return f"Validation failed: {self.error}"
