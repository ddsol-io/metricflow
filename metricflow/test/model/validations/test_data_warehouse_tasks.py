from copy import deepcopy

import pytest
from _pytest.fixtures import FixtureRequest

from metricflow.engine.metricflow_engine import MetricFlowEngine
from metricflow.model.data_warehouse_model_validator import (
    DataWarehouseModelValidator,
    DataWarehouseTaskBuilder,
    DataWarehouseValidationTask,
)
from metricflow.model.model_transformer import ModelTransformer
from metricflow.model.objects.data_source import DataSource, Mutability, MutabilityType
from metricflow.model.objects.elements.measure import AggregationType, Measure
from metricflow.model.objects.user_configured_model import UserConfiguredModel
from metricflow.model.semantic_model import SemanticModel
from metricflow.model.validations.validator_helpers import ValidationIssueLevel
from metricflow.plan_conversion.column_resolver import DefaultColumnAssociationResolver
from metricflow.plan_conversion.time_spine import TimeSpineSource
from metricflow.protocols.sql_client import SqlClient
from metricflow.specs import MeasureReference
from metricflow.test.fixtures.setup_fixtures import MetricFlowTestSessionState
from metricflow.test.plan_utils import assert_snapshot_text_equal, make_schema_replacement_function
from metricflow.test.test_utils import as_datetime
from metricflow.test.time.configurable_time_source import ConfigurableTimeSource


@pytest.fixture(scope="module")
def mf_engine(  # noqa: D
    data_warehouse_validation_model: UserConfiguredModel,
    sql_client: SqlClient,
    time_spine_source: TimeSpineSource,
    mf_test_session_state: MetricFlowTestSessionState,
) -> MetricFlowEngine:
    semantic_model = SemanticModel(data_warehouse_validation_model)
    return MetricFlowEngine(
        semantic_model=semantic_model,
        sql_client=sql_client,
        column_association_resolver=DefaultColumnAssociationResolver(semantic_model=semantic_model),
        time_source=ConfigurableTimeSource(as_datetime("2020-01-01")),
        time_spine_source=time_spine_source,
        system_schema=mf_test_session_state.mf_system_schema,
    )


def test_build_data_source_tasks(
    mf_test_session_state: MetricFlowTestSessionState, data_warehouse_validation_model: UserConfiguredModel
) -> None:  # noqa:D
    tasks = DataWarehouseTaskBuilder.gen_data_source_tasks(model=data_warehouse_validation_model)
    assert len(tasks) == len(data_warehouse_validation_model.data_sources)
    assert (
        tasks[0].query_string
        == f"SELECT (true) AS col0 FROM (SELECT * FROM {mf_test_session_state.mf_source_schema}.fct_animals) "
        f"WHERE is_dog IS NOT NULL"
    )


def test_task_runner(sql_client: SqlClient, mf_engine: MetricFlowEngine) -> None:  # noqa: D
    dw_validator = DataWarehouseModelValidator(sql_client=sql_client, mf_engine=mf_engine)

    tasks = [
        DataWarehouseValidationTask(query_string="SELECT 'foo' AS foo", error_message="Could not select foo"),
        DataWarehouseValidationTask(query_string="SELECT 'bar' AS bar", error_message="Could not select bar"),
    ]

    issues = dw_validator.run_tasks(tasks=tasks)
    assert len(issues) == 0

    err_msg_bad = "Could not access table 'doesnt_exist' in data warehouse"
    bad_task = DataWarehouseValidationTask(
        query_string="SELECT (true) AS col1 FROM doesnt_exist", error_message=err_msg_bad
    )

    tasks.append(bad_task)
    issues = dw_validator.run_tasks(tasks=tasks)
    assert len(issues) == 1
    assert issues[0].level == ValidationIssueLevel.ERROR
    assert err_msg_bad in issues[0].message


def test_validate_data_sources(  # noqa: D
    data_warehouse_validation_model: UserConfiguredModel,
    create_data_warehouse_validation_model_tables: bool,
    sql_client: SqlClient,
    mf_engine: MetricFlowEngine,
) -> None:
    model = deepcopy(data_warehouse_validation_model)

    dw_validator = DataWarehouseModelValidator(sql_client=sql_client, mf_engine=mf_engine)

    issues = dw_validator.validate_data_sources(model)
    assert len(issues) == 0

    model.data_sources.append(
        DataSource(
            name="test_data_source2",
            sql_table="doesnt_exist",
            dimensions=[],
            mutability=Mutability(type=MutabilityType.IMMUTABLE),
        )
    )

    issues = dw_validator.validate_data_sources(model)
    assert len(issues) == 1
    assert issues[0].level == ValidationIssueLevel.ERROR
    assert "Unable to access data source `test_data_source2`" in issues[0].message


def test_build_metric_tasks(  # noqa: D
    request: FixtureRequest,
    data_warehouse_validation_model: UserConfiguredModel,
    sql_client: SqlClient,
    mf_engine: MetricFlowEngine,
    mf_test_session_state: MetricFlowTestSessionState,
) -> None:
    tasks = DataWarehouseTaskBuilder.gen_metric_tasks(model=data_warehouse_validation_model, mf_engine=mf_engine)
    assert len(tasks) == 1
    assert_snapshot_text_equal(
        request=request,
        mf_test_session_state=mf_test_session_state,
        group_id="data_warehouse_validation_model",
        snapshot_id="query0",
        snapshot_text=tasks[0].query_string,
        snapshot_file_extension=".sql",
        incomparable_strings_replacement_function=make_schema_replacement_function(
            system_schema=mf_test_session_state.mf_system_schema, source_schema=mf_test_session_state.mf_source_schema
        ),
        additional_sub_directories_for_snapshots=(sql_client.__class__.__name__,),
    )


def test_validate_metrics(  # noqa: D
    data_warehouse_validation_model: UserConfiguredModel,
    sql_client: SqlClient,
    mf_engine: MetricFlowEngine,
    time_spine_source: TimeSpineSource,
    mf_test_session_state: MetricFlowTestSessionState,
) -> None:
    model = deepcopy(data_warehouse_validation_model)
    dw_validator = DataWarehouseModelValidator(sql_client=sql_client, mf_engine=mf_engine)

    issues = dw_validator.validate_metrics(model)
    assert len(issues) == 0

    # Update model to have a new measure which creates a new metric by proxy
    new_measures = list(model.data_sources[0].measures)
    new_measures.append(
        Measure(
            name=MeasureReference(element_name="count_cats"),
            agg=AggregationType.SUM,
            expr="is_cat",  # doesn't exist as column
            create_metric=True,
        )
    )
    model.data_sources[0].measures = new_measures
    model.metrics = []
    model = ModelTransformer.pre_validation_transform_model(model)
    model = ModelTransformer.post_validation_transform_model(model)

    # Get new metric flow engine which has the context of the updated model
    semantic_model = SemanticModel(model)
    new_engine = MetricFlowEngine(
        semantic_model=semantic_model,
        sql_client=sql_client,
        column_association_resolver=DefaultColumnAssociationResolver(semantic_model=semantic_model),
        time_source=ConfigurableTimeSource(as_datetime("2020-01-01")),
        time_spine_source=time_spine_source,
        system_schema=mf_test_session_state.mf_system_schema,
    )

    # Validate new metric created by proxy causes an issue (because the column used doesn't exist)
    dw_validator = DataWarehouseModelValidator(sql_client=sql_client, mf_engine=new_engine)
    issues = dw_validator.validate_metrics(model)
    assert len(issues) == 1
    assert issues[0].level == ValidationIssueLevel.ERROR
    assert "Unable to query metric `count_cats`" in issues[0].message