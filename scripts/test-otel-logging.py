#!/usr/bin/env python
"""Test script to verify OpenTelemetry logging setup."""

import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from Lib.tda_telemetry.setup_logging import setup_otel_logging


def test_otel_logging_setup():
	"""Test the OpenTelemetry logging setup."""
	print("Testing OpenTelemetry logging setup...")

	try:
		# Setup OTEL logging
		handler = setup_otel_logging(
			service_name='tda-logging-test', alloy_endpoint='localhost:4317'
		)
		print("✓ OpenTelemetry logging handler created successfully")

		# Test that handler is a LoggingHandler
		from opentelemetry.sdk._logs import LoggingHandler
		assert isinstance(
			handler, LoggingHandler
		), f"Expected LoggingHandler, got {type(handler)}"
		print("✓ Handler is correct type")

		# Test basic functionality by adding handler temporarily
		test_logger = logging.getLogger('test_otel_logger')
		test_logger.addHandler(handler)
		test_logger.setLevel(logging.INFO)

		print("✓ Test logger configured")
		print("Sending test log messages...")

		test_logger.debug("Test debug message - should appear with DEBUG level")
		test_logger.info("Test info message from OpenTelemetry logging")
		test_logger.warning("Test warning message")
		test_logger.error("Test error message")

		print("✓ Test messages sent")
		print("Check Grafana Loki to verify logs are received")
		print("Access Grafana at: http://localhost:3000")

	except Exception as e:
		print(f"✗ Error: {e}")
		import traceback
		traceback.print_exc()


if __name__ == "__main__":
	test_otel_logging_setup()
