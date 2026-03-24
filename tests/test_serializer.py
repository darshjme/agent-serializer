"""Tests for agent-serializer."""

import dataclasses
import json
from datetime import datetime, date, time
from enum import Enum
from typing import Any

import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from agent_serializer import Serializer, TypedSerializer, BinarySerializer, serialized


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

class Color(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


@dataclasses.dataclass
class ToolResult:
    name: str
    output: str
    score: float = 0.0


@dataclasses.dataclass
class AgentState:
    step: int
    result: ToolResult
    tags: set


# ---------------------------------------------------------------------------
# Serializer — basic types
# ---------------------------------------------------------------------------

class TestSerializer:
    def setup_method(self):
        self.s = Serializer()

    def test_roundtrip_primitives(self):
        for val in [42, 3.14, "hello", True, None, [], {}]:
            assert self.s.loads(self.s.dumps(val)) == val

    def test_roundtrip_datetime(self):
        dt = datetime(2024, 6, 15, 12, 30, 45)
        result = self.s.loads(self.s.dumps(dt))
        assert result == dt
        assert isinstance(result, datetime)

    def test_roundtrip_date(self):
        d = date(2024, 6, 15)
        result = self.s.loads(self.s.dumps(d))
        assert result == d
        assert isinstance(result, date)

    def test_roundtrip_time(self):
        t = time(14, 30, 0)
        result = self.s.loads(self.s.dumps(t))
        assert result == t
        assert isinstance(result, time)

    def test_roundtrip_set(self):
        s = {1, 2, 3}
        result = self.s.loads(self.s.dumps(s))
        assert result == s
        assert isinstance(result, set)

    def test_roundtrip_enum(self):
        result = self.s.loads(self.s.dumps(Color.RED))
        assert result == Color.RED

    def test_roundtrip_dataclass(self):
        obj = ToolResult(name="search", output="Paris", score=0.95)
        result = self.s.loads(self.s.dumps(obj))
        assert isinstance(result, ToolResult)
        assert result.name == "search"
        assert result.score == 0.95

    def test_roundtrip_bytes(self):
        b = b"\x00\xde\xad\xbe\xef"
        result = self.s.loads(self.s.dumps(b))
        assert result == b
        assert isinstance(result, bytes)

    def test_nested_complex(self):
        obj = {
            "ts": datetime(2025, 1, 1),
            "colors": [Color.RED, Color.BLUE],
            "tags": {1, 2},
        }
        result = self.s.loads(self.s.dumps(obj))
        assert result["ts"] == datetime(2025, 1, 1)
        assert Color.RED in result["colors"]
        assert isinstance(result["tags"], set)

    def test_encode_returns_dict_compatible(self):
        dt = datetime(2024, 1, 1)
        encoded = self.s.encode(dt)
        assert isinstance(encoded, dict)
        assert encoded["__type__"] == "datetime"

    def test_register_custom_type(self):
        class Point:
            def __init__(self, x, y):
                self.x = x
                self.y = y

        s = Serializer()
        s.register(Point, lambda p: {"x": p.x, "y": p.y}, lambda d: Point(d["x"], d["y"]))
        p = Point(3, 7)
        result = s.loads(s.dumps(p))
        assert result.x == 3
        assert result.y == 7


# ---------------------------------------------------------------------------
# TypedSerializer
# ---------------------------------------------------------------------------

class TestTypedSerializer:
    def test_loads_coerces_to_dataclass(self):
        ts = TypedSerializer(ToolResult)
        obj = ToolResult(name="calc", output="42", score=1.0)
        raw = ts.dumps(obj)
        result = ts.loads(raw)
        assert isinstance(result, ToolResult)
        assert result.name == "calc"

    def test_validate_valid(self):
        ts = TypedSerializer(ToolResult)
        assert ts.validate({"name": "x", "output": "y", "score": 0.5}) is True

    def test_validate_missing_required_field(self):
        ts = TypedSerializer(ToolResult)
        # 'name' is required (no default)
        assert ts.validate({"output": "y"}) is False

    def test_dumps_produces_json_string(self):
        ts = TypedSerializer(ToolResult)
        obj = ToolResult(name="t", output="v")
        result = ts.dumps(obj)
        assert isinstance(result, str)
        json.loads(result)  # must be valid JSON

    def test_typed_serializer_inherits_datetime_support(self):
        @dataclasses.dataclass
        class Event:
            name: str
            ts: datetime

        ts = TypedSerializer(Event)
        obj = Event(name="click", ts=datetime(2025, 3, 1, 10, 0))
        result = ts.loads(ts.dumps(obj))
        assert isinstance(result, Event)
        assert result.ts == datetime(2025, 3, 1, 10, 0)


# ---------------------------------------------------------------------------
# BinarySerializer
# ---------------------------------------------------------------------------

class TestBinarySerializer:
    def setup_method(self):
        self.bs = BinarySerializer()

    def test_pack_returns_bytes(self):
        packed = self.bs.pack({"key": "value"})
        assert isinstance(packed, bytes)

    def test_roundtrip_simple(self):
        obj = {"x": 1, "y": [1, 2, 3]}
        assert self.bs.unpack(self.bs.pack(obj)) == obj

    def test_roundtrip_datetime(self):
        obj = {"ts": datetime(2024, 12, 31, 23, 59)}
        result = self.bs.unpack(self.bs.pack(obj))
        assert result["ts"] == datetime(2024, 12, 31, 23, 59)

    def test_roundtrip_set(self):
        obj = {1, 2, 3}
        result = self.bs.unpack(self.bs.pack(obj))
        assert result == obj

    def test_size_reduction_large_payload(self):
        # Repetitive data compresses well
        large = {"data": "hello world " * 500}
        ratio = self.bs.size_reduction(large)
        assert ratio > 0  # must compress

    def test_size_reduction_returns_float(self):
        ratio = self.bs.size_reduction({"x": 1})
        assert isinstance(ratio, float)

    def test_packed_smaller_than_json(self):
        obj = {"items": list(range(1000))}
        raw_size = len(json.dumps(obj).encode("utf-8"))
        packed_size = len(self.bs.pack(obj))
        assert packed_size < raw_size


# ---------------------------------------------------------------------------
# @serialized decorator
# ---------------------------------------------------------------------------

class TestSerializedDecorator:
    def setup_method(self):
        self.s = Serializer()

    def test_return_value_round_trips_datetime(self):
        @serialized(self.s)
        def get_event():
            return {"ts": datetime(2025, 1, 1)}

        result = get_event()
        assert isinstance(result["ts"], datetime)

    def test_dict_arg_decoded(self):
        @serialized(self.s)
        def identity(data):
            return data

        # Pass a raw encoded datetime dict as arg
        encoded = self.s.encode(datetime(2024, 6, 1))
        result = identity(encoded)
        # After decoding the arg, the result should be a datetime
        assert isinstance(result, datetime)

    def test_preserves_function_name(self):
        @serialized(self.s)
        def my_func():
            return 42

        assert my_func.__name__ == "my_func"

    def test_none_return_value(self):
        @serialized(self.s)
        def returns_none():
            return None

        assert returns_none() is None
