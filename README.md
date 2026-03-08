# Sentinel

A lightweight Linux observability and fault-diagnosis training project.

> WIP / learning project  
> This is a learning-oriented, single-node Linux observability project.

## Goals

- Parse /proc manually
- Expose metrics for Prometheus
- Build Grafana dashboards
- Capture fault snapshots
- Reproduce common Linux failures

## Structure

- collector/: parsers for /proc and system data
- exporter/: prometheus metrics exporter
- snapshot/: fault snapshot scripts
- rules/: alert rules
- chaos/: fault injection scripts
- dashboards/: grafana dashboards
- docs/: notes and reports
- tests/: unit tests
