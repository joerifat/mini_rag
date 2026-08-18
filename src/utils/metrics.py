from prometheus_client import Counter,Histogram,generate_latest,CONTENT_TYPE_LATEST
from fastapi import Request,Response,FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
import time


REQUEST_COUNT=Counter("http_request_total","Total_Http_requests",["method","endpoint","status"])
REQUEST_LATENCY=Histogram("http_request_latecny","Latency_of_Http_request",["method","endpoint"])


class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):

        start_time=time.perf_counter()

        response= await call_next(request)

        duration=time.perf_counter()-start_time
        endpoint=request.url.path

        REQUEST_LATENCY.labels(
            method=request.method,endpoint=endpoint
        ).observe(duration)

        REQUEST_COUNT.labels(
            method=request.method,endpoint=endpoint,status=response.status_code
        ).inc()


        return response



def setup_metrics(app:FastAPI):

    app.add_middleware(PrometheusMiddleware)

    @app.get("/youssefrifat_metrics",include_in_schema=False)
    def metrics():
        return Response(generate_latest(),media_type=CONTENT_TYPE_LATEST)






