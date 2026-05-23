# Expense Tracker MCP

A **Model Context Protocol (MCP) server** built with FastMCP and Python that enables AI assistants to log, retrieve, edit, and summarize personal expenses through natural language — backed by a local SQLite database.

---

## Overview

Traditional expense trackers require you to open an app, navigate menus, and manually fill forms. This project eliminates that friction entirely — you just talk to your AI assistant and it handles the rest.

```
You: "Log ₹500 for a cab ride to Kavali today"
You: "How much did I spend on food this month?"
You: "Update entry 8 — the Udemy course was ₹850, not ₹899"
```

The MCP server exposes structured tools that any MCP-compatible AI client (Claude Desktop, Cursor, etc.) can discover and call automatically.

---

## Tech Stack

| Technology | Role |
|---|---|
| Python 3.13 | Core language |
| FastMCP | MCP server framework |
| SQLite | Local expense storage |
| JSON | Category taxonomy definition |

---

## Features

### Tools

| Tool | Description |
|---|---|
| `add_expenses` | Insert a new expense — date, amount, category, subcategory, note |
| `list_expenses` | Retrieve all expenses within an inclusive date range |
| `summarize_expenses` | Aggregate total spending by category for a date range, with optional category filter |
| `edit_expenses` | Partially update an existing expense by ID — only provided fields are changed |

### Resource

| Resource | Description |
|---|---|
| `expense://categories` | Live MCP resource that exposes the full category taxonomy as JSON — read fresh on every request |

---

## Project Structure

```
Expense-Tracker-MCP/
├── main.py           # MCP server — tool and resource definitions
├── category.json     # Category and subcategory taxonomy
├── pyproject.toml    # Project metadata and dependencies
└── uv.lock           # Locked dependency versions
```

> `expenses.db` is created automatically on first run and is not tracked in version control.

---

## Setup

**Requirements:** Python 3.13+

```bash
# 1. Clone the repository
git clone https://github.com/sathwick06/Expense-Tracker-MCP
cd Expense-Tracker-MCP

# 2. Install dependencies
pip install -e .

# 3. Run the server
python main.py
```

The SQLite database initializes automatically on first run — no manual setup required.

---

## Connecting to Claude Desktop

Add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "expense-tracker": {
      "command": "python",
      "args": ["/absolute/path/to/main.py"]
    }
  }
}
```

Restart Claude Desktop. The tools are immediately available in any conversation.

---

## Usage Examples

**Add an expense**
```
You: "Add ₹1,200 for dinner last night"
→ add_expenses(date="2025-05-23", amount=1200, category="food", subcategory="dining_out")
```

**List expenses for a period**
```
You: "Show me all my expenses for October 2025"
→ list_expenses(start_date="2025-10-01", end_date="2025-10-31")
```

**Summarize spending by category**
```
You: "How much did I spend this month, broken down by category?"
→ summarize_expenses(start_date="2025-10-01", end_date="2025-10-31")
```

**Edit an existing entry**
```
You: "Fix entry 8 — the amount should be ₹850"
→ edit_expenses(id=8, amount=850)
```

---

## Category Taxonomy

Expenses are organized into **20 top-level categories**, each with multiple subcategories:

| Category | Example Subcategories |
|---|---|
| `food` | groceries, dining_out, coffee_tea, delivery_fees |
| `transport` | fuel, cab_ride_hailing, public_transport, parking |
| `housing` | rent, repairs_service, maintenance_hoa |
| `utilities` | electricity, internet_broadband, mobile_phone |
| `health` | medicines, doctor_consultation, fitness_gym |
| `education` | books, courses, online_subscriptions |
| `entertainment` | movies_events, streaming_subscriptions, outing |
| `shopping` | clothing, electronics_gadgets, home_decor |
| `travel` | flights, hotels, local_transport |
| `investments` | mutual_funds, stocks, crypto |
| + 10 more | `subscriptions` · `personal_care` · `business` · `taxes` · `home` · `pet` · `gifts_donations` · `finance_fees` · `family_kids` · `misc` |

The full taxonomy is available via the `expense://categories` MCP resource — AI clients fetch it at runtime so valid categories are always up to date.

---

## Design Decisions

**SQLite over a hosted database**
A local SQLite file requires zero infrastructure, works fully offline, and keeps sensitive financial data on the user's own machine — the right choice for a personal finance tool.

**Category normalization at write time**
All categories and subcategories are stored in lowercase. Enforcing this at insert time rather than query time means summaries and filters are always consistent, regardless of how the AI phrases the input.

**Partial updates in `edit_expenses`**
The SQL `SET` clause is built dynamically from only the fields the caller provides. This prevents unintentional overwrites and keeps tool calls minimal — the AI only needs to send what actually changed.

**Live category resource**
`category.json` is read on every resource request rather than loaded once at startup. This means categories can be added or modified without restarting the server.

**Structured error responses**
All tools return a consistent `{"status": "ok", ...}` or `{"status": "error", "message": "..."}` shape. This gives AI clients reliable, parseable feedback to handle failures gracefully.


