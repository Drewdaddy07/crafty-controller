from prometheus_client import CollectorRegistry, Gauge, Info
from prometheus_client.metrics import MetricWrapperBase
from prometheus_client.samples import Sample
from prometheus_client.values import ValueClass


class UncheckedCounter(MetricWrapperBase):
    _type = "counter"

    def set(self, value: float):
        self._value.set(value)

    def _metric_init(self):
        self._value = ValueClass(
            self._type,
            self._name,
            self._name + "_total",
            self._labelnames,
            self._labelvalues,
            self._documentation,
        )

    def _child_samples(self) -> Iterable[Sample]:
        return (Sample("_total", {}, self._value.get(), None, None),)
