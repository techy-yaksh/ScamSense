"""Scenario registry."""

from .ss101 import SS101Scenario
from .ss201 import SS201Scenario
from .ss301 import SS301Scenario

_registry = {
    "ss101": SS101Scenario(),
    "ss201": SS201Scenario(),
    "ss301": SS301Scenario(),
}
# Frontend routes use the scenario slug; accept it as an alias for each scenario.
_registry["upi-banking-fraud"] = _registry["ss101"]
_registry["digital-arrest"] = _registry["ss201"]
_registry["fake-job-internship"] = _registry["ss301"]


def get_scenario(scenario_id: str):
    return _registry.get(scenario_id)


def scenario_ids() -> list[str]:
    return list(_registry.keys())


def primary_ids() -> list[str]:
    return ["ss101", "ss201", "ss301"]
