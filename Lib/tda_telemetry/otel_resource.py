from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes

tda_resource = Resource.create(
	{
		ResourceAttributes.SERVICE_NAME: 'td-arena',
	}
)
