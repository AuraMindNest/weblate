.. _boost-weblate:

Boost Weblate additions
=======================

This repository extends upstream Weblate with capabilities used for translating
`Boost C++ Libraries <https://www.boost.org/>`_ documentation: QuickBook and
AsciiDoc handling tailored for Boost workflows, optional OpenRouter-based batch
machine translation, and a REST surface for CI-driven component maintenance.

The sections below document fork-specific **configuration**, **dependencies**,
and **HTTP endpoints** that are not covered by generic Weblate documentation.

.. seealso::

   Standard administrator guides still apply: :doc:`install/docker`,
   :ref:`docker-environment`, :doc:`machine`, and :doc:`config`.

Python packages
---------------

OpenRouter batch translation uses the `OpenAI Python SDK <https://pypi.org/project/openai/>`_
(`OpenAI Client`) against the OpenRouter HTTP API. The SDK is **not** part of
core Weblate dependencies; install it explicitly:

.. code-block:: sh

   pip install 'weblate[openai]'
   # or
   pip install 'openai>=2.0,<3.0'

If the SDK is missing when OpenRouter translation runs, Weblate raises
``django.core.exceptions.ImproperlyConfigured`` with an installation hint.

Docker images built from :file:`weblate-docker/Dockerfile` use
``WEBLATE_EXTRAS=all`` so the ``openai`` extra is included in the container.

System commands and packages
----------------------------

The following executables must be available on the server **PATH** where the
relevant code paths execute (web workers, Celery workers):

.. list-table::
   :header-rows: 1
   :widths: 22 78

   * - Executable
     - Used by
   * - ``git``
     - Boost endpoint service: clone repositories, commit and push translation
       changes (see ``weblate.boost_endpoint.services``).
   * - ``po4a-gettextize``, ``po4a-translate``
     - AsciiDoc format pipeline (``weblate.formats.asciidoc``).
   * - ``msgattrib``, ``msgfmt``
     - gettext toolchain for AsciiDoc save path; ``msgattrib`` is optional (the
       code falls back if absent).

The official Docker image for this fork installs **po4a** from source during the
image build (see comments in :file:`weblate-docker/Dockerfile`). Custom or
bare-metal installs must provide **po4a** and **gettext** separately (for
example distribution packages for ``po4a`` and ``gettext``).

Environment variables
---------------------

These variables apply to **Boost fork** behaviour. They do **not** use the
``WEBLATE_`` prefix. Standard Docker variables remain documented under
:ref:`docker-environment`.

.. envvar:: OPENROUTER_API_KEY

   API key used when OpenRouter batch translation cannot read credentials from
   Weblate’s machinery configuration (see :ref:`boost-weblate-openrouter-config`).
   Read by ``weblate.trans.autobatchtranslate``.

.. envvar:: OPENROUTER_MODEL

   Model identifier passed to OpenRouter (for example ``deepseek/deepseek-chat``).
   Default if unset: ``deepseek/deepseek-chat``. Used together with
   :envvar:`OPENROUTER_API_KEY` as an environment fallback.

.. envvar:: AUTO_BATCH_TRANSLATE_VIA_OPENROUTER

   Boolean interpreted by :file:`weblate/settings_docker.py`. When ``true``
   (Docker default), components may trigger automatic batch translation via
   OpenRouter according to internal workflows. When ``false``, that behaviour is
   disabled. For non-Docker installs, set ``AUTO_BATCH_TRANSLATE_VIA_OPENROUTER``
   in :file:`settings.py`.

.. envvar:: BOOST_ENDPOINT_ADD_TRANSLATION_SECONDS

   Integer seconds to wait when the Boost endpoint waits for a component or
   translation to become ready before adding a language (polling interval is
   derived from this setting in ``weblate.boost_endpoint.services``).
   Default in Docker: ``300``. Override per deployment if repositories are slow
   or fast to sync.

.. _boost-weblate-openrouter-config:

OpenRouter credentials (batch translation)
------------------------------------------

Batch OpenRouter translation resolves configuration in this order:

#. **Weblate machinery settings** — category MT, ``openai`` entry with ``key``
   (API key) and ``custom_model`` (model id). This mirrors fields used for the
   generic OpenAI-compatible machinery documented under :ref:`mt-openai`.
#. **Environment variables** — :envvar:`OPENROUTER_API_KEY` and
   :envvar:`OPENROUTER_MODEL` when the database configuration does not supply both
   values.

If no usable key and model are found, auto-translation is skipped and a warning
is logged.

REST API: ``/boost-endpoint/``
-------------------------------

These endpoints are **not** part of the ``/api/`` namespace and are **not**
included in the OpenAPI schema served at ``/api/schema/``. They require an
authenticated user (same token mechanism as :ref:`api-tokens`).

Base path (relative to your site root): ``/boost-endpoint/``.

.. http:get:: /boost-endpoint/

   Returns a short JSON description of the Boost endpoint module.

   :reqheader Authorization: ``Token …`` (required)

   :status 200:

      .. code-block:: json

         {
           "module": "boost-endpoint",
           "description": "Boost documentation translation API"
         }

.. http:post:: /boost-endpoint/add-or-update/

   Accepts a job description and enqueues asynchronous work on a Celery worker.
   The HTTP response returns immediately with a task identifier.

   :reqheader Authorization: ``Token …`` (required)
   :reqheader Content-Type: ``application/json``

   :<json string organization: GitHub organisation hosting Boost library repos (example: ``CppDigest``).
   :<json object add_or_update: Mapping from Weblate language code to a list of repository names (submodules) to process for that language. Must be non-empty.
   :<json string version: Boost branch or tag name (example: ``boost-1.90.0``).
   :<json array extensions: Optional list of file extensions to scan (example: ``[".adoc", ".md"]``). Only extensions Weblate recognises are used; omit or leave empty to allow all supported extensions.

   :status 202: Job accepted; processing continues in Celery.

      .. code-block:: json

         {
           "status": "accepted",
           "task_id": "<celery-task-uuid>",
           "detail": "Boost add-or-update is running in the background; check Celery logs or task result for completion."
         }

   :status 400: Validation error.

      .. code-block:: json

         { "errors": { "...": ["..."] } }

Related Django settings
-----------------------

The following settings appear in :file:`weblate/settings_example.py` for
non-Docker deployments:

``AUTO_BATCH_TRANSLATE_VIA_OPENROUTER``
   Enables or disables OpenRouter batch translation hooks. Defaults to
   ``False`` in the example settings file; Docker defaults differ via
   :envvar:`AUTO_BATCH_TRANSLATE_VIA_OPENROUTER`.

``BOOST_ENDPOINT_ADD_TRANSLATION_SECONDS``
   Delay used when waiting for components during Boost endpoint processing.
   Example file sets ``150`` seconds; Docker overrides via
   :envvar:`BOOST_ENDPOINT_ADD_TRANSLATION_SECONDS` unless customised.

File formats
------------

* :doc:`../formats/quickbook` — QuickBook ``.qbk`` (fork-specific).
* :doc:`../formats/asciidoc` — AsciiDoc (implementation notes including **po4a**).
