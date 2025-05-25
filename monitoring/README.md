# Grafana OTEL-LGTM Monitoring Stack

This directory contains a Docker Compose setup for the [grafana/otel-lgtm](https://github.com/grafana/docker-otel-lgtm) monitoring stack.

## Components

The stack includes:

- **OpenTelemetry Collector** - Receives and processes telemetry data
- **Prometheus** - Metrics storage and querying
- **Tempo** - Distributed tracing backend
- **Loki** - Log aggregation system
- **Grafana** - Visualization and dashboards
- **Pyroscope** - Continuous profiling platform

## Quick Start

1. Start the monitoring stack:

   ```bash
   docker-compose up -d
   ```

2. Access Grafana at http://localhost:3000

   - Username: `admin`
   - Password: `admin`

3. Stop the monitoring stack:
   ```bash
   docker-compose down
   ```

## Ports

- **3000**: Grafana UI
- **4317**: OpenTelemetry gRPC endpoint
- **4318**: OpenTelemetry HTTP endpoint
- **9090**: Prometheus
- **3200**: Tempo
- **3100**: Loki
- **4040**: Pyroscope

## Sending OpenTelemetry Data

The stack works with OpenTelemetry's default configuration. Your applications can send data to:

- gRPC: `localhost:4317`
- HTTP: `localhost:4318`

Example environment variables for your application:

```bash
export OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
```

## Data Persistence

Data is persisted in the `./data` directory, which is mounted as a volume in the container. This ensures your metrics, logs, and traces are preserved between container restarts.

## Troubleshooting

To enable logging for debugging, uncomment the environment variables in `docker-compose.yml`:

```yaml
environment:
  ENABLE_LOGS_ALL: "true"
  # Or enable specific components:
  # ENABLE_LOGS_GRAFANA: "true"
  # ENABLE_LOGS_LOKI: "true"
  # ENABLE_LOGS_PROMETHEUS: "true"
  # ENABLE_LOGS_TEMPO: "true"
  # ENABLE_LOGS_PYROSCOPE: "true"
  # ENABLE_LOGS_OTELCOL: "true"
```

## Sending Data to External Vendors

To forward telemetry data to external services (e.g., Grafana Cloud), uncomment and configure:

```yaml
environment:
  OTEL_EXPORTER_OTLP_ENDPOINT: "https://your-endpoint.com"
  OTEL_EXPORTER_OTLP_HEADERS: "Authorization=Bearer your-token"
```

## Note

This stack is intended for development, demo, and testing environments. For production use, consider [Grafana Cloud Application Observability](https://grafana.com/products/cloud/application-observability/).
