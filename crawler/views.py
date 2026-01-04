from __future__ import annotations

import csv
from io import StringIO

from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import HasCrawlerToken
from crawler.models import CrawlSeed
from crawler.serializers import CrawlSeedSerializer, CrawlerConfigSerializer
from crawler.services import crawler_live_status, get_config, start_crawler_async, CrawlerService


class CrawlerStatusView(APIView):
    permission_classes = [HasCrawlerToken]

    def get(self, request):
        return Response(crawler_live_status())


class CrawlerRunView(APIView):
    permission_classes = [HasCrawlerToken]

    def post(self, request):
        started = start_crawler_async()
        if not started:
            return Response({"status": "already_running"}, status=status.HTTP_409_CONFLICT)
        return Response({"status": "started"}, status=status.HTTP_202_ACCEPTED)


class CrawlerConfigView(APIView):
    permission_classes = [HasCrawlerToken]

    def get(self, request):
        config = get_config()
        return Response(CrawlerConfigSerializer(config).data)

    def put(self, request):
        config = get_config()
        serializer = CrawlerConfigSerializer(config, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class CrawlerSeedsView(APIView):
    permission_classes = [HasCrawlerToken]

    def get(self, request):
        seeds = CrawlSeed.objects.order_by("url")
        return Response(CrawlSeedSerializer(seeds, many=True).data)

    def post(self, request):
        serializer = CrawlSeedSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        seed = serializer.save()
        return Response(CrawlSeedSerializer(seed).data, status=status.HTTP_201_CREATED)


class CrawlerExportView(APIView):
    permission_classes = [HasCrawlerToken]

    def get(self, request):
        buf = StringIO()
        writer = csv.writer(buf)
        service = CrawlerService()
        count = service.export_articles_csv(writer)
        service.close()
        resp = HttpResponse(buf.getvalue(), content_type="text/csv")
        resp["Content-Disposition"] = 'attachment; filename="articles.csv"'
        resp["X-Exported-Rows"] = str(count)
        return resp
