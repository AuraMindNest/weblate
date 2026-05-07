# Copyright © Boost Organization <boost@boost.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from weblate.boost_endpoint.serializers import AddOrUpdateRequestSerializer
from weblate.boost_endpoint.tasks import boost_add_or_update_task


class BoostEndpointInfo(APIView):
    """Boost documentation translation API info."""

    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):  # pylint: disable=redefined-builtin  # noqa: A002
        """Return Boost endpoint module info."""
        return Response(
            {
                "module": "boost-endpoint",
                "description": "Boost documentation translation API",
            }
        )


class AddOrUpdateView(APIView):
    """Add or update Boost documentation components."""

    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):  # pylint: disable=redefined-builtin  # noqa: A002
        """
        Create or update Boost documentation components.

        add_or_update is a map: lang_code -> [submodule names]. For each lang_code
        the service runs with that language and its submodule list (clone, scan,
        create/update project and components, add language).

        Heavy work runs in a Celery worker and returns immediately with HTTP 202 and
        task_id so clients can validate the request without waiting for completion.
        """
        serializer = AddOrUpdateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = serializer.validated_data
        async_result = boost_add_or_update_task.delay(
            organization=data["organization"],
            add_or_update=data["add_or_update"],
            version=data["version"],
            extensions=data.get("extensions"),
            user_id=request.user.pk,
        )

        return Response(
            {
                "status": "accepted",
                "task_id": str(async_result.id),
                "detail": (
                    "Boost add-or-update is running in the background; "
                    "check Celery logs or task result for completion."
                ),
            },
            status=status.HTTP_202_ACCEPTED,
        )
