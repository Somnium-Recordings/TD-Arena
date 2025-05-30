#!/usr/bin/env python
"""Test script to verify OpenTelemetry traces are sent to Alloy."""

import logging
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from Lib.tda_telemetry.config import initialize_telemetry
from Lib.tda_telemetry.context import trace_context

# Setup logging
logging.basicConfig(
	level=logging.INFO,
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_alloy_connection():
	"""Test sending traces to Alloy."""
	logger.info("Initializing telemetry...")

	try:
		# Initialize telemetry pointing to Alloy
		initialize_telemetry(
			service_name='td-arena-test',
			endpoint='localhost:4317',
			log_to_console=True
		)
		logger.info("Telemetry initialized successfully")
	except Exception as e:
		logger.error(f"Failed to initialize telemetry: {e}")
		return

	# Send test traces
	logger.info("Sending test traces...")

	with trace_context('test_span_outer', attributes={'test': 'alloy'}) as span:
		logger.info(f"Created outer span: {span.get_span_context().span_id:016x}")
		time.sleep(0.1)

		with trace_context(
			'test_span_inner', attributes={'nested': 'true'}
		) as inner_span:
			logger.info(
				f"Created inner span: {inner_span.get_span_context().span_id:016x}"
			)
			time.sleep(0.1)

	logger.info("Test traces sent. Check Grafana Tempo to verify.")
	logger.info("Access Grafana at: http://localhost:3000")
	logger.info("Default credentials: admin/admin")


if __name__ == "__main__":
	test_alloy_connection()
