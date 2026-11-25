"""Streamlit interface for the sales assistant."""

import json
import os
from pathlib import Path

import streamlit as st
from openai import OpenAI, OpenAIError

from src.assistant import run_sales_assistant
from src.config import load_config, resolve_project_path
from src.data_loader import SalesData, load_sales_data
from src.function_registry import build_function_registry
from src.response_store import save_response
from src.tool_definitions import build_tools


@st.cache_data
def load_cached_sales_data(workbook_path: str) -> SalesData:
    return load_sales_data(Path(workbook_path))


def main() -> None:
    st.set_page_config(page_title="Sales Assistant", page_icon=":bar_chart:", layout="wide")
    config = load_config()
    assistant_config = config["assistant"]
    workbook_path = resolve_project_path(assistant_config["data_file"])
    output_dir = resolve_project_path(config["output_dir"])

    st.title("Sales Operations Assistant")
    st.caption(
        "Ask about customers, orders, products, order values, and payment status."
    )

    data = load_cached_sales_data(str(workbook_path))
    registry = build_function_registry(data)
    tools = build_tools()

    with st.sidebar:
        st.subheader("Sales data")
        st.metric("Orders", len(data.orders))
        st.metric("Customers", len(data.customers))
        st.metric("Products", len(data.products))
        st.metric("Payment records", len(data.payments))
        st.caption(f"Model: {assistant_config['model']}")
        if not os.getenv("OPENAI_API_KEY"):
            st.info("Set OPENAI_API_KEY in your environment to enable questions.")

    with st.form("sales_assistant_query"):
        query = st.text_area(
            "Your question",
            placeholder=(
                "Example: Show the orders for customer C101, including product, "
                "quantity, delivery status, and payment status."
            ),
            height=110,
        )
        submitted = st.form_submit_button("Ask the sales assistant", type="primary")

    if submitted:
        if not query.strip():
            st.warning("Enter a question before submitting.")
        else:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                st.error("OPENAI_API_KEY is not set. Add it and restart Streamlit.")
            else:
                try:
                    with st.spinner("Looking up sales records..."):
                        answer = run_sales_assistant(
                            query=query,
                            client=OpenAI(api_key=api_key),
                            tools=tools,
                            registry=registry,
                            model=assistant_config["model"],
                            max_rounds=assistant_config["max_rounds"],
                        )
                        response = {
                            "query": query,
                            "answer": answer,
                            "model": assistant_config["model"],
                        }
                        saved_path = save_response(response, output_dir)
                    st.session_state["latest_result"] = {
                        **response,
                        "saved_path": str(saved_path),
                    }
                except (OpenAIError, RuntimeError, ValueError) as error:
                    st.error(f"The assistant could not complete the request: {error}")

    result = st.session_state.get("latest_result")
    if result:
        st.subheader("Assistant response")
        st.markdown(result["answer"])
        st.caption(f"Saved to `{result['saved_path']}`")
        download_data = json.dumps(
            {
                "query": result["query"],
                "answer": result["answer"],
                "model": result["model"],
            },
            ensure_ascii=False,
            indent=2,
        )
        st.download_button(
            "Download response JSON",
            data=download_data,
            file_name=Path(result["saved_path"]).name,
            mime="application/json",
        )


if __name__ == "__main__":
    main()
