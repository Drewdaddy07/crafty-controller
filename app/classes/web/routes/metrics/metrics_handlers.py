from app.classes.web.routes.metrics.index import ApiOpenMetricsIndexHandler
from app.classes.web.routes.metrics.host import ApiOpenMetricsCraftyHandler

def metrics_handlers(handler_args):
    return [
        # OpenMetrics routes
        (
            r"/metrics/?",
            ApiOpenMetricsIndexHandler,
            handler_args,
        ),
        (
            r"/metrics/host/?",
            ApiOpenMetricsCraftyHandler,
            handler_args,
        ),
    ]
