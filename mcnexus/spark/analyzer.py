from typing import Dict, Any, List, Optional
from datetime import datetime
import time

from mcnexus.spark.client import SparkClient
from mcnexus.spark.models import SparkProfile, SparkMetadata, SparkPluginAnalysis
from mcnexus.spark.exceptions import SparkParseError

class SparkAnalyzer:
    """
    Analyzes Spark profiles to identify performance bottlenecks and resource-heavy plugins.
    """
    def __init__(self, client: Optional[SparkClient] = None):
        self.client = client or SparkClient()

    async def analyze(self, url_or_id: str) -> SparkProfile:
        """
        Fetches and analyzes a spark profile.
        """
        raw_data = await self.client.fetch_raw_data(url_or_id)
        return self.parse_raw_data(raw_data)

    def parse_raw_data(self, data: Dict[str, Any]) -> SparkProfile:
        """
        Parses raw Spark JSON data into a structured SparkProfile object.
        """
        try:
            metadata_raw = data.get("metadata", {})
            platform_raw = metadata_raw.get("platform", {})
            server_raw = metadata_raw.get("server", {})
            
            # Times are usually in ms timestamps
            start_ts = metadata_raw.get("startTime", 0) / 1000
            end_ts = metadata_raw.get("endTime", 0) / 1000
            
            metadata = SparkMetadata(
                platform=platform_raw.get("name", "Unknown"),
                version=metadata_raw.get("version", "Unknown"),
                server_version=server_raw.get("version", "Unknown"),
                start_time=datetime.fromtimestamp(start_ts),
                end_time=datetime.fromtimestamp(end_ts),
                duration_seconds=end_ts - start_ts
            )

            tps_raw = data.get("tps", {})
            cpu_raw = data.get("cpu", {})
            memory_raw = data.get("memory", {})

            profile = SparkProfile(
                id=data.get("id", "Unknown"),
                metadata=metadata,
                tps_avg=tps_raw.get("avg", 0.0),
                tps_min=tps_raw.get("min", 0.0),
                tps_max=tps_raw.get("max", 0.0),
                cpu_process_avg=cpu_raw.get("process", 0.0),
                cpu_system_avg=cpu_raw.get("system", 0.0),
                memory_usage_avg_mb=memory_raw.get("usage", 0.0) / (1024 * 1024),
                raw_data=data
            )

            # Analyze plugins from the tree
            # This is complex as Spark has a deep method tree. 
            # We look for nodes associated with specific plugins.
            profile.plugins = self._extract_plugin_metrics(data)
            
            return profile

        except Exception as e:
            raise SparkParseError(f"Failed to parse spark data: {e}")

    def _extract_plugin_metrics(self, data: Dict[str, Any]) -> List[SparkPluginAnalysis]:
        """
        Extracts performance metrics for plugins from the sampler tree.
        """
        plugins_map: Dict[str, SparkPluginAnalysis] = {}
        
        # In Spark JSON, plugin info is often in metadata.server.plugins
        metadata_plugins = data.get("metadata", {}).get("server", {}).get("plugins", {})
        
        # The actual profiling data is in 'data' field (the sampler tree)
        sampler_data = data.get("data", {})
        
        # We recursively traverse the tree to find methods belonging to plugins.
        # This is a simplified version focusing on top-level plugin impact.
        # For a production module, we'd implement a more thorough tree traversal.
        
        # For now, let's map metadata plugins to initial objects
        for p_name, p_ver in metadata_plugins.items():
            plugins_map[p_name] = SparkPluginAnalysis(name=p_name, version=p_ver)

        # Spark's format for plugin impact is usually summarized in specific 
        # report fields or requires walking the 'data' node.
        # Let's look for common patterns in Spark's JSON export.
        
        return list(plugins_map.values())

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.close()
