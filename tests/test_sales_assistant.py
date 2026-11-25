"""Focused tests for sales data tools, the tool loop, and JSON persistence."""

import json
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace

from src.assistant import run_sales_assistant
from src.data_loader import load_sales_data
from src.function_registry import build_function_registry
from src.response_store import save_response
from src.tool_executor import execute_tool
from src.tool_definitions import build_tools
from src.tools.calculations import calculate_order_value
from src.tools.customers import get_customer_details
from src.tools.orders import get_customer_orders


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class SalesAssistantTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = load_sales_data(PROJECT_ROOT / "data" / "sales_database.xlsx")
        cls.registry = build_function_registry(cls.data)

    def test_workbook_loads_all_expected_records(self) -> None:
        self.assertEqual(len(self.data.orders), 6)
        self.assertEqual(len(self.data.customers), 4)
        self.assertEqual(len(self.data.products), 3)
        self.assertEqual(len(self.data.payments), 6)

    def test_customer_lookup_and_unknown_customer_are_distinguished(self) -> None:
        customer = get_customer_details(self.data, "C101")
        orders = get_customer_orders(self.data, "C101")

        self.assertEqual(customer[0]["customer_name"], "Acme Healthcare")
        self.assertEqual(len(orders), 2)
        self.assertEqual(
            get_customer_orders(self.data, "UNKNOWN"),
            {"error": "Customer 'UNKNOWN' was not found."},
        )

    def test_order_value_rejects_negative_inputs(self) -> None:
        self.assertEqual(
            calculate_order_value(3, 8000),
            {"quantity": 3, "unit_price": 8000, "total": 24000},
        )
        with self.assertRaises(ValueError):
            calculate_order_value(-1, 8000)

    def test_executor_returns_tool_protocol_message(self) -> None:
        tool_call = SimpleNamespace(
            id="call-1",
            function=SimpleNamespace(
                name="get_payment_status",
                arguments='{"order_id":"O101"}',
            ),
        )

        result = execute_tool(tool_call, self.registry)

        self.assertEqual(result["role"], "tool")
        self.assertEqual(result["tool_call_id"], "call-1")
        self.assertEqual(json.loads(result["content"])[0]["payment_status"], "Paid")

    def test_assistant_runs_tool_and_returns_final_answer(self) -> None:
        tool_call = SimpleNamespace(
            id="call-2",
            function=SimpleNamespace(
                name="get_order_details",
                arguments='{"order_id":"O101"}',
            ),
        )
        tool_message = SimpleNamespace(
            content=None,
            tool_calls=[tool_call],
            model_dump=lambda **_: {
                "role": "assistant",
                "tool_calls": [{"id": "call-2"}],
            },
        )
        final_message = SimpleNamespace(
            content="Order O101 is delivered.",
            tool_calls=None,
            model_dump=lambda **_: {
                "role": "assistant",
                "content": "Order O101 is delivered.",
            },
        )
        responses = iter([tool_message, final_message])
        recorded_messages: list[list[dict]] = []

        def create(**kwargs: object) -> SimpleNamespace:
            recorded_messages.append(list(kwargs["messages"]))
            return SimpleNamespace(
                choices=[SimpleNamespace(message=next(responses))]
            )

        client = SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(create=create),
            )
        )

        answer = run_sales_assistant(
            query="What is the status of O101?",
            client=client,
            tools=build_tools(),
            registry=self.registry,
            model="test-model",
            max_rounds=2,
        )

        self.assertEqual(answer, "Order O101 is delivered.")
        self.assertEqual(recorded_messages[1][-1]["role"], "tool")
        self.assertEqual(
            json.loads(recorded_messages[1][-1]["content"])[0]["status"],
            "Delivered",
        )

    def test_response_is_saved_as_json_and_updates_latest(self) -> None:
        response = {"query": "Show O101", "answer": "Delivered", "model": "test-model"}
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_dir = Path(temporary_directory)

            saved_path = save_response(response, output_dir)
            saved_content = json.loads(saved_path.read_text(encoding="utf-8"))
            latest_content = json.loads(
                (output_dir / "latest_response.json").read_text(encoding="utf-8")
            )

        self.assertEqual(saved_content["answer"], "Delivered")
        self.assertIn("saved_at_utc", saved_content)
        self.assertEqual(latest_content, saved_content)


if __name__ == "__main__":
    unittest.main()
