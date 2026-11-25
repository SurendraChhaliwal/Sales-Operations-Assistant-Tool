# Sales Assistant Tool

A modular sales operations assistant that answers questions about customers, orders, products, order values, and payment status using the records in `data/sales_database.xlsx`. It uses OpenAI function calling and presents answers in a Streamlit interface.

## Features

- Loads and validates the `Orders`, `Customers`, `Products`, and `Payments` Excel sheets.
- Keeps each business lookup in a separate tool module.
- Defines JSON schemas for the assistant tools and routes tool calls through a function registry and executor.
- Limits assistant/tool interaction rounds and reports API or execution errors instead of silently returning incomplete answers.
- Saves each successful answer as JSON in `output/` and displays it in the UI.

## Project layout

```text
Sales_assistant_tool/
├── config/
│   └── config.yaml
├── data/
│   └── sales_database.xlsx
├── output/
│   └── .gitkeep
├── src/
│   ├── tools/
│   │   ├── calculations.py
│   │   ├── customers.py
│   │   ├── orders.py
│   │   ├── payments.py
│   │   └── products.py
│   ├── assistant.py
│   ├── config.py
│   ├── data_loader.py
│   ├── function_registry.py
│   ├── response_store.py
│   ├── tool_executor.py
│   ├── tool_schema.py
│   └── tools.py
├── tests/
├── app.py
├── requirements.txt
└── .gitignore
```

## Setup

Use Python 3.10 or newer. From this project directory, create and activate a virtual environment, then install the dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Set an OpenAI API key in the current PowerShell session (do not commit keys to GitHub):

```powershell
$env:OPENAI_API_KEY = "your-api-key"
```

Start the app:

```powershell
streamlit run app.py
```

The model and maximum number of assistant rounds are configurable in `config/config.yaml`. The API key is read only from `OPENAI_API_KEY`.

## Example questions

- `Show the orders for customer C101, including product, quantity, delivery status, and payment status.`
- `What is the payment status for order O102?`
- `What is the order value for 10 units at 5000 each?`
- `Show the details for product P103.`

## Response files

Each successful run writes a timestamped JSON file and updates `output/latest_response.json`. A response includes its UTC save time, the user's query, the configured model, and the assistant's answer. These generated files are ignored by Git by default; the `output/` directory remains in the repository through `.gitkeep`.

## Tests

Run the focused unit tests from this directory:

```powershell
python -m unittest discover -s tests -v
```
