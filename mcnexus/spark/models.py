from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

@dataclass
class SparkMetadata:
    platform: str
    version: str
    server_version: str
    start_time: datetime
    end_time: datetime
    duration_seconds: float

@dataclass
class SparkPluginAnalysis:
    name: str
    version: Optional[str] = None
    total_time_percent: float = 0.0
    self_time_percent: float = 0.0
    total_time_ms: float = 0.0
    
    @property
    def impact_score(self) -> float:
        """Heuristic score for server impact."""
        return self.total_time_percent * 1.5 + self.self_time_percent

@dataclass
class SparkProfile:
    id: str
    metadata: SparkMetadata
    tps_avg: float
    tps_min: float
    tps_max: float
    cpu_process_avg: float
    cpu_system_avg: float
    memory_usage_avg_mb: float
    plugins: List[SparkPluginAnalysis] = field(default_factory=list)
    raw_data: Dict[str, Any] = field(default_factory=dict)

    def get_heavy_plugins(self, threshold: float = 1.0) -> List[SparkPluginAnalysis]:
        """Returns plugins that exceed the specified total time percentage threshold."""
        return sorted(
            [p for p in self.plugins if p.total_time_percent >= threshold],
            key=lambda x: x.total_time_percent,
            reverse=True
        )
