from dataclasses import dataclass, asdict
from typing import Optional
import json

@dataclass
class YAMLValidationError:
    """Detailed information about a YAML syntax error."""
    message: str
    line: int
    column: int
    snippet: Optional[str] = None
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    def __str__(self) -> str:
        return f"Error at line {self.line}, column {self.column}: {self.message}"

@dataclass
class YAMLValidationResult:
    """The result of a YAML validation check."""
    is_valid: bool
    error: Optional[YAMLValidationError] = None
    
    def to_dict(self) -> dict:
        result = {"is_valid": self.is_valid}
        if self.error:
            result["error"] = self.error.to_dict()
        else:
            result["error"] = None
        return result

    def to_json(self, indent: int = 4) -> str:
        """Returns the validation result as a JSON string."""
        return json.dumps(self.to_dict(), indent=indent)
    
    @property
    def summary(self) -> str:
        if self.is_valid:
            return "Validation successful: No errors found."
        return f"Validation failed: {self.error}"
