from app.classes.web.routes.metrics.index import ApiOpenMetricsIndexHandler

def metrics_handlers(handler_args):
    return [
        # OpenMetrics routes
        (
            r"/metrics/?",
            ApiOpenMetricsIndexHandler,
            handler_args,
        ),
    ]
