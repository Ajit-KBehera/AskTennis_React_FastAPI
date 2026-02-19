from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
import os


def setup_observability(service_name: str = "asktennis-backend"):
    """
    Configures OpenTelemetry observability.
    defaults to Console exporter for development, OTLP for production if endpoint is set.
    """
    provider = TracerProvider()

    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")

    if otlp_endpoint:
        processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint))
    else:
        # Fallback to console for local dev
        processor = BatchSpanProcessor(ConsoleSpanExporter())

    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)

    return trace.get_tracer(service_name)
