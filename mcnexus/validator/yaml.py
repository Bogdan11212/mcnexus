import yaml
import os
from typing import Union, Optional
from mcnexus.validator.models import YAMLValidationResult, YAMLValidationError

class YAMLValidator:
    """
    Asynchronous and synchronous validator for YAML configuration files.
    Focuses on syntax correctness and precise error reporting.
    """
    
    @staticmethod
    def validate_string(content: str) -> YAMLValidationResult:
        """
        Validates a YAML string.
        """
        try:
            yaml.safe_load(content)
            return YAMLValidationResult(is_valid=True)
        except yaml.YAMLError as e:
            error_msg = str(e)
            line = 0
            column = 0
            snippet = None
            
            # Extract coordinates from PyYAML mark
            if hasattr(e, 'problem_mark') and e.problem_mark:
                line = e.problem_mark.line + 1
                column = e.problem_mark.column + 1
                snippet = e.problem_mark.get_snippet()
            
            return YAMLValidationResult(
                is_valid=False,
                error=YAMLValidationError(
                    message=getattr(e, 'problem', error_msg),
                    line=line,
                    column=column,
                    snippet=snippet
                )
            )

    @classmethod
    def validate_file(cls, file_path: str) -> YAMLValidationResult:
        """
        Validates a YAML file on disk.
        """
        if not os.path.exists(file_path):
            return YAMLValidationResult(
                is_valid=False, 
                error=YAMLValidationError(f"File not found: {file_path}", 0, 0)
            )
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return cls.validate_string(content)
        except Exception as e:
            return YAMLValidationResult(
                is_valid=False,
                error=YAMLValidationError(f"IO Error: {str(e)}", 0, 0)
            )

    @classmethod
    async def validate_file_async(cls, file_path: str) -> YAMLValidationResult:
        """
        Asynchronous validation of a YAML file.
        Useful for non-blocking I/O in large networks.
        """
        # For small files, we can just run in a thread or read then validate
        # We'll use a simple approach for compatibility
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, cls.validate_file, file_path)
