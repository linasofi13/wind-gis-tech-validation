"""
Metrics collection infrastructure.

This module provides utilities for collecting and monitoring
performance metrics during processing.
"""

import psutil
import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime


class MetricsCollector:
    """Collects and manages performance metrics."""
    
    def __init__(self):
        """Initialize the metrics collector."""
        self.logger = logging.getLogger(__name__)
        self.start_time = None
        self.start_memory = None
        self.peak_memory = 0
        self.metrics = {}
    
    def start_monitoring(self) -> None:
        """Start monitoring performance metrics."""
        self.start_time = time.time()
        self.start_memory = self.get_memory_usage()
        self.peak_memory = self.start_memory
        self.logger.info("Started performance monitoring")
    
    def stop_monitoring(self) -> Dict[str, Any]:
        """
        Stop monitoring and return collected metrics.
        
        Returns:
            Dictionary of collected metrics
        """
        if self.start_time is None:
            raise ValueError("Monitoring was not started")
        
        end_time = time.time()
        end_memory = self.get_memory_usage()
        
        metrics = {
            "processing_time_seconds": end_time - self.start_time,
            "start_memory_mb": self.start_memory,
            "end_memory_mb": end_memory,
            "peak_memory_mb": self.peak_memory,
            "memory_delta_mb": end_memory - self.start_memory,
            "timestamp": datetime.now().isoformat()
        }
        
        self.metrics.update(metrics)
        self.logger.info(f"Stopped monitoring. Processing time: {metrics['processing_time_seconds']:.2f}s")
        
        return metrics
    
    def get_memory_usage(self) -> float:
        """
        Get current memory usage in MB.
        
        Returns:
            Memory usage in megabytes
        """
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024  # Convert to MB
        
        # Update peak memory
        if memory_mb > self.peak_memory:
            self.peak_memory = memory_mb
        
        return memory_mb
    
    def get_cpu_usage(self) -> float:
        """
        Get current CPU usage percentage.
        
        Returns:
            CPU usage percentage
        """
        return psutil.cpu_percent()
    
    def get_disk_usage(self, path: str) -> Dict[str, float]:
        """
        Get disk usage for a given path.
        
        Args:
            path: Path to check disk usage for
            
        Returns:
            Dictionary with disk usage information
        """
        try:
            usage = psutil.disk_usage(path)
            return {
                "total_gb": usage.total / 1024 / 1024 / 1024,
                "used_gb": usage.used / 1024 / 1024 / 1024,
                "free_gb": usage.free / 1024 / 1024 / 1024,
                "usage_percent": (usage.used / usage.total) * 100
            }
        except Exception as e:
            self.logger.warning(f"Could not get disk usage for {path}: {e}")
            return {}
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get system information.
        
        Returns:
            Dictionary with system information
        """
        return {
            "cpu_count": psutil.cpu_count(),
            "memory_total_gb": psutil.virtual_memory().total / 1024 / 1024 / 1024,
            "memory_available_gb": psutil.virtual_memory().available / 1024 / 1024 / 1024,
            "platform": psutil.platform.platform(),
            "python_version": psutil.sys.version
        }
    
    def add_custom_metric(self, name: str, value: Any) -> None:
        """
        Add a custom metric.
        
        Args:
            name: Metric name
            value: Metric value
        """
        self.metrics[name] = value
        self.logger.debug(f"Added custom metric: {name} = {value}")
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """
        Get all collected metrics.
        
        Returns:
            Dictionary of all metrics
        """
        return self.metrics.copy()
    
    def save_metrics(self, file_path: str) -> None:
        """
        Save metrics to a JSON file.
        
        Args:
            file_path: Path to save metrics file
        """
        import json
        import os
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        
        self.logger.info(f"Metrics saved to: {file_path}")
    
    def reset(self) -> None:
        """Reset all metrics and monitoring state."""
        self.start_time = None
        self.start_memory = None
        self.peak_memory = 0
        self.metrics = {}
        self.logger.info("Metrics collector reset")



