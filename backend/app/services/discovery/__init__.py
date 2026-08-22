"""Scaffolding for automated tool discovery and pricing verification.

Nothing here runs in V1. The module exists so the eventual scheduler has a
defined contract and so no path can publish unverified data automatically.
"""

from app.services.discovery.pipeline import (
    CandidateTool,
    DiscoveryPipeline,
    DiscoveryStage,
)

__all__ = ["CandidateTool", "DiscoveryPipeline", "DiscoveryStage"]
