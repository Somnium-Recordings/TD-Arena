from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes

tda_resource = Resource.create(
	{
		ResourceAttributes.SERVICE_NAME: 'td-arena',
		ResourceAttributes.SERVICE_VERSION: '0.1.0',
	}
)
