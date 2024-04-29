from __future__ import annotations

from typing import TYPE_CHECKING, List

from dbt_semantic_interfaces.references import (
    EntityReference,
    SemanticModelReference,
)
from metricflow_semantics.instances import EntityInstance, InstanceSet
from metricflow_semantics.mf_logging.pretty_print import mf_pformat
from metricflow_semantics.model.semantics.semantic_model_join_evaluator import SemanticModelJoinEvaluator

if TYPE_CHECKING:
    from metricflow_semantics.model.semantics.semantic_model_lookup import SemanticModelLookup


class JoinDataflowOutputValidator:
    """Checks that the instances in the output of a join dataflow node is valid."""

    def __init__(self, semantic_model_lookup: SemanticModelLookup) -> None:  # noqa: D107
        self._join_evaluator = SemanticModelJoinEvaluator(semantic_model_lookup)

    @staticmethod
    def _semantic_model_of_entity_in_instance_set(
        instance_set: InstanceSet,
        entity_reference: EntityReference,
    ) -> SemanticModelReference:
        """Return the semantic model where the entity was defined in the instance set."""
        matching_instances: List[EntityInstance] = []
        for entity_instance in instance_set.entity_instances:
            assert len(entity_instance.defined_from) == 1
            if len(entity_instance.spec.entity_links) == 0 and entity_instance.spec.reference == entity_reference:
                matching_instances.append(entity_instance)

        assert len(matching_instances) == 1, (
            f"Not exactly 1 matching entity instances found: {matching_instances} for {entity_reference} in "
            f"{mf_pformat(instance_set)}"
        )
        return matching_instances[0].origin_semantic_model_reference.semantic_model_reference

    def is_valid_instance_set_join(
        self,
        left_instance_set: InstanceSet,
        right_instance_set: InstanceSet,
        on_entity_reference: EntityReference,
    ) -> bool:
        """Return true if the instance sets can be joined using the given entity."""
        return self._join_evaluator.is_valid_semantic_model_join(
            left_semantic_model_reference=JoinDataflowOutputValidator._semantic_model_of_entity_in_instance_set(
                instance_set=left_instance_set, entity_reference=on_entity_reference
            ),
            right_semantic_model_reference=JoinDataflowOutputValidator._semantic_model_of_entity_in_instance_set(
                instance_set=right_instance_set,
                entity_reference=on_entity_reference,
            ),
            on_entity_reference=on_entity_reference,
        )