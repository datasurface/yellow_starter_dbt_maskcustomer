"""Contract tests for the PySpark masked-customer implementation."""

from __future__ import annotations

import sys
from types import ModuleType

import pyspark_transformer


class _Expression:
    def __init__(self, value: str) -> None:
        self.value = value

    def alias(self, name: str) -> "_Expression":
        return _Expression(f"{self.value} AS {name}")

    def isNotNull(self) -> "_Expression":
        return _Expression(f"({self.value} IS NOT NULL)")

    def __and__(self, other: "_Expression") -> "_Expression":
        return _Expression(f"({self.value} AND {other.value})")

    def __gt__(self, other: object) -> "_Expression":
        return _Expression(f"({self.value} > {other})")


class _WhenExpression(_Expression):
    def otherwise(self, other: _Expression) -> _Expression:
        return _Expression(f"{self.value} ELSE {other.value}")


class _Functions(ModuleType):
    @staticmethod
    def col(name: str) -> _Expression:
        return _Expression(name)

    @staticmethod
    def lit(value: object) -> _Expression:
        return _Expression(repr(value))

    @staticmethod
    def substring(value: _Expression, start: int, length: int) -> _Expression:
        return _Expression(f"substring({value.value}, {start}, {length})")

    @staticmethod
    def substring_index(value: _Expression, delimiter: str, count: int) -> _Expression:
        return _Expression(
            f"substring_index({value.value}, {delimiter!r}, {count})"
        )

    @staticmethod
    def instr(value: _Expression, substring: str) -> _Expression:
        return _Expression(f"instr({value.value}, {substring!r})")

    @staticmethod
    def concat(*values: _Expression) -> _Expression:
        return _Expression(
            "concat(" + ", ".join(value.value for value in values) + ")"
        )

    @staticmethod
    def when(condition: _Expression, value: _Expression) -> _WhenExpression:
        return _WhenExpression(f"CASE WHEN {condition.value} THEN {value.value}")


class _DataFrame:
    def __init__(self) -> None:
        self.selections: tuple[_Expression, ...] = ()

    def select(self, *expressions: _Expression) -> "_DataFrame":
        self.selections = expressions
        return self


class _Context:
    def __init__(self) -> None:
        self.input = _DataFrame()
        self.read: tuple[str, str, str] | None = None
        self.written: tuple[str, _DataFrame] | None = None

    def getInputDataFrame(
        self, dsg: str, store_name: str, dataset_name: str
    ) -> _DataFrame:
        self.read = (dsg, store_name, dataset_name)
        return self.input

    def writeOutput(self, dataset_name: str, dataframe: _DataFrame) -> None:
        self.written = (dataset_name, dataframe)


def _install_pyspark_stub() -> None:
    pyspark = ModuleType("pyspark")
    sql = ModuleType("pyspark.sql")
    sql.functions = _Functions("pyspark.sql.functions")  # type: ignore[attr-defined]
    pyspark.sql = sql  # type: ignore[attr-defined]
    sys.modules["pyspark"] = pyspark
    sys.modules["pyspark.sql"] = sql
    sys.modules["pyspark.sql.functions"] = sql.functions  # type: ignore[attr-defined]


def test_execute_transformer_uses_portable_context_contract() -> None:
    _install_pyspark_stub()
    context = _Context()

    pyspark_transformer.executeTransformer(object(), context)

    assert context.read == ("Original", "CustomerDB", "customers")
    assert context.written == ("customers", context.input)


def test_mask_customer_projects_iud_shape() -> None:
    _install_pyspark_stub()
    frame = _DataFrame()

    transformed = pyspark_transformer.maskCustomers(frame)

    assert transformed is frame
    expressions = [expression.value for expression in frame.selections]
    assert len(expressions) == 9
    assert expressions[0] == "id AS id"
    assert expressions[1].endswith("AS firstname")
    assert expressions[2].endswith("AS lastname")
    assert "***@" in expressions[4]
    assert "***-***-" in expressions[5]
    assert expressions[-1] == "'U' AS ds_surf_iud"
