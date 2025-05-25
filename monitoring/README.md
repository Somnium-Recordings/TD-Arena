# Monitoring Setup

This directory contains the Docker Compose configuration for monitoring TD-Arena logs using Grafana's LGTM stack (Loki, Grafana, Tempo, Mimir) and Alloy for log collection.

## Components

### LGTM Stack

- **Grafana**: Web UI for visualization (port 3000)
- **Loki**: Log aggregation system (port 3100)
- **Prometheus/Mimir**: Metrics storage (port 9090)
- **Tempo**: Distributed tracing (port 3200)
- **Pyroscope**: Continuous profiling (port 4040)

### Alloy

- Log collector that reads JSON logs from the `../Logs` directory
- Parses JSON format and forwards to Loki
- Web UI available on port 12345

## Quick Start

1. Start the monitoring stack:

   ```bash
   docker-compose up -d
   ```

2. Access the services:
   - Grafana: http://localhost:3000 (default login: admin/admin)
   - Alloy UI: http://localhost:12345
   - Prometheus: http://localhost:9090
   - Loki: http://localhost:3100

## Log Collection

Alloy is configured to:

- Monitor all `*.log` files in the `../Logs` directory
- Parse JSON-formatted logs
- Extract fields like message, level, source, module, etc.
- Handle log rotation automatically
- Store file positions to resume after restarts

## Viewing Logs in Grafana

1. Open Grafana at http://localhost:3000
2. Go to Explore (compass icon)
3. Select Loki as the data source
4. Use LogQL queries to filter logs:
   ```
   {level="ERROR"}
   {source="/tdArena/render/state"}
   {module="logging_mixins"} |= "initialized"
   ```

## Configuration Files

- `docker-compose.yml`: Container orchestration
- `config.alloy`: Alloy configuration for log collection
- `data/lgtm/`: Persistent storage for LGTM stack (Grafana, Loki, Prometheus, etc.)
- `data/alloy/`: Persistent storage for Alloy (file positions for log rotation)

## Directory Structure

```
monitoring/
├── docker-compose.yml
├── config.alloy
├── README.md
├── .gitignore
└── data/              # Created automatically on first run
    ├── lgtm/          # LGTM stack data
    └── alloy/         # Alloy position files
```

## Troubleshooting

### Logs not appearing

1. Check Alloy is running: `docker-compose ps`
2. Check Alloy logs: `docker-compose logs alloy`
3. Verify log files exist in `../Logs` directory
4. Check Alloy UI at http://localhost:12345 for component status

### Debug mode

Enable debug logging by uncommenting in docker-compose.yml:

```yaml
environment:
  ALLOY_LOG_LEVEL: debug
```
