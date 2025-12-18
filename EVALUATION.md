# 🧪 FinAgent Evaluation System

Comprehensive guide to testing and evaluating your AI financial agent's performance using CSV datasets and automated metrics.

---

## 📖 Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [CSV Format Guide](#csv-format-guide)
- [Evaluation Metrics](#evaluation-metrics)
- [Multi-Tool Testing](#multi-tool-testing)
- [Best Practices](#best-practices)
- [Interpreting Results](#interpreting-results)
- [Advanced Usage](#advanced-usage)

---

## Overview

The evaluation system allows you to systematically test your agent's performance by:

1. **Uploading CSV test datasets** with expected behaviors
2. **Running tests automatically** through the live agent
3. **Receiving real-time results** via streaming
4. **Analyzing metrics** for tool selection, argument matching, and response quality

### Key Features

✅ **Automated Testing** - Run batches of test cases automatically

✅ **Real-Time Streaming** - Watch evaluation progress live

✅ **Three Core Metrics** - Tool selection, argument accuracy, response faithfulness

✅ **Multi-Tool Support** - Test queries requiring multiple tools

✅ **LLM-as-Judge** - GPT-4o evaluates response quality

✅ **Downloadable Results** - Export detailed results as JSON

---

## Quick Start

### 1. Access Evaluation Interface

Navigate to the evaluation page:
```
http://localhost:5173/evaluation
```

### 2. Prepare Your CSV

Create a CSV file with these required columns:
- `test_id` - Unique identifier
- `query` - User question to test
- `expected_tool` - Tool(s) that should be called
- `expected_args` - Expected arguments
- `expected_response_contains` - Keywords for response validation

### 3. Upload and Run

1. Drag and drop your CSV file or click to browse
2. Watch real-time progress as tests execute
3. Review detailed results and summary metrics
4. Download results as JSON if needed

### 4. Example Test

Use the included sample file:
```bash
sample_evaluation.csv
```

---

## CSV Format Guide

### Required Columns

#### **`test_id`**
Unique identifier for each test case.

**Format:** String (e.g., "1", "test_001", "stock_price_test")

**Example:**
```csv
1
```

---

#### **`query`**
The user question to test against the agent.

**Format:** String (quoted if contains commas)

**Examples:**
```csv
"What is Apple's current stock price?"
"Compare AAPL and MSFT financial ratios"
"If I invest $5000 at 7% for 15 years, what will I have?"
```

---

#### **`expected_tool`**
Tool(s) that should be called - single tool name OR JSON array of tool names.

**Format:**
- Single tool: `"tool_name"`
- Multiple tools: `["tool1","tool2"]`

**⚠️ Important:** Use **internal tool names** (snake_case), not display names.

**Available Tools:**
- `get_stock_price`
- `get_company_info`
- `calculate_financial_ratios`
- `calculate_investment_returns`

**Examples:**

**Single Tool:**
```csv
"get_stock_price"
```

**Multiple Tools:**
```csv
["get_stock_price","get_company_info"]
```

---

#### **`expected_args`**
Expected arguments - single JSON object OR array of objects (matching tools order).

**Format:**
- Single tool: `{"key":"value"}`
- Multiple tools: `[{"key1":"value1"},{"key2":"value2"}]`

**⚠️ Critical:** Use **escaped double quotes** (`""`) for quotes inside JSON.

**Examples:**

**Single Tool Arguments:**
```csv
"{""ticker"":""AAPL""}"
"{""ticker"":""MSFT"",""period"":""1mo""}"
"{""principal"":1000,""annual_rate"":7,""years"":10}"
```

**Multiple Tools Arguments:**
```csv
"[{""ticker"":""AAPL""},{""ticker"":""AAPL""}]"
```

**Argument Details by Tool:**

| Tool | Required Args | Optional Args |
|------|--------------|---------------|
| `get_stock_price` | `ticker` | `period` ("1d", "5d", "1mo", "3mo", "6mo", "1y", "2y")<br>`info` (boolean) |
| `get_company_info` | `ticker` | - |
| `calculate_financial_ratios` | `ticker` | - |
| `calculate_investment_returns` | `principal`<br>`annual_rate`<br>`years` | `monthly_contribution` |

---

#### **`expected_response_contains`**
Comma-separated keywords that should appear in the agent's final response.

**Format:** String with comma-separated keywords

**Usage:** Used by LLM judge to evaluate response faithfulness

**Examples:**
```csv
"current price,AAPL"
"sector,industry,Microsoft"
"P/E ratio,profitability"
"future value,compound interest"
```

---

### Complete CSV Examples

#### Example 1: Single Tool Test
```csv
test_id,query,expected_tool,expected_args,expected_response_contains
1,"What is Apple's stock price?","get_stock_price","{""ticker"":""AAPL""}","current price,Apple"
```

#### Example 2: Multi-Tool Test
```csv
test_id,query,expected_tool,expected_args,expected_response_contains
2,"Get Tesla's price and company info","[""get_stock_price"",""get_company_info""]","[{""ticker"":""TSLA""},{""ticker"":""TSLA""}]","Tesla,stock,sector"
```

#### Example 3: Full Test Suite
```csv
test_id,query,expected_tool,expected_args,expected_response_contains
1,"What is Apple's stock price?","get_stock_price","{""ticker"":""AAPL""}","current price"
2,"Tell me about Microsoft","get_company_info","{""ticker"":""MSFT""}","sector,industry"
3,"Calculate ratios for Google","calculate_financial_ratios","{""ticker"":""GOOGL""}","P/E ratio"
4,"$1000 at 7% for 10 years?","calculate_investment_returns","{""principal"":1000,""annual_rate"":7,""years"":10}","future value"
5,"Get Apple price and info","[""get_stock_price"",""get_company_info""]","[{""ticker"":""AAPL""},{""ticker"":""AAPL""}]","Apple,stock,sector"
```

---

## Evaluation Metrics

The system evaluates each test case on three dimensions:

### 1. Tool Selection Accuracy (0.0 - 1.0)

**What it measures:** Did the agent select the correct tool(s)?

**Scoring:**
- **Single tool:**
  - `1.0` - Expected tool was called
  - `0.0` - Expected tool was NOT called

- **Multiple tools:**
  - Percentage of expected tools that were called
  - Example: Expected 3 tools, called 2 correctly = `0.67`

**Example:**
```
Query: "What is Apple's stock price?"
Expected: get_stock_price
Actual: get_stock_price
Score: 1.0 ✅
```

```
Query: "Get Apple's price and info"
Expected: ["get_stock_price", "get_company_info"]
Actual: ["get_stock_price"]
Score: 0.5 ⚠️ (only 1 of 2 tools called)
```

---

### 2. Argument Match (0.0 - 1.0)

**What it measures:** Did the agent extract the correct arguments?

**Scoring:**
- Field-level comparison with normalization
- Percentage of expected fields that match
- Average across all tools (if multiple)

**Normalization Rules:**
- **Strings:** Case-insensitive (`"AAPL"` == `"aapl"`)
- **Numbers:** Float comparison with epsilon (`7` == `7.0`)
- **Nested objects:** Recursive comparison

**Example:**
```
Query: "What is Apple's stock price for the last month?"
Expected: {"ticker": "AAPL", "period": "1mo"}
Actual: {"ticker": "AAPL", "period": "1mo"}
Score: 1.0 ✅ (2/2 fields match)
```

```
Query: "Get MSFT stock data"
Expected: {"ticker": "MSFT", "period": "1mo"}
Actual: {"ticker": "MSFT"}
Score: 0.5 ⚠️ (1/2 fields match, missing period)
```

**Important:**
- Extra fields in actual args don't penalize the score
- Only checks that expected fields are present and correct

---

### 3. Response Faithfulness (0.0 - 1.0)

**What it measures:** Is the response grounded in tool outputs and contains expected content?

**Method:** LLM-as-judge using GPT-4o with temperature=0

**Evaluation Criteria:**
- Response addresses the original query
- Response is grounded in tool outputs (no hallucinations)
- Response contains expected keywords/content
- Response is accurate and complete

**Scoring Rubric:**
- **1.0 (Perfect):** Fully addresses query with all expected content, accurately grounded
- **0.7-0.9 (Good):** Mostly correct, expected content present, minor details missing
- **0.4-0.6 (Partial):** Partially addresses query, some inaccuracies
- **0.0-0.3 (Poor):** Lacks expected content or contains hallucinations

**Example:**
```
Query: "What is Apple's current stock price?"
Expected Contains: "current price"
Tool Output: {"current_price": 182.50, "ticker": "AAPL"}
Response: "Apple's current stock price is $182.50"
Score: 1.0 ✅
```

```
Query: "Tell me about Microsoft"
Expected Contains: "sector,industry"
Tool Output: {"sector": "Technology", "industry": "Software"}
Response: "Microsoft is a company." (doesn't mention sector/industry)
Score: 0.3 ❌
```

---

### Overall Score

**Calculation:** Average of all three metrics

```
Overall Score = (Tool Selection + Argument Match + Faithfulness) / 3
```

**Pass/Fail Threshold:** `0.7`
- Score ≥ 0.7: Test **PASSES** ✅
- Score < 0.7: Test **FAILS** ❌

---

## Multi-Tool Testing

The system fully supports testing queries that require multiple tools.

### How It Works

1. **Tool Selection:** Checks that ALL expected tools were called
   - Score = (Number of expected tools called) / (Total expected tools)

2. **Argument Match:** Validates arguments for EACH expected tool
   - Matches tools in order specified in CSV
   - Averages scores across all tools

3. **Faithfulness:** Uses ALL tool outputs to evaluate response
   - Ensures response incorporates data from all tools

### Example Multi-Tool Test

**CSV Entry:**
```csv
6,"Compare Apple and Microsoft stock prices","[""get_stock_price"",""get_stock_price""]","[{""ticker"":""AAPL""},{""ticker"":""MSFT""}]","Apple,Microsoft,price,comparison"
```

**Agent Behavior:**
1. Calls `get_stock_price` with `ticker="AAPL"`
2. Calls `get_stock_price` with `ticker="MSFT"`
3. Provides comparative analysis

**Evaluation:**
- Tool Selection: 1.0 (both calls to get_stock_price ✅)
- Argument Match: 1.0 (both ticker args correct ✅)
- Faithfulness: 0.95 (includes both prices and comparison ✅)
- **Overall: 0.98 - PASS** ✅

---

## Best Practices

### Writing Good Test Cases

1. **Be Specific**
   - ❌ "Tell me about stocks"
   - ✅ "What is Apple's current stock price?"

2. **Match Real User Queries**
   - Test questions users actually ask
   - Include variations (formal, casual, abbreviated)

3. **Cover Edge Cases**
   - Missing information: "What's the stock price?" (no ticker)
   - Ambiguous requests: "Tell me about Apple" (stock or company?)
   - Multi-step reasoning: "Compare these companies..."

4. **Test Multi-Tool Scenarios**
   - "Get Apple's price and company information"
   - "Compare AAPL and MSFT ratios"
   - "Show me Tesla's price, info, and ratios"

5. **Use Realistic Keywords**
   - Don't require exact wording
   - Include synonyms: "current price,latest price,stock price"
   - Focus on key information, not phrasing

### Dataset Organization

**Small Dataset (5-10 tests):** Quick smoke tests
```csv
- 1 test per tool
- 1 multi-tool test
- 1-2 edge cases
```

**Medium Dataset (20-50 tests):** Comprehensive testing
```csv
- Multiple variations per tool
- Several multi-tool combinations
- Edge cases and error scenarios
```

**Large Dataset (100+ tests):** Production validation
```csv
- Real user query samples
- Full coverage of tool combinations
- Regression tests for known issues
```

### File Naming Convention

```
evaluation_[purpose]_[date].csv

Examples:
- evaluation_smoke_2024-12-17.csv
- evaluation_stock_tools_2024-12-17.csv
- evaluation_production_2024-12-17.csv
```

---

## Interpreting Results

### Summary Metrics

After evaluation completes, you'll see:

```
Pass Rate: 85%
Total Tests: 20
Passed: 17
Failed: 3

Average Scores:
- Tool Selection: 92%
- Argument Match: 85%
- Faithfulness: 88%
Overall Average: 88%
```

### What Good Scores Mean

| Metric | Good (≥90%) | Acceptable (70-89%) | Needs Work (<70%) |
|--------|-------------|---------------------|-------------------|
| **Tool Selection** | Agent reliably chooses correct tools | Mostly correct, occasional mistakes | Frequently selects wrong tools |
| **Argument Match** | Accurately extracts parameters | Usually correct, minor parsing issues | Struggles with parameter extraction |
| **Faithfulness** | Responses grounded and accurate | Generally good, minor deviations | Hallucinations or missing information |

### Individual Test Results

Each test shows:
- **Query** - The question tested
- **Expected Tools** - Tools that should be called
- **Actual Tools** - Tools actually called (green = correct, gray = extra)
- **Metric Scores** - Color-coded (green ≥70%, yellow 40-69%, red <40%)
- **Overall Score** - Final pass/fail status

**Expandable Details:**
- Tool arguments comparison
- Full agent response
- LLM judge explanation

---

## Advanced Usage

### API Testing

Test via API instead of UI:

```bash
# Upload CSV and stream results
curl -N -X POST "http://localhost:8000/evaluations/run" \
  -F "file=@my_tests.csv"
```

Results stream as SSE events:
- `test_case_start` - Test beginning
- `test_case_result` - Test completed
- `summary` - All tests finished
- `error` - Test failed

### Programmatic Evaluation

Create test datasets programmatically:

```python
import csv

tests = [
    {
        "test_id": "1",
        "query": "What is Apple's stock price?",
        "expected_tool": "get_stock_price",
        "expected_args": '{"ticker":"AAPL"}',
        "expected_response_contains": "current price,Apple"
    },
    # ... more tests
]

with open('automated_tests.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=tests[0].keys())
    writer.writeheader()
    writer.writerows(tests)
```

## Troubleshooting

### Common Issues

**Issue:** CSV upload fails with "Invalid CSV format"
- **Solution:** Check column names match exactly
- Ensure no extra spaces in headers
- Verify file encoding is UTF-8

**Issue:** "expected_args must be valid JSON"
- **Solution:** Use escaped quotes: `{""key"":""value""}`
- Don't use single quotes
- Validate JSON syntax

**Issue:** Tool selection score is 0 but tool was called
- **Solution:** Check tool name is internal name (snake_case)
- Example: Use `get_stock_price` not `"Stock Price Lookup"`

**Issue:** Argument match score is low
- **Solution:** Check argument names match exactly
- Ensure data types match (string vs number)
- Include all required arguments

**Issue:** Faithfulness score is low despite correct response
- **Solution:** Check `expected_response_contains` keywords are in response
- Keywords should be general, not exact phrases
- Ensure response actually uses tool outputs

---

## Limits and Performance

- **Max File Size:** 5MB
- **Max Test Cases:** 100 per CSV
- **Per-Test Timeout:** 60 seconds
- **Average Test Time:** 3-13 seconds
  - 2-10s for agent execution
  - 1-3s for LLM judge evaluation

**Performance Tips:**
- Keep test datasets under 50 tests for quick feedback
- Use batch processing for large test suites
- Consider parallelization for production testing

---

## Support and Resources

- **Sample Dataset:** `sample_evaluation.csv`
- **CSV Format Help:** Available in evaluation UI
- **API Docs:** http://localhost:8000/docs
- **Main Documentation:** [README.md](./README.md)

---

<div align="center">

**Happy Testing! 🧪**

Test often, test thoroughly, and iterate on your agent's performance.

</div>
