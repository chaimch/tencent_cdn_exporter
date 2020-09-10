import arrow
import json
import os
from flask import current_app as app
from prometheus_client import Gauge
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.cdn.v20180606 import cdn_client, models


class TencentCdnCollector:
    CDN_EXPORTER_PREFIX = "tencent_cdn_"
    STATUS_CODE = "statusCode"

    def __init__(self, registry, metrics=None):
        self.registry = registry
        self.project_id = app.config["CDN_CONFIG"]["projectId"]
        self.metrics = metrics or app.config["CDN_CONFIG"]["metrics"]
        self.domains = app.config["CDN_CONFIG"]["domains"]
        self._registered = {}

    @property
    def client(self):
        TENCENTCLOUD_SECRET_ID = os.environ.get("TENCENTCLOUD_SECRET_ID")
        TENCENTCLOUD_SECRET_KEY = os.environ.get("TENCENTCLOUD_SECRET_KEY")
        cred = credential.Credential(TENCENTCLOUD_SECRET_ID, TENCENTCLOUD_SECRET_KEY)

        httpProfile = HttpProfile()
        httpProfile.endpoint = "cdn.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = cdn_client.CdnClient(cred, "", clientProfile)
        return client

    def _collect(self, metric):
        req = models.DescribeCdnDataRequest()
        params = {
            "StartTime": arrow.now().floor("minute").format("YYYY-MM-DD hh:mm:ss"),
            "EndTime": arrow.now().ceil("minute").format("YYYY-MM-DD hh:mm:ss"),
            "Metric": metric,
            "Domains": self.domains,
            "Project": self.project_id,
            "Detail": True,
            "Area": "overseas",
        }

        req.from_json_string(json.dumps(params))

        resp = self.client.DescribeCdnData(req)
        result = json.loads(resp.to_json_string())

        if metric == self.STATUS_CODE:
            data = []
            for m in result.get("Data", []):
                for cd in m["CdnData"][1:]:
                    data.append(
                        {
                            "host": m["Resource"],
                            self.STATUS_CODE: cd["Metric"],
                            "value": cd["SummarizedData"]["Value"]
                        }
                    )
            return data

        return [
            {
                "host": m["Resource"],
                "value": m["CdnData"][0]["SummarizedData"]["Value"]
            }
            for m in result.get("Data", [])]

    def collect(self, metric=None, help=None):
        if metric is None and help is None:
            for m in self.metrics:
                if hasattr(self, f"metric_{m.lower()}"):
                    getattr(self, f"metric_{m.lower()}")(m)
            return

        show_metric = f'{self.CDN_EXPORTER_PREFIX}{metric}'
        if show_metric not in self._registered:
            if metric == self.STATUS_CODE:
                self._registered[show_metric] = Gauge(show_metric, help, ['host', 'statusCode'], registry=self.registry)
            else:
                self._registered[show_metric] = Gauge(show_metric, help, ['host'], registry=self.registry)

        gauge = self._registered[show_metric]
        for m in self._collect(metric):
            if metric == self.STATUS_CODE:
                gauge.labels(m["host"], m["statusCode"]).set(m["value"])
            else:
                gauge.labels(m["host"]).set(m["value"])

    def metric_flux(self, metric):
        self.collect(metric, f'cdn {metric} unit bytes')

    def metric_bandwidth(self, metric):
        self.collect(metric, f'cdn {metric} unit bytes/second')

    def metric_request(self, metric):
        self.collect(metric, f'cdn {metric} unit count')

    def metric_fluxhitrate(self, metric):
        self.collect(metric, f'cdn {metric} unit %')

    def metric_statuscode(self, metric):
        self.collect(metric, f'cdn {metric} unit %')
