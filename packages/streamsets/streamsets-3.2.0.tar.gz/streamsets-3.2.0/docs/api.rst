.. _api:

API Reference
=============

The StreamSets SDK for Python is broadly divided into abstractions for interacting with
StreamSet Data Collector and StreamSets Control Hub.

.. module:: streamsets.sdk

StreamSets Data Collector
-------------------------

Main interface
""""""""""""""
This is the main entry point used by users when interacting with SDC instances.

.. autoclass:: streamsets.sdk.DataCollector
    :members:

.. autoattribute:: sdc.DEFAULT_SDC_USERNAME
.. autoattribute:: sdc.DEFAULT_SDC_PASSWORD

Models
""""""
These models wrap and provide useful functionality for interacting with common SDC abstractions.

Alerts
^^^^^^
.. autoclass:: streamsets.sdk.sdc_models.Alert
    :members:
.. autoclass:: streamsets.sdk.sdc_models.Alerts
    :members:

Data Rules
^^^^^^^^^^
.. autoclass:: streamsets.sdk.sdc_models.DataDriftRule
    :members:
.. autoclass:: streamsets.sdk.sdc_models.DataRule
    :members:

History
^^^^^^^
.. autoclass:: streamsets.sdk.sdc_models.History
    :members:
.. autoclass:: streamsets.sdk.sdc_models.HistoryEntry
    :members:

Issues
^^^^^^
.. autoclass:: streamsets.sdk.sdc_models.Issue
    :members:
.. autoclass:: streamsets.sdk.sdc_models.Issues
    :members:

Logs
^^^^
.. autoclass:: streamsets.sdk.sdc_models.Log
    :members:

Metrics
^^^^^^^
.. autoclass:: streamsets.sdk.sdc_models.MetricCounter
    :members:
.. autoclass:: streamsets.sdk.sdc_models.MetricGauge
    :members:
.. autoclass:: streamsets.sdk.sdc_models.MetricHistogram
    :members:
.. autoclass:: streamsets.sdk.sdc_models.MetricTimer
    :members:
.. autoclass:: streamsets.sdk.sdc_models.Metrics
    :members:

Pipelines
^^^^^^^^^
.. autoclass:: streamsets.sdk.sdc_models.PipelineBuilder
    :members:
.. autoclass:: streamsets.sdk.sdc_models.Pipeline
    :members:
.. autoclass:: streamsets.sdk.sdc_models.Stage
    :members:

Pipeline ACLs
^^^^^^^^^^^^^
.. autoclass:: streamsets.sdk.sdc_models.PipelineAcl
    :members:

Pipeline Permissions
^^^^^^^^^^^^^^^^^^^^
.. autoclass:: streamsets.sdk.sdc_models.PipelinePermission
    :members:
.. autoclass:: streamsets.sdk.sdc_models.PipelinePermissions
    :members:

Previews
^^^^^^^^
.. autoclass:: streamsets.sdk.sdc_models.Preview
    :members:

Snapshots
^^^^^^^^^
.. autoclass:: streamsets.sdk.sdc_models.Batch
    :members:
.. autoclass:: streamsets.sdk.sdc_models.Record
    :members:
.. autoclass:: streamsets.sdk.sdc_models.RecordHeader
    :members:
.. autoclass:: streamsets.sdk.sdc_models.Snapshot
    :members:
.. autoclass:: streamsets.sdk.sdc_models.StageOutput
    :members:

Users
^^^^^
.. autoclass:: streamsets.sdk.sdc_models.User
    :members:


StreamSets Control Hub
----------------------

Main interface
""""""""""""""
This is the main entry point used by users when interacting with SCH instances.

.. autoclass:: streamsets.sdk.ControlHub
    :members:

Models
""""""
These models wrap and provide useful functionality for interacting with common SCH abstractions.

Organizations
^^^^^^^^^^^^^
.. autoclass:: streamsets.sdk.sch_models.NewOrganization
    :members:
.. autoclass:: streamsets.sdk.sch_models.Organization
    :members:

Users
^^^^^
.. autoclass:: streamsets.sdk.sch_models.User
    :members:




Common
------
Models used by StreamSets Data Collector and StreamSets Control Hub:

.. autoclass:: streamsets.sdk.models.Configuration
    :members:

Exceptions
----------

.. automodule:: streamsets.sdk.exceptions
    :members:
