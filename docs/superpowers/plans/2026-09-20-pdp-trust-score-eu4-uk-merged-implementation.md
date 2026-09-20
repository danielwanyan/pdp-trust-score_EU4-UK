# PDP Trust Score EU4+UK Merged Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an isolated UK+EU4 merged PDP Trust Score Aicolate copybook in `pdp-trust-score_EU4-UK`, with all-product-image input, size chart and product attribute RPC support, strict target-country language localization, mixed UK/EU4 price semantics, and 30-day-new-product quality tolerance.

**Architecture:** Start from the existing single-product, single-LLM PDP Trust copybook, but place all deployable assets in the new repository so old raw URLs and old workflow versions are untouched. Keep `Trust_Evaluator` as the only LLM node, with Code Nodes responsible for deterministic RPC parsing, price normalization, rules context, evidence manifests, and prompt support fields. Preserve the RESULT JSON whitelist.

**Tech Stack:** Python Aicolate Code Nodes, JSON rulebook, plain-text Aicolate prompts, Markdown copybook docs, `python3 -m pytest` for local validation, GitHub raw URLs for Aicolate HTTP Request nodes.

---

## File Structure

Create or modify these files in `/Users/bytedance/pdp-trust-score_EU4-UK`:

- Create `rules/pdp_trust_rules_structured_v1.json`: structured rule source for locale profiles, routing, strict language, long-image, size-chart, and new-product rules.
- Create `rules/pdp_trust_rules_compressed_v1.txt`: compressed full rulebook fallback for `Trust_Evaluator`.
- Create `code_nodes/final_data_cleaning_pdp_trust_v1.py`: parse Start fields, both RPC nodes, all product main images, size chart images, product attributes, mixed currency semantics, and new-product flag.
- Create `code_nodes/rules_brain_pdp_trust_v1.py`: select relevant rules and emit `rules_context`, `locale_context`, `visual_evidence_context`, `new_product_context`, `price_context`, and debug fields.
- Create `code_nodes/context_builder_pdp_trust_v1.py`: build the single-LLM status bar, evidence manifest, and decision checklist.
- Create `prompts/trust_evaluator_system_prompt_v1.txt`: stable plain-text system prompt.
- Create `prompts/trust_evaluator_user_prompt_v1.txt`: dynamic user prompt with visual variables and RESULT examples.
- Create `docs/overview.md`: concise project overview and version boundary.
- Create `docs/wiring-checklist.md`: Aicolate node-by-node copy/paste and Output panel checklist.
- Create `tests/validate_pdp_trust_assets.py`: local contract tests for copybook assets.

Use old assets only as source material:

```text
/Users/bytedance/Desktop/EU-LLM_Wiki/wiki/projects/pdp-trust-score/code_nodes/
/Users/bytedance/Desktop/EU-LLM_Wiki/wiki/projects/pdp-trust-score/prompts/
/Users/bytedance/Desktop/EU-LLM_Wiki/wiki/projects/pdp-trust-score/rules/
```

Do not edit the old wiki copybook or `/Users/bytedance/pdp-trust-score` while executing this plan.

---

### Task 1: Seed The New Repository With Baseline Assets

**Files:**
- Create: `/Users/bytedance/pdp-trust-score_EU4-UK/rules/pdp_trust_rules_structured_v1.json`
- Create: `/Users/bytedance/pdp-trust-score_EU4-UK/rules/pdp_trust_rules_compressed_v1.txt`
- Create: `/Users/bytedance/pdp-trust-score_EU4-UK/code_nodes/final_data_cleaning_pdp_trust_v1.py`
- Create: `/Users/bytedance/pdp-trust-score_EU4-UK/code_nodes/rules_brain_pdp_trust_v1.py`
- Create: `/Users/bytedance/pdp-trust-score_EU4-UK/code_nodes/context_builder_pdp_trust_v1.py`
- Create: `/Users/bytedance/pdp-trust-score_EU4-UK/prompts/trust_evaluator_system_prompt_v1.txt`
- Create: `/Users/bytedance/pdp-trust-score_EU4-UK/prompts/trust_evaluator_user_prompt_v1.txt`
- Create: `/Users/bytedance/pdp-trust-score_EU4-UK/tests/validate_pdp_trust_assets.py`

- [ ] **Step 1: Create asset directories**

Run:

```bash
mkdir -p rules code_nodes prompts tests docs
```

Expected: command exits with status 0.

- [ ] **Step 2: Copy baseline copybook files from the current PDP Trust assets**

Run:

```bash
cp /Users/bytedance/Desktop/EU-LLM_Wiki/wiki/projects/pdp-trust-score/rules/pdp_trust_rules_structured_v1.json rules/pdp_trust_rules_structured_v1.json
cp /Users/bytedance/Desktop/EU-LLM_Wiki/wiki/projects/pdp-trust-score/rules/pdp_trust_rules_compressed_v1.txt rules/pdp_trust_rules_compressed_v1.txt
cp /Users/bytedance/Desktop/EU-LLM_Wiki/wiki/projects/pdp-trust-score/code_nodes/final_data_cleaning_pdp_trust_v1.py code_nodes/final_data_cleaning_pdp_trust_v1.py
cp /Users/bytedance/Desktop/EU-LLM_Wiki/wiki/projects/pdp-trust-score/code_nodes/rules_brain_pdp_trust_v1.py code_nodes/rules_brain_pdp_trust_v1.py
cp /Users/bytedance/Desktop/EU-LLM_Wiki/wiki/projects/pdp-trust-score/code_nodes/context_builder_pdp_trust_v1.py code_nodes/context_builder_pdp_trust_v1.py
cp /Users/bytedance/Desktop/EU-LLM_Wiki/wiki/projects/pdp-trust-score/prompts/trust_evaluator_system_prompt_v1.txt prompts/trust_evaluator_system_prompt_v1.txt
cp /Users/bytedance/Desktop/EU-LLM_Wiki/wiki/projects/pdp-trust-score/prompts/trust_evaluator_user_prompt_v1.txt prompts/trust_evaluator_user_prompt_v1.txt
cp /Users/bytedance/Desktop/EU-LLM_Wiki/wiki/projects/pdp-trust-score/tests/validate_pdp_trust_assets.py tests/validate_pdp_trust_assets.py
```

Expected: files exist in the new repo with the same names.

- [ ] **Step 3: Run baseline validation so future failures are attributable**

Run:

```bash
python3 -m pytest tests/validate_pdp_trust_assets.py -q
```

Expected: tests may fail because the copied test file still expects old `locale: UK` in some assertions while copied assets are already partially dynamic. Record the exact failing tests before editing.

- [ ] **Step 4: Commit the seeded baseline**

Run:

```bash
git add rules code_nodes prompts tests
git commit -m "chore: seed PDP trust copybook baseline"
```

Expected: a commit is created. If Step 3 failed due to known copied-test drift, mention the failing test names in the commit body or implementation notes.

---

### Task 2: Add Failing Tests For New RPC Output Contracts

**Files:**
- Modify: `/Users/bytedance/pdp-trust-score_EU4-UK/tests/validate_pdp_trust_assets.py`

- [ ] **Step 1: Add a reusable Code Node loader helper**

Insert near the top of `tests/validate_pdp_trust_assets.py`, after constants:

```python
def load_code_node(rel_path):
    code_path = ROOT / rel_path
    namespace = {"Args": object, "Output": dict}
    source = code_path.read_text()
    exec(compile(source, str(code_path), "exec"), namespace)
    return namespace
```

- [ ] **Step 2: Add a test that all product main images are preserved**

Add this test after the existing image parsing tests:

```python
def test_final_data_cleaning_preserves_all_product_main_images():
    namespace = load_code_node("code_nodes/final_data_cleaning_pdp_trust_v1.py")
    payload = {
        "output": {
            "BaseResp": {"StatusCode": 0, "StatusMessage": ""},
            "result": {
                "ProductMeta.images": {
                    "feature_code": "ProductMeta.images",
                    "feature_type": "Array",
                    "feature_value": json.dumps(
                        [
                            "https://example.com/main-1.jpeg",
                            "https://example.com/main-2.jpeg",
                            "https://example.com/detail-long.jpeg",
                        ]
                    ),
                }
            },
        }
    }
    output = namespace["build_output"](
        {
            "product_id": "all-images-case",
            "product_name": "All Image Case",
            "target_country": "UK",
            "rpc_images": payload,
        }
    )
    assert output["product_main_images"] == [
        "https://example.com/main-1.jpeg",
        "https://example.com/main-2.jpeg",
        "https://example.com/detail-long.jpeg",
    ]
    assert output["images"][:3] == output["product_main_images"]
    assert "product_main_images_count=3" in output["image_manifest"]
    assert "first image only" not in output["final_data_cleaning_debug"].lower()
```

- [ ] **Step 3: Add a test for product attributes and size chart RPC parsing**

Add this test after the all-images test:

```python
def test_final_data_cleaning_parses_product_extra_attributes_rpc():
    namespace = load_code_node("code_nodes/final_data_cleaning_pdp_trust_v1.py")
    extra_payload = {
        "output": {
            "BaseResp": {"StatusCode": 0, "StatusMessage": ""},
            "result": {
                "product_extra_attributes.product_attributes": {
                    "bolt_usable_type": 0,
                    "description": "",
                    "display_name": "",
                    "feature_code": "product_attributes",
                    "feature_type": "Array",
                    "feature_value": json.dumps(
                        [
                            {"value": "Plain", "label": "Pattern"},
                            {"value": "Summer", "label": "Season"},
                            {"label": "Style", "value": "Party"},
                            {"label": "Material", "value": "Strong polyester single jersey"},
                            {"value": "Polyester 95%Elastane 5%", "label": "Composition"},
                        ],
                        ensure_ascii=False,
                    ),
                    "is_bolt_usable": True,
                },
                "product_extra_attributes.size_chart": {
                    "bolt_usable_type": 0,
                    "description": "",
                    "display_name": "",
                    "feature_code": "size_chart",
                    "feature_type": "Array",
                    "feature_value": json.dumps(["https://example.com/size-chart.jpeg"]),
                    "is_bolt_usable": True,
                },
            },
        }
    }
    output = namespace["build_output"](
        {
            "product_id": "extra-attributes-case",
            "product_name": "Extra Attributes Case",
            "target_country": "DE",
            "product_extra_attributes": extra_payload,
        }
    )
    assert output["size_chart_images"] == ["https://example.com/size-chart.jpeg"]
    assert "Pattern=Plain" in output["product_attributes_text"]
    assert "Material=Strong polyester single jersey" in output["product_attributes_text"]
    assert "Composition=Polyester 95%Elastane 5%" in output["product_attributes_text"]
    assert '"label": "Pattern"' in output["product_attributes_json"]
    assert "product_attributes=yes" in output["extra_attributes_source"]
    assert "size_chart_images_count=1" in output["image_manifest"]
```

- [ ] **Step 4: Run the new RPC tests and confirm they fail**

Run:

```bash
python3 -m pytest tests/validate_pdp_trust_assets.py::test_final_data_cleaning_preserves_all_product_main_images tests/validate_pdp_trust_assets.py::test_final_data_cleaning_parses_product_extra_attributes_rpc -q
```

Expected: FAIL because `product_main_images`, `size_chart_images`, `product_attributes_text`, and `image_manifest` are not implemented yet.

---

### Task 3: Implement RPC Parsing In Final_data_cleaning

**Files:**
- Modify: `/Users/bytedance/pdp-trust-score_EU4-UK/code_nodes/final_data_cleaning_pdp_trust_v1.py`
- Test: `/Users/bytedance/pdp-trust-score_EU4-UK/tests/validate_pdp_trust_assets.py`

- [ ] **Step 1: Replace single-image build logic with two-source visual parsing**

In `final_data_cleaning_pdp_trust_v1.py`, replace the existing `build_images` function with:

```python
def dedupe_preserve_order(values):
    output = []
    for value in values:
        text = clean_text(value)
        if text and text.startswith(("http://", "https://")) and text not in output:
            output.append(text)
    return output


def build_product_main_images(params):
    urls = extract_rpc_images(params)
    return dedupe_preserve_order(urls)


def extract_feature_value_from_result(result, literal_key, feature_code):
    if not isinstance(result, dict):
        return None
    literal = result.get(literal_key)
    if isinstance(literal, dict) and "feature_value" in literal:
        return literal.get("feature_value")
    if literal is not None:
        return literal
    for value in result.values():
        if isinstance(value, dict) and value.get("feature_code") == feature_code:
            return value.get("feature_value")
    return None


def extract_product_extra_result(params):
    raw = find_param(
        params,
        (
            "product_extra_attributes",
            "product_extra_attributes_rpc",
            "product_extra_attributes_output",
            "extra_attributes",
            "extra_attributes_output",
        ),
    )
    return get_result_object(raw)


def parse_product_attributes(value):
    parsed = maybe_json(value)
    if parsed is None:
        parsed = value
    if not isinstance(parsed, list):
        text = clean_text(value)
        return text, text
    pairs = []
    normalized = []
    for item in parsed:
        if not isinstance(item, dict):
            continue
        label = clean_text(item.get("label"))
        attr_value = clean_text(item.get("value"))
        if not label and not attr_value:
            continue
        normalized.append({"label": label, "value": attr_value})
        if label and attr_value:
            pairs.append(f"{label}={attr_value}")
        elif label:
            pairs.append(label)
        else:
            pairs.append(attr_value)
    return "; ".join(pairs), json.dumps(normalized, ensure_ascii=False)


def build_extra_attributes(params):
    result = extract_product_extra_result(params)
    attributes_raw = extract_feature_value_from_result(
        result,
        "product_extra_attributes.product_attributes",
        "product_attributes",
    )
    size_chart_raw = extract_feature_value_from_result(
        result,
        "product_extra_attributes.size_chart",
        "size_chart",
    )
    product_attributes_text, product_attributes_json = parse_product_attributes(attributes_raw)
    size_chart_images = dedupe_preserve_order(split_url_list(size_chart_raw))
    source_parts = [
        f"product_attributes={'yes' if product_attributes_text else 'no'}",
        f"size_chart_images_count={len(size_chart_images)}",
    ]
    if not isinstance(result, dict) or not result:
        source_parts.append("missing_product_extra_attributes")
    return {
        "product_attributes_text": product_attributes_text,
        "product_attributes_json": product_attributes_json,
        "size_chart_images": size_chart_images,
        "extra_attributes_source": "; ".join(source_parts),
    }


def build_images(params):
    product_main_images = build_product_main_images(params)
    extra = build_extra_attributes(params)
    size_chart_images = extra["size_chart_images"]
    images = dedupe_preserve_order(product_main_images + size_chart_images)
    image_manifest = "; ".join(
        [
            f"product_main_images_count={len(product_main_images)}",
            f"size_chart_images_count={len(size_chart_images)}",
            "image_order=product_main_images first, then size_chart_images",
        ]
    )
    if product_main_images and size_chart_images:
        image_source = "product_main_images+size_chart_images"
    elif product_main_images:
        image_source = "product_main_images"
    elif size_chart_images:
        image_source = "missing_product_main_images+size_chart_images"
    else:
        image_source = "missing_product_main_images+missing_size_chart_images"
    return product_main_images, size_chart_images, images, image_source, image_manifest, extra
```

- [ ] **Step 2: Update `build_output` to return the new visual and attribute fields**

Change the first lines of `build_output` from:

```python
product_desc = html_to_text(find_param(params, ("product_desc",)))
images, image_source = build_images(params)
localized_price_fields = build_localized_price_fields(params)
```

to:

```python
product_desc = html_to_text(find_param(params, ("product_desc",)))
product_main_images, size_chart_images, images, image_source, image_manifest, extra_attributes = build_images(params)
localized_price_fields = build_localized_price_fields(params)
```

Add these fields to the returned `output` dictionary after `product_name`:

```python
"product_main_images": product_main_images,
"size_chart_images": size_chart_images,
"image_manifest": image_manifest,
"product_attributes_text": extra_attributes["product_attributes_text"],
"product_attributes_json": extra_attributes["product_attributes_json"],
"extra_attributes_source": extra_attributes["extra_attributes_source"],
```

Keep `"images": images` so Aicolate can still bind one image array when needed.

- [ ] **Step 3: Update debug mapping**

In `build_debug_mapping`, append these fragments to the returned string:

```python
f"; product_main_images_count={len(output.get('product_main_images', []))}"
f"; size_chart_images_count={len(output.get('size_chart_images', []))}"
f"; extra_attributes_source={output.get('extra_attributes_source', '')}"
```

- [ ] **Step 4: Run the RPC tests and verify they pass**

Run:

```bash
python3 -m pytest tests/validate_pdp_trust_assets.py::test_final_data_cleaning_preserves_all_product_main_images tests/validate_pdp_trust_assets.py::test_final_data_cleaning_parses_product_extra_attributes_rpc -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

Run:

```bash
git add code_nodes/final_data_cleaning_pdp_trust_v1.py tests/validate_pdp_trust_assets.py
git commit -m "feat: parse product images and extra attributes"
```

Expected: commit succeeds.

---

### Task 4: Add Failing Tests For Mixed Price Semantics And New-Product Flag

**Files:**
- Modify: `/Users/bytedance/pdp-trust-score_EU4-UK/tests/validate_pdp_trust_assets.py`

- [ ] **Step 1: Add constants for supported countries and EUR conversion**

Insert after `ALLOWED_B_END_REASONS`:

```python
SUPPORTED_TARGET_COUNTRIES = {"UK", "DE", "FR", "ES", "IT"}
EXPECTED_TARGET_CURRENCIES = {
    "UK": "GBP",
    "DE": "EUR",
    "FR": "EUR",
    "ES": "EUR",
    "IT": "EUR",
}
USD_TO_EUR = "0.86453"
EXCHANGE_RATE_DATE = "2026-08-14"
```

- [ ] **Step 2: Add mixed price-semantics tests**

Add these tests after the RPC parsing tests:

```python
def test_final_data_cleaning_uses_native_gbp_for_uk_prices():
    namespace = load_code_node("code_nodes/final_data_cleaning_pdp_trust_v1.py")
    output = namespace["build_output"](
        {
            "product_id": "price-uk",
            "product_name": "UK price case",
            "target_country": "UK",
            "sales_price": "100",
            "shipping_fee": "10",
            "list_price_usd": "150",
        }
    )
    assert output["currency"] == "GBP"
    assert output["target_currency"] == "GBP"
    assert output["price_input_semantics"] == "UK sales_price and shipping_fee are native GBP; no conversion applied"
    assert output["sales_price_local"] == "100.00"
    assert output["shipping_fee_local"] == "10.00"
    assert output["landed_cost_local"] == "110.00"
    assert "no conversion applied" in output["localized_price_context"]
    assert "list_price_usd=150.00 USD anchor only" in output["localized_price_context"]


def test_final_data_cleaning_converts_eu4_usd_prices_to_eur():
    namespace = load_code_node("code_nodes/final_data_cleaning_pdp_trust_v1.py")
    for country in ["DE", "FR", "ES", "IT"]:
        output = namespace["build_output"](
            {
                "product_id": f"price-{country.lower()}",
                "product_name": "EU4 price case",
                "target_country": country,
                "sales_price": "100",
                "shipping_fee": "10",
                "list_price_usd": "150",
            }
        )
        assert output["currency"] == "USD"
        assert output["target_currency"] == "EUR"
        assert output["exchange_rate_to_target_currency"] == USD_TO_EUR
        assert output["exchange_rate_date"] == EXCHANGE_RATE_DATE
        assert output["price_input_semantics"] == "EU4 sales_price and shipping_fee are USD; converted to EUR"
        assert output["sales_price_local"] == "86.45"
        assert output["shipping_fee_local"] == "8.65"
        assert output["landed_cost_local"] == "95.10"
        assert "100.00 USD -> 86.45 EUR" in output["localized_price_context"]
        assert "110.00 USD -> 95.10 EUR" in output["localized_price_context"]
```

- [ ] **Step 3: Add new-product flag parsing tests**

Add this test after the price tests:

```python
def test_final_data_cleaning_normalizes_new_product_30d_flag():
    namespace = load_code_node("code_nodes/final_data_cleaning_pdp_trust_v1.py")
    truthy = namespace["build_output"](
        {
            "product_id": "new-product",
            "product_name": "New Product",
            "target_country": "FR",
            "is_new_product_30d": "1",
            "cl_pay_sub_order_cnt": "9",
        }
    )
    assert truthy["is_new_product_30d"] == "true"
    assert truthy["new_product_context"] == "is_new_product_30d=true; cl_pay_sub_order_cnt=9; new_product_low_sales=yes"

    empty = namespace["build_output"](
        {
            "product_id": "old-product",
            "product_name": "Old Product",
            "target_country": "FR",
            "is_new_product_30d": "",
            "cl_pay_sub_order_cnt": "0",
        }
    )
    assert empty["is_new_product_30d"] == "false"
    assert "new_product_low_sales=no" in empty["new_product_context"]
```

- [ ] **Step 4: Run the new tests and confirm they fail**

Run:

```bash
python3 -m pytest tests/validate_pdp_trust_assets.py::test_final_data_cleaning_uses_native_gbp_for_uk_prices tests/validate_pdp_trust_assets.py::test_final_data_cleaning_converts_eu4_usd_prices_to_eur tests/validate_pdp_trust_assets.py::test_final_data_cleaning_normalizes_new_product_30d_flag -q
```

Expected: FAIL because mixed price semantics and `new_product_context` are not implemented yet.

---

### Task 5: Implement Mixed Price Semantics And New-Product Flag

**Files:**
- Modify: `/Users/bytedance/pdp-trust-score_EU4-UK/code_nodes/final_data_cleaning_pdp_trust_v1.py`
- Test: `/Users/bytedance/pdp-trust-score_EU4-UK/tests/validate_pdp_trust_assets.py`

- [ ] **Step 1: Replace price constants**

Set these constants near the top of `final_data_cleaning_pdp_trust_v1.py`:

```python
SUPPORTED_TARGET_COUNTRIES = {"UK", "DE", "FR", "ES", "IT"}
TARGET_CURRENCY_BY_COUNTRY = {
    "UK": "GBP",
    "DE": "EUR",
    "FR": "EUR",
    "ES": "EUR",
    "IT": "EUR",
}
USD_TO_EUR = 0.86453
EXCHANGE_RATE_DATE = "2026-08-14"
EXCHANGE_RATE_SOURCE = "Frankfurter API"
```

- [ ] **Step 2: Replace `build_localized_price_fields`**

Replace the existing function with:

```python
def build_localized_price_fields(params):
    target_country = normalize_target_country(params)
    sales_price = parse_float(get_text(params, "sales_price"))
    list_price_usd = parse_float(get_text(params, "list_price_usd"))
    shipping_fee = parse_float(get_text(params, "shipping_fee"))
    landed_input = None
    if sales_price is not None or shipping_fee is not None:
        landed_input = (sales_price or 0.0) + (shipping_fee or 0.0)

    if target_country not in SUPPORTED_TARGET_COUNTRIES:
        return {
            "currency": "UNSUPPORTED",
            "target_country": target_country,
            "target_currency": "UNSUPPORTED",
            "exchange_rate_to_target_currency": "",
            "exchange_rate_date": EXCHANGE_RATE_DATE,
            "sales_price_local": "",
            "shipping_fee_local": "",
            "landed_cost_local": "",
            "price_input_semantics": "unsupported target_country; no price conversion applied",
            "localized_price_context": (
                f"unsupported target_country={target_country or 'missing'}; "
                "supported values are UK, DE, FR, ES, IT; no fallback to UK"
            ),
        }

    if target_country == "UK":
        context_parts = [
            "target_country=UK",
            "input_currency=GBP",
            "target_currency=GBP",
            "price_input_semantics=UK sales_price and shipping_fee are native GBP; no conversion applied",
        ]
        if sales_price is not None:
            context_parts.append(f"sales_price={format_money(sales_price)} GBP")
        if shipping_fee is not None:
            context_parts.append(f"shipping_fee={format_money(shipping_fee)} GBP")
        if landed_input is not None:
            context_parts.append(f"landed_cost={format_money(landed_input)} GBP")
        if list_price_usd is not None:
            context_parts.append(f"list_price_usd={format_money(list_price_usd)} USD anchor only")
        return {
            "currency": "GBP",
            "target_country": target_country,
            "target_currency": "GBP",
            "exchange_rate_to_target_currency": "",
            "exchange_rate_date": "",
            "sales_price_local": format_money(sales_price),
            "shipping_fee_local": format_money(shipping_fee),
            "landed_cost_local": format_money(landed_input),
            "price_input_semantics": "UK sales_price and shipping_fee are native GBP; no conversion applied",
            "localized_price_context": "; ".join(context_parts),
        }

    sales_local = None if sales_price is None else sales_price * USD_TO_EUR
    shipping_local = None if shipping_fee is None else shipping_fee * USD_TO_EUR
    landed_local = None if landed_input is None else landed_input * USD_TO_EUR
    context_parts = [
        f"target_country={target_country}",
        "input_currency=USD",
        "target_currency=EUR",
        "price_input_semantics=EU4 sales_price and shipping_fee are USD; converted to EUR",
        f"exchange_rate_source={EXCHANGE_RATE_SOURCE}",
        f"exchange_rate_date={EXCHANGE_RATE_DATE}",
        f"exchange_rate=1 USD to {format_money(USD_TO_EUR)} EUR",
    ]
    if sales_price is not None:
        context_parts.append(f"sales_price={format_money(sales_price)} USD -> {format_money(sales_local)} EUR")
    if shipping_fee is not None:
        context_parts.append(f"shipping_fee={format_money(shipping_fee)} USD -> {format_money(shipping_local)} EUR")
    if landed_input is not None:
        context_parts.append(f"landed_cost={format_money(landed_input)} USD -> {format_money(landed_local)} EUR")
    if list_price_usd is not None:
        context_parts.append(f"list_price_usd={format_money(list_price_usd)} USD anchor only")
    return {
        "currency": "USD",
        "target_country": target_country,
        "target_currency": "EUR",
        "exchange_rate_to_target_currency": str(USD_TO_EUR),
        "exchange_rate_date": EXCHANGE_RATE_DATE,
        "sales_price_local": format_money(sales_local),
        "shipping_fee_local": format_money(shipping_local),
        "landed_cost_local": format_money(landed_local),
        "price_input_semantics": "EU4 sales_price and shipping_fee are USD; converted to EUR",
        "localized_price_context": "; ".join(context_parts),
    }
```

- [ ] **Step 3: Add new-product helpers**

Add these functions after `parse_bool_flag`:

```python
def normalize_bool_marker(value):
    parsed = parse_bool_flag(value)
    return "true" if parsed is True else "false"


def build_new_product_context(params):
    is_new = normalize_bool_marker(get_text(params, "is_new_product_30d"))
    sales_count = parse_float(get_text(params, "cl_pay_sub_order_cnt"))
    low_sales = is_new == "true" and sales_count is not None and sales_count < 10
    sales_text = get_text(params, "cl_pay_sub_order_cnt") or "missing"
    return {
        "is_new_product_30d": is_new,
        "new_product_context": (
            f"is_new_product_30d={is_new}; "
            f"cl_pay_sub_order_cnt={sales_text}; "
            f"new_product_low_sales={'yes' if low_sales else 'no'}"
        ),
    }
```

- [ ] **Step 4: Update `build_output` to use the new fields**

In `build_output`, after `localized_price_fields = build_localized_price_fields(params)`, add:

```python
new_product_fields = build_new_product_context(params)
```

Change `"currency": "USD",` to:

```python
"currency": localized_price_fields["currency"],
```

Add:

```python
"price_input_semantics": localized_price_fields["price_input_semantics"],
"is_new_product_30d": new_product_fields["is_new_product_30d"],
"new_product_context": new_product_fields["new_product_context"],
```

- [ ] **Step 5: Run price and new-product tests**

Run:

```bash
python3 -m pytest tests/validate_pdp_trust_assets.py::test_final_data_cleaning_uses_native_gbp_for_uk_prices tests/validate_pdp_trust_assets.py::test_final_data_cleaning_converts_eu4_usd_prices_to_eur tests/validate_pdp_trust_assets.py::test_final_data_cleaning_normalizes_new_product_30d_flag -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

Run:

```bash
git add code_nodes/final_data_cleaning_pdp_trust_v1.py tests/validate_pdp_trust_assets.py
git commit -m "feat: support merged UK EU4 price semantics"
```

Expected: commit succeeds.

---

### Task 6: Add Failing Tests For Rulebook And Prompt Contracts

**Files:**
- Modify: `/Users/bytedance/pdp-trust-score_EU4-UK/tests/validate_pdp_trust_assets.py`

- [ ] **Step 1: Replace old locale schema assertions**

In `test_structured_rules_schema`, replace assertions that expect `locale == "UK"` or `"British" in data["goal"]` with:

```python
assert data["locale"] == "merged_uk_eu4_target_country"
assert "UK, DE, FR, ES, IT" in data["goal"]
assert set(data["locale_profiles"]) == SUPPORTED_TARGET_COUNTRIES
for country, expected_currency in EXPECTED_TARGET_CURRENCIES.items():
    profile = data["locale_profiles"][country]
    assert profile["target_currency"] == expected_currency
    assert profile["primary_language"]
    assert profile["buyer_persona"]
```

- [ ] **Step 2: Add rule text contract tests**

Add:

```python
def test_rulebook_contains_strict_localization_and_new_product_rules():
    structured = json.loads((ROOT / "rules/pdp_trust_rules_structured_v1.json").read_text())
    compressed = (ROOT / "rules/pdp_trust_rules_compressed_v1.txt").read_text()
    combined_rules = json.dumps(structured, ensure_ascii=False) + "\n" + compressed
    assert "page_quality <= 3" in combined_rules
    assert "size_chart_images" in combined_rules
    assert "product_main_images" in combined_rules
    assert "target-country primary language" in combined_rules
    assert "is_new_product_30d" in combined_rules
    assert "cl_pay_sub_order_cnt < 10" in combined_rules
    assert "shop_sales" in combined_rules
    assert "shop_fans" in combined_rules
    assert "shop_final_score" in combined_rules
    assert "score 3 is not a harmless neutral value" in combined_rules
```

- [ ] **Step 3: Add prompt variable contract tests**

Add:

```python
def test_prompts_include_new_visual_attribute_and_new_product_inputs():
    system_text = (ROOT / "prompts/trust_evaluator_system_prompt_v1.txt").read_text()
    user_text = (ROOT / "prompts/trust_evaluator_user_prompt_v1.txt").read_text()
    combined = system_text + "\n" + user_text
    for required in [
        "{{product_main_images}}",
        "{{size_chart_images}}",
        "{{product_attributes_text}}",
        "{{image_manifest}}",
        "{{price_input_semantics}}",
        "{{is_new_product_30d}}",
        "{{new_product_context}}",
        "{{visual_evidence_context}}",
    ]:
        assert required in combined
    assert "page_quality <= 3" in combined
    assert "主图" in combined
    assert "尺码图" in combined
    assert "长图" in combined
    assert "新品" in combined
    assert "3 分不是普通中性分" in combined
```

- [ ] **Step 4: Run the new contract tests and confirm they fail**

Run:

```bash
python3 -m pytest tests/validate_pdp_trust_assets.py::test_structured_rules_schema tests/validate_pdp_trust_assets.py::test_rulebook_contains_strict_localization_and_new_product_rules tests/validate_pdp_trust_assets.py::test_prompts_include_new_visual_attribute_and_new_product_inputs -q
```

Expected: FAIL because the rulebook and prompts still reflect the old language tolerance and do not expose all new variables.

---

### Task 7: Update Rulebook For Merged UK+EU4 vNext

**Files:**
- Modify: `/Users/bytedance/pdp-trust-score_EU4-UK/rules/pdp_trust_rules_structured_v1.json`
- Modify: `/Users/bytedance/pdp-trust-score_EU4-UK/rules/pdp_trust_rules_compressed_v1.txt`
- Test: `/Users/bytedance/pdp-trust-score_EU4-UK/tests/validate_pdp_trust_assets.py`

- [ ] **Step 1: Update structured rulebook metadata**

Set these top-level fields in `rules/pdp_trust_rules_structured_v1.json`:

```json
{
  "project": "pdp-trust-score_EU4-UK",
  "version": "2026-09-20-vnext",
  "locale": "merged_uk_eu4_target_country",
  "goal": "Score TikTok Shop PDP purchase trust from the viewpoint of the local buyer indicated by target_country across UK, DE, FR, ES, IT."
}
```

Update `locale_profiles` so each profile includes:

```json
{
  "buyer_persona": "local TikTok Shop shopper string",
  "primary_language": "target country primary language",
  "target_currency": "GBP or EUR",
  "price_input_semantics": "UK native GBP or EU4 USD converted to EUR",
  "strict_language_rule": "Core PDP information should be localized into the target-country primary language. Large-scale non-localized core text across title, product_main_images, size_chart_images, product_desc, or attributes caps page_quality at 3."
}
```

- [ ] **Step 2: Add structured rules for localization and new-product behavior**

Append these rule objects to the `rules` array:

```json
{
  "id": "LOCALIZE-01",
  "name": "Strict target-country language cap",
  "category": "page_quality",
  "applies_to": ["all"],
  "text": "Use the target-country primary language strictly: UK English, DE German, FR French, ES Spanish, IT Italian. If product title, product_main_images, size_chart_images, product_desc, or product_attributes_text contain large-scale core information in a non-target primary language without equivalent localized translation, page_quality <= 3. Do not apply this cap to brand names, model names, international units, small decorative words, or isolated non-critical labels."
}
```

```json
{
  "id": "LOCALIZE-02",
  "name": "Long-image description localization",
  "category": "page_quality",
  "applies_to": ["all"],
  "text": "If product_desc text is empty but product_main_images contain readable long-image product descriptions, use those images as PDP description evidence. If those long-image descriptions carry core product information but are not localized into the target-country primary language, page_quality <= 3. For size, safety, ingredients, material, compatibility, or usage-critical goods, non-localized long-image descriptions usually place page_quality in the 2 to 3 range."
}
```

```json
{
  "id": "LOCALIZE-03",
  "name": "Size chart localization",
  "category": "page_quality",
  "applies_to": ["apparel", "shoes", "accessories", "child", "pet", "furniture", "protective equipment", "all"],
  "text": "size_chart_images are fit evidence and language-localization evidence. If size or fit matters and the size chart is not in the target-country primary language or lacks equivalent localized translation, page_quality <= 3. For size-sensitive goods, unreadable or non-localized size charts can lower page_quality further within the 2 to 3 range."
}
```

```json
{
  "id": "NEW-01",
  "name": "Thirty-day new product low-sales tolerance",
  "category": "review_logic",
  "applies_to": ["all"],
  "text": "When is_new_product_30d=true and cl_pay_sub_order_cnt < 10, do not mechanically lower quality because product-level sales or reviews are sparse. Reduce product review-history weight and rely more on shop_sales, shop_fans, shop_final_score, official/channel evidence, page completeness, product_attributes_text, product_main_images, and size_chart_images. This does not override safety, compliance, Stage 1 red flags, misleading or wrong-item evidence, IPR risk, visible product/spec conflict, or negative review_contents when present."
}
```

```json
{
  "id": "NEW-02",
  "name": "No historical sales or reviews quality default",
  "category": "review_logic",
  "applies_to": ["all"],
  "text": "For products with no historical sales or review evidence, quality should rely more on shop_final_score, shop_sales, shop_fans, official/channel evidence, page completeness, and product attributes. If evidence is neutral and no clear risk appears, quality should default to 4 rather than being mechanically held at 3. High-sensitivity categories, weak shops, incomplete pages, safety concerns, compliance concerns, IPR risk, and strong PDP inconsistency can still justify lower quality and lower final score."
}
```

- [ ] **Step 3: Update the compressed rulebook**

In `rules/pdp_trust_rules_compressed_v1.txt`, replace old broad language tolerance with this text:

```text
Strict target-country language rule
Use the target-country primary language strictly: UK English, DE German, FR French, ES Spanish, IT Italian. Check product title, product_main_images, size_chart_images, product_desc text, and product_attributes_text. If core PDP information is mostly or materially in a non-target primary language and lacks equivalent localized translation, page_quality <= 3. Core information includes product identity, material, composition, size, fit, quantity, compatibility, usage, safety warnings, warranty, return, delivery restrictions, region restrictions, expiry, and digital redemption steps. Brand names, model names, international units, small decorative words, short universal words, single SKU labels, and isolated non-critical packaging text do not trigger the cap by themselves.

Long-image description rule
product_main_images may contain long detail images. If product_desc text is empty but product_main_images contain readable and complete product information, use those images as PDP description evidence. If the long-image description is not localized into the target-country primary language, page_quality <= 3. If size, safety, ingredients, material, compatibility, or usage depends on that long image and it is not locally understandable, page_quality usually sits at 2 or 3.

Size chart localization
size_chart_images are both fit evidence and language-localization evidence. If size or fit matters and the size chart is not localized into the target-country primary language, page_quality <= 3. For clothing, shoes, accessories with fit constraints, child goods, pet goods, furniture, protective equipment, and other size-sensitive goods, unreadable or non-localized size charts can push page_quality further down within 2 to 3.

New-product quality reliability
When is_new_product_30d=true and cl_pay_sub_order_cnt < 10, reduce product review-history weight. Do not mechanically lower quality only because product-level sales or reviews are sparse. Instead, weigh shop_sales, shop_fans, shop_final_score, official/channel evidence, page completeness, product_attributes_text, product_main_images, and size_chart_images more heavily. This rule does not override safety, compliance, Stage 1 red flags, misleading or wrong-item evidence, IPR or authorization risk, visible product/spec conflict, or negative review_contents when present. For no historical sales or review evidence, if evidence is neutral and no clear risk appears, quality should default to 4 rather than being mechanically held at 3.

Traffic-control tier reminder
The final score maps to business control tiers: 1/2 = policy filtering tier, 3 = deboost traffic-control tier, 4/5 = no control tier. Score 3 is not a harmless neutral value. Require clear evidence before moving a product from 4/5 to 3, and stronger evidence before moving it to 1/2.
```

- [ ] **Step 4: Run rulebook tests**

Run:

```bash
python3 -m pytest tests/validate_pdp_trust_assets.py::test_structured_rules_schema tests/validate_pdp_trust_assets.py::test_rulebook_contains_strict_localization_and_new_product_rules -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

Run:

```bash
git add rules tests/validate_pdp_trust_assets.py
git commit -m "feat: add merged UK EU4 rulebook contracts"
```

Expected: commit succeeds.

---

### Task 8: Add Failing Tests For Rules_Brain Context Outputs

**Files:**
- Modify: `/Users/bytedance/pdp-trust-score_EU4-UK/tests/validate_pdp_trust_assets.py`

- [ ] **Step 1: Add a test for strict localization context**

Add:

```python
def test_rules_brain_emits_visual_localization_context():
    namespace = load_code_node("code_nodes/rules_brain_pdp_trust_v1.py")
    rules = json.loads((ROOT / "rules/pdp_trust_rules_structured_v1.json").read_text())
    output = namespace["build_output"](
        {
            "rules_json": rules,
            "product_id": "locale-fr",
            "product_name": "English only dress",
            "first_category_name": "Womenswear",
            "target_country": "FR",
            "target_currency": "EUR",
            "product_main_images": ["https://example.com/main.jpeg", "https://example.com/long.jpeg"],
            "size_chart_images": ["https://example.com/size.jpeg"],
            "image_manifest": "product_main_images_count=2; size_chart_images_count=1",
            "product_attributes_text": "Material=Polyester; Washing instructions=Machine wash",
            "localized_price_context": "target_country=FR; input_currency=USD; target_currency=EUR",
        }
    )
    assert "visual_evidence_context" in output
    assert "product_main_images_count=2" in output["visual_evidence_context"]
    assert "size_chart_images_count=1" in output["visual_evidence_context"]
    assert "strict_language_check=title, product_main_images, size_chart_images, product_desc, product_attributes_text" in output["locale_context"]
    assert "primary_language=French" in output["locale_context"]
    assert "LOCALIZE-01" in output["matched_rules"]
    assert "LOCALIZE-02" in output["matched_rules"]
    assert "LOCALIZE-03" in output["matched_rules"]
```

- [ ] **Step 2: Add a test for new-product context**

Add:

```python
def test_rules_brain_emits_new_product_context():
    namespace = load_code_node("code_nodes/rules_brain_pdp_trust_v1.py")
    rules = json.loads((ROOT / "rules/pdp_trust_rules_structured_v1.json").read_text())
    output = namespace["build_output"](
        {
            "rules_json": rules,
            "product_id": "new-product-rules",
            "product_name": "New low sales item",
            "first_category_name": "Home Supplies",
            "target_country": "DE",
            "is_new_product_30d": "true",
            "new_product_context": "is_new_product_30d=true; cl_pay_sub_order_cnt=9; new_product_low_sales=yes",
            "cl_pay_sub_order_cnt": "9",
            "shop_sales": "20000",
            "shop_fans": "5000",
            "shop_final_score": "4.7",
        }
    )
    assert "new_product_context" in output
    assert "new_product_low_sales=yes" in output["new_product_context"]
    assert "NEW-01" in output["matched_rules"]
    assert "NEW-02" in output["matched_rules"]
    assert "shop_sales=20000" in output["new_product_context"]
    assert "shop_fans=5000" in output["new_product_context"]
    assert "shop_final_score=4.7" in output["new_product_context"]
```

- [ ] **Step 3: Run tests and confirm they fail**

Run:

```bash
python3 -m pytest tests/validate_pdp_trust_assets.py::test_rules_brain_emits_visual_localization_context tests/validate_pdp_trust_assets.py::test_rules_brain_emits_new_product_context -q
```

Expected: FAIL because `visual_evidence_context` and the new-product Rules Brain output are not implemented yet.

---

### Task 9: Implement Rules_Brain Context Outputs

**Files:**
- Modify: `/Users/bytedance/pdp-trust-score_EU4-UK/code_nodes/rules_brain_pdp_trust_v1.py`
- Test: `/Users/bytedance/pdp-trust-score_EU4-UK/tests/validate_pdp_trust_assets.py`

- [ ] **Step 1: Parse image-array context in `collect_pdp`**

Add fields to the dict returned by `collect_pdp`:

```python
"product_main_images": text_param(params, "product_main_images"),
"size_chart_images": text_param(params, "size_chart_images"),
"image_manifest": text_param(params, "image_manifest"),
"product_attributes_text": text_param(params, "product_attributes_text"),
"is_new_product_30d": text_param(params, "is_new_product_30d"),
"new_product_context": text_param(params, "new_product_context"),
"shop_sales": text_param(params, "shop_sales"),
"shop_fans": text_param(params, "shop_fans"),
"shop_final_score": text_param(params, "shop_final_score"),
```

- [ ] **Step 2: Add locale and visual context builders**

Add:

```python
def build_locale_context(rules, pdp):
    target_country = (pdp.get("target_country") or "").upper()
    profiles = rules.get("locale_profiles") or {}
    profile = profiles.get(target_country) or {}
    primary_language = profile.get("primary_language", "unsupported")
    buyer_persona = profile.get("buyer_persona", "unsupported target-country buyer")
    target_currency = pdp.get("target_currency") or profile.get("target_currency", "")
    return "; ".join(
        [
            f"target_country={target_country or 'missing'}",
            f"buyer_persona={buyer_persona}",
            f"primary_language={primary_language}",
            f"target_currency={target_currency or 'missing'}",
            "strict_language_check=title, product_main_images, size_chart_images, product_desc, product_attributes_text",
            "page_quality_cap_rule=large-scale non-localized core PDP information without translation means page_quality <= 3",
        ]
    )


def count_listish(value):
    parsed = None
    if isinstance(value, str) and value.strip().startswith("["):
        try:
            parsed = json.loads(value)
        except Exception:
            parsed = None
    if isinstance(parsed, list):
        return len(parsed)
    if isinstance(value, list):
        return len(value)
    text = str(value or "")
    if not text:
        return 0
    return text.count("http://") + text.count("https://")


def build_visual_evidence_context(pdp):
    main_count = count_listish(pdp.get("product_main_images"))
    size_count = count_listish(pdp.get("size_chart_images"))
    return "; ".join(
        [
            f"product_main_images_count={main_count}",
            f"size_chart_images_count={size_count}",
            f"image_manifest={pdp.get('image_manifest') or 'missing'}",
            "product_main_images may include ordinary main images and long detail images",
            "size_chart_images are size evidence and localization-language evidence",
        ]
    )


def build_new_product_context_from_pdp(pdp):
    base = pdp.get("new_product_context") or "is_new_product_30d=false; new_product_low_sales=no"
    return "; ".join(
        [
            base,
            f"shop_sales={pdp.get('shop_sales') or 'missing'}",
            f"shop_fans={pdp.get('shop_fans') or 'missing'}",
            f"shop_final_score={pdp.get('shop_final_score') or 'missing'}",
            "quality_weighting=if confirmed 30-day new product with sales < 10, reduce product review-history weight and use shop metrics plus page evidence more heavily",
        ]
    )
```

- [ ] **Step 3: Ensure rules route for localization and new-product IDs**

In `infer_tags`, always add:

```python
tags.update(["strict_localization", "long_image_description", "size_chart_localization"])
```

When `pdp.get("new_product_context")` contains `new_product_low_sales=yes`, add:

```python
tags.update(["new_product_low_sales", "new_product_quality_tolerance"])
```

Make sure the new structured rules have matching `applies_to` terms:

```text
strict_localization
long_image_description
size_chart_localization
new_product_low_sales
new_product_quality_tolerance
```

- [ ] **Step 4: Add outputs in `build_output`**

In the returned dict from `build_output`, include:

```python
"locale_context": build_locale_context(rules, pdp),
"visual_evidence_context": build_visual_evidence_context(pdp),
"new_product_context": build_new_product_context_from_pdp(pdp),
```

Keep existing outputs: `rules_context`, `matched_rules`, `risk_hints`, `evidence_gaps`, `review_context`, `price_context`, `rules_version`, `rules_source_warning`, `pdp_debug_summary`.

- [ ] **Step 5: Run Rules_Brain tests**

Run:

```bash
python3 -m pytest tests/validate_pdp_trust_assets.py::test_rules_brain_emits_visual_localization_context tests/validate_pdp_trust_assets.py::test_rules_brain_emits_new_product_context -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

Run:

```bash
git add code_nodes/rules_brain_pdp_trust_v1.py tests/validate_pdp_trust_assets.py
git commit -m "feat: add visual and new product rules context"
```

Expected: commit succeeds.

---

### Task 10: Add Failing Tests For Context_Builder And Prompt Wiring

**Files:**
- Modify: `/Users/bytedance/pdp-trust-score_EU4-UK/tests/validate_pdp_trust_assets.py`

- [ ] **Step 1: Add Context_Builder propagation test**

Add:

```python
def test_context_builder_propagates_new_visual_and_new_product_context():
    namespace = load_code_node("code_nodes/context_builder_pdp_trust_v1.py")
    output = namespace["build_output"](
        {
            "product_id": "ctx-case",
            "product_name": "Context Case",
            "target_country": "IT",
            "target_currency": "EUR",
            "product_main_images": ["https://example.com/main-1.jpeg", "https://example.com/main-2.jpeg"],
            "size_chart_images": ["https://example.com/size.jpeg"],
            "image_manifest": "product_main_images_count=2; size_chart_images_count=1",
            "product_attributes_text": "Material=Cotton; Size=M",
            "is_new_product_30d": "true",
            "new_product_context": "is_new_product_30d=true; cl_pay_sub_order_cnt=5; new_product_low_sales=yes",
            "visual_evidence_context": "product_main_images_count=2; size_chart_images_count=1",
            "locale_context": "target_country=IT; primary_language=Italian; page_quality_cap_rule=page_quality <= 3",
        }
    )
    combined = "\n".join(output.values())
    assert "product_main_images_count=2" in combined
    assert "size_chart_images_count=1" in combined
    assert "Material=Cotton" in combined
    assert "new_product_low_sales=yes" in combined
    assert "primary_language=Italian" in combined
    assert "page_quality <= 3" in combined
```

- [ ] **Step 2: Run the Context_Builder and prompt contract tests and confirm they fail**

Run:

```bash
python3 -m pytest tests/validate_pdp_trust_assets.py::test_context_builder_propagates_new_visual_and_new_product_context tests/validate_pdp_trust_assets.py::test_prompts_include_new_visual_attribute_and_new_product_inputs -q
```

Expected: FAIL because Context_Builder and prompts do not yet include all new context fields.

---

### Task 11: Update Context_Builder And Trust_Evaluator Prompts

**Files:**
- Modify: `/Users/bytedance/pdp-trust-score_EU4-UK/code_nodes/context_builder_pdp_trust_v1.py`
- Modify: `/Users/bytedance/pdp-trust-score_EU4-UK/prompts/trust_evaluator_system_prompt_v1.txt`
- Modify: `/Users/bytedance/pdp-trust-score_EU4-UK/prompts/trust_evaluator_user_prompt_v1.txt`
- Test: `/Users/bytedance/pdp-trust-score_EU4-UK/tests/validate_pdp_trust_assets.py`

- [ ] **Step 1: Update Context_Builder image parsing**

In `context_builder_pdp_trust_v1.py`, update `build_output` so it reads:

```python
product_main_images = parse_images(find_param(params, ("product_main_images",)))
size_chart_images = parse_images(find_param(params, ("size_chart_images",)))
images = parse_images(find_param(params, ("images", "Product_images", "product_images")))
if not images:
    images = product_main_images + size_chart_images
```

Pass `product_main_images` and `size_chart_images` into helper functions or read them directly inside helpers with `get_text`.

- [ ] **Step 2: Add new fields to `build_case_state`**

Append these lines to the `parts` list in `build_case_state`:

```python
f"product_main_images_count={len(parse_images(find_param(params, ('product_main_images',))))}",
f"size_chart_images_count={len(parse_images(find_param(params, ('size_chart_images',))))}",
f"product_attributes_present={yes_no(has_text(params, 'product_attributes_text'))}",
f"is_new_product_30d={get_text(params, 'is_new_product_30d') or 'false'}",
f"new_product_context={trim(get_text(params, 'new_product_context'), 260) or 'missing'}",
```

- [ ] **Step 3: Add new fields to `build_evidence_manifest`**

Append these manifest rows:

```python
f"image_manifest={trim(get_text(params, 'image_manifest'), 500) or 'missing'}",
f"visual_evidence_context={trim(get_text(params, 'visual_evidence_context'), 700) or 'missing'}",
f"product_attributes_text={trim(get_text(params, 'product_attributes_text'), 700) or 'missing'}",
f"new_product_context={trim(get_text(params, 'new_product_context'), 500) or 'missing'}",
```

- [ ] **Step 4: Add new checklist reminders**

Append to `build_decision_checklist`:

```python
"12. Strict localization: check title, product_main_images, size_chart_images, product_desc, and product_attributes_text. Large-scale non-target primary language without translation means page_quality <= 3.",
"13. Long-image descriptions inside product_main_images can count as description evidence, but non-localized core long-image descriptions still cap page_quality at 3.",
"14. Size chart images are fit evidence and localization evidence; non-localized size charts for size-sensitive goods cap page_quality at 3.",
"15. New product tolerance: if is_new_product_30d=true and cl_pay_sub_order_cnt < 10, reduce product review-history weight and lean on shop_sales, shop_fans, shop_final_score, page evidence, attributes, and images.",
"16. Traffic tiers: score 3 is a deboost tier, so downgrading from 4/5 to 3 requires clear evidence.",
```

- [ ] **Step 5: Update system prompt**

In `prompts/trust_evaluator_system_prompt_v1.txt`, replace the old language paragraph:

```text
Target-country PDPs may contain multiple European languages. Non-local language is not a negative signal by itself. Penalize language only when it blocks the target-country buyer from understanding core specs, safety, warranty, return, compatibility, region, expiry, or redemption information. Use locale_context for the primary language and tolerated-language expectations.
```

with:

```text
Strict localization rule
Use the target-country primary language strictly: UK English, DE German, FR French, ES Spanish, IT Italian. Check product_name/title, product_main_images readable text, size_chart_images readable text, product_desc text, and product_attributes_text. If core PDP information is mostly or materially in a non-target primary language and lacks equivalent target-language translation, page_quality <= 3. Brand names, model names, international units, small decorative words, and isolated non-critical labels do not trigger the cap by themselves.
```

Add these prompt variables after `Localized Price Context`:

```text
Price Input Semantics
{{price_input_semantics}}

Product Main Images
{{product_main_images}}

Size Chart Images
{{size_chart_images}}

Image Manifest
{{image_manifest}}

Product Attributes
{{product_attributes_text}}

Visual Evidence Context
{{visual_evidence_context}}

New Product Context
{{new_product_context}}
```

Add this paragraph near review guidance:

```text
New-product quality reliability
If is_new_product_30d=true and cl_pay_sub_order_cnt < 10, do not mechanically lower quality only because product-level sales or reviews are sparse. Reduce product review-history weight and rely more on shop_sales, shop_fans, shop_final_score, official or channel evidence, page completeness, product_attributes_text, product_main_images, and size_chart_images. This tolerance never overrides safety, compliance, Stage 1 red flags, clear misleading or wrong-item evidence, IPR risk, visible product/spec conflicts, or negative review_contents when present.
```

Add this traffic-tier paragraph near boundary calibration:

```text
Traffic-control tier reminder
The final score maps to business controls: 1/2 goes to policy filtering, 3 triggers deboost traffic control, and 4/5 receives no control. Score 3 is not a harmless neutral value. Require clear evidence before downgrading from 4/5 to 3, and stronger evidence before assigning 1/2.
```

- [ ] **Step 6: Update user prompt**

In `prompts/trust_evaluator_user_prompt_v1.txt`, under PDP visible inputs, replace the old image lines with:

```text
product_main_images: {{product_main_images}}
size_chart_images: {{size_chart_images}}
image_manifest: {{image_manifest}}
images_combined_for_visual_binding: {{images}}
Image source note: product_main_images are all ProductMeta.images returned by RPC and may include ordinary main images, long detail images, selling-point images, package/spec images, and product description images. size_chart_images are separate size-chart evidence. If Aicolate binds only one image array, images contains product_main_images followed by size_chart_images.
```

Add under product attributes:

```text
product_attributes_text: {{product_attributes_text}}
```

Add under quality/reviews:

```text
is_new_product_30d: {{is_new_product_30d}}
new_product_context: {{new_product_context}}
```

Add under price:

```text
price_input_semantics: {{price_input_semantics}}
```

Add under Rules Brain summary fields:

```text
visual_evidence_context: {{visual_evidence_context}}
```

Add this required analysis item before final conclusion:

```text
本地化页面语言检查：严格按 target_country 主语言判断。必须检查标题、product_main_images 中的可读文字、size_chart_images 中的可读文字、product_desc、product_attributes_text。若核心信息大规模非本地化且无等价翻译，页面呈现质量 page_quality <= 3。长图详描可作为说明证据，但没有本地化翻译也要触发 page_quality <= 3。尺码图也纳入同一规则。
```

Add this required analysis item in quality reliability:

```text
新品宽容度检查：如果 is_new_product_30d=true 且 cl_pay_sub_order_cnt < 10，说明商品历史销评权重降低，质量可靠性更多参考 shop_sales、shop_fans、shop_final_score、官方/渠道、页面完整度、product_attributes_text、product_main_images、size_chart_images。若没有明确风险，quality 可默认 4；但安全、合规、误导、IPR、图文冲突或 review_contents 中的真实负面问题不能被新品宽容覆盖。
```

Add:

```text
3 分不是普通中性分，而是 deboost 流控档。把商品从 4/5 降到 3 时必须说明清晰证据；把商品降到 1/2 时必须说明策略过滤级风险。
```

- [ ] **Step 7: Run Context_Builder and prompt tests**

Run:

```bash
python3 -m pytest tests/validate_pdp_trust_assets.py::test_context_builder_propagates_new_visual_and_new_product_context tests/validate_pdp_trust_assets.py::test_prompts_include_new_visual_attribute_and_new_product_inputs -q
```

Expected: PASS.

- [ ] **Step 8: Commit**

Run:

```bash
git add code_nodes/context_builder_pdp_trust_v1.py prompts tests/validate_pdp_trust_assets.py
git commit -m "feat: wire merged evaluator prompt context"
```

Expected: commit succeeds.

---

### Task 12: Add Documentation And Aicolate Wiring Checklist

**Files:**
- Create: `/Users/bytedance/pdp-trust-score_EU4-UK/docs/overview.md`
- Create: `/Users/bytedance/pdp-trust-score_EU4-UK/docs/wiring-checklist.md`
- Modify: `/Users/bytedance/pdp-trust-score_EU4-UK/tests/validate_pdp_trust_assets.py`

- [ ] **Step 1: Add docs existence tests**

Add:

```python
def test_docs_describe_new_repo_and_aicolate_outputs():
    overview = (ROOT / "docs/overview.md").read_text()
    wiring = (ROOT / "docs/wiring-checklist.md").read_text()
    combined = overview + "\n" + wiring
    assert "pdp-trust-score_EU4-UK" in combined
    assert "https://github.com/danielwanyan/pdp-trust-score_EU4-UK" in combined
    for field in [
        "product_main_images",
        "size_chart_images",
        "product_attributes_text",
        "image_manifest",
        "price_input_semantics",
        "is_new_product_30d",
        "new_product_context",
        "visual_evidence_context",
    ]:
        assert field in combined
    assert "Output Panel" in wiring
    assert "rules_text_fetch" in wiring
    assert "rules_json_fetch" in wiring
```

- [ ] **Step 2: Run docs test and confirm it fails**

Run:

```bash
python3 -m pytest tests/validate_pdp_trust_assets.py::test_docs_describe_new_repo_and_aicolate_outputs -q
```

Expected: FAIL because `docs/overview.md` and `docs/wiring-checklist.md` do not exist yet.

- [ ] **Step 3: Create `docs/overview.md`**

Create the file with:

````markdown
# PDP Trust Score EU4+UK

This repository contains the isolated UK+EU4 merged PDP Trust Score Aicolate copybook.

GitHub repo:

```text
https://github.com/danielwanyan/pdp-trust-score_EU4-UK
```

The workflow evaluates one product per invocation with exactly one LLM node, `Trust_Evaluator`.

Supported target countries:

```text
UK, DE, FR, ES, IT
```

Key vNext changes:

- UK and EU4 share one merged `target_country` workflow with independent locale profiles.
- `product_image_rpc` preserves all `ProductMeta.images` as `product_main_images`.
- `product_extra_attributes_rpc` provides `product_attributes_text` and `size_chart_images`.
- Strict target-country language localization can cap `page_quality <= 3`.
- Long-image descriptions inside `product_main_images` can count as PDP description evidence, but non-localized core long-image text also caps `page_quality <= 3`.
- `size_chart_images` are included in localization-language checks.
- UK `sales_price` and `shipping_fee` are native GBP. EU4 `sales_price` and `shipping_fee` are USD and are converted to EUR.
- `is_new_product_30d=true` with `cl_pay_sub_order_cnt < 10` reduces product-review-history weight and shifts quality reliability toward shop metrics and page evidence.
- RESULT JSON keeps the existing field whitelist.

Traffic tiers:

```text
1/2 = policy filtering tier
3 = deboost traffic-control tier
4/5 = no control tier
```
````

- [ ] **Step 4: Create `docs/wiring-checklist.md`**

Create the file with the Aicolate checklist below:

````markdown
# PDP Trust Score EU4+UK Aicolate Wiring Checklist

## Start Inputs

Add or keep these fields:

```text
product_id: String
target_country: String
is_new_product_30d: String
product_name: String
brand_name: String
first_category_name: String
shop_name: String
product_desc: String
review_contents: String
comment_summary_text: String
comment_30d_emotion: String
is_official_tag: String
is_free_shipping_fee: String
has_flash_sale: String
is_free_return: String
sku_cnt: String
shop_sales: String
shop_fans: String
comment_cnt_td: String
cl_pay_sub_order_cnt: String
review_cnt_td: String
pv_rank: String
video_product_show_cnt: String
is_main_img_firstimg_quality: String
prd_basic_info_score: String
list_price_usd: String
sales_price: String
shop_final_score: String
avg_review_star_td: String
with_image_comment_ratio: String
avg_star_rating: String
shipping_fee: String
onnr15: String
onnr30: String
```

## RPC Nodes

`product_image_rpc` fetches `ProductMeta.images`.

Map into `Final_data_cleaning`:

```text
rpc_images = product_image_rpc.output
```

`product_extra_attributes_rpc` fetches:

```text
product_extra_attributes.product_attributes
product_extra_attributes.size_chart
```

Map into `Final_data_cleaning`:

```text
product_extra_attributes = product_extra_attributes_rpc.output
```

## HTTP Nodes

After pushing this repo, configure:

```text
rules_text_fetch:
https://raw.githubusercontent.com/danielwanyan/pdp-trust-score_EU4-UK/main/rules/pdp_trust_rules_compressed_v1.txt

rules_json_fetch:
https://raw.githubusercontent.com/danielwanyan/pdp-trust-score_EU4-UK/main/rules/pdp_trust_rules_structured_v1.json
```

## Final_data_cleaning Output Panel

Declare:

```text
product_id: String
product_name: String
product_main_images: Array<String>
size_chart_images: Array<String>
images: Array<String>
image_source: String
image_manifest: String
product_attributes_text: String
product_attributes_json: String
extra_attributes_source: String
product_desc: String
brand_name: String
first_category_name: String
sku_cnt: String
is_main_img_firstimg_quality: String
prd_basic_info_score: String
list_price_usd: String
sales_price: String
shipping_fee: String
currency: String
target_country: String
target_currency: String
exchange_rate_to_target_currency: String
exchange_rate_date: String
sales_price_local: String
shipping_fee_local: String
landed_cost_local: String
price_input_semantics: String
localized_price_context: String
is_new_product_30d: String
new_product_context: String
shop_name: String
is_official_tag: String
shop_final_score: String
shop_sales: String
shop_fans: String
comment_cnt_td: String
review_cnt_td: String
avg_review_star_td: String
avg_star_rating: String
review_contents: String
cl_pay_sub_order_cnt: String
with_image_comment_ratio: String
comment_summary_text: String
comment_30d_emotion: String
is_free_shipping_fee: String
has_flash_sale: String
is_free_return: String
onnr15: String
onnr30: String
shop_info: String
review_context: String
logistics_info: String
governance_metrics: String
final_data_cleaning_debug: String
```

## Rules_Brain Output Panel

Declare:

```text
rules_context: String
matched_rules: String
locale_context: String
visual_evidence_context: String
new_product_context: String
risk_hints: String
evidence_gaps: String
review_context: String
price_context: String
rules_version: String
rules_source_warning: String
pdp_debug_summary: String
```

## Context_Builder Output Panel

Declare:

```text
case_state: String
evidence_manifest: String
decision_checklist: String
context_builder_debug: String
```

## Trust_Evaluator Inputs

Use flat names only:

```text
body
rules_context
rules_review_context
price_context
locale_context
visual_evidence_context
new_product_context
risk_hints
evidence_gaps
case_state
evidence_manifest
decision_checklist
product_id
product_name
product_main_images
size_chart_images
images
image_manifest
product_attributes_text
product_desc
brand_name
first_category_name
sku_cnt
is_main_img_firstimg_quality
prd_basic_info_score
list_price_usd
sales_price
shipping_fee
currency
target_country
target_currency
price_input_semantics
localized_price_context
is_new_product_30d
shop_name
is_official_tag
shop_final_score
shop_sales
shop_fans
comment_cnt_td
review_cnt_td
avg_review_star_td
avg_star_rating
review_contents
cl_pay_sub_order_cnt
with_image_comment_ratio
comment_summary_text
comment_30d_emotion
is_free_shipping_fee
has_flash_sale
is_free_return
onnr15
onnr30
shop_info
review_context
logistics_info
governance_metrics
```
````

- [ ] **Step 5: Run docs test**

Run:

```bash
python3 -m pytest tests/validate_pdp_trust_assets.py::test_docs_describe_new_repo_and_aicolate_outputs -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

Run:

```bash
git add docs tests/validate_pdp_trust_assets.py
git commit -m "docs: add merged workflow wiring checklist"
```

Expected: commit succeeds.

---

### Task 13: Run Full Validation, Push, And Verify Raw URLs

**Files:**
- Read: all files created by previous tasks
- External target: `https://github.com/danielwanyan/pdp-trust-score_EU4-UK`

- [ ] **Step 1: Run full validation**

Run:

```bash
python3 -m pytest tests/validate_pdp_trust_assets.py -q
```

Expected: all tests pass.

- [ ] **Step 2: Check no forbidden placeholders or stale repo URLs remain**

Run:

```bash
rg -n 'TB[D]|TO[D]O|pdp-trust-score[/]main|European languages are not a negative signa[l]|first image onl[y]|detail[_]images' rules code_nodes prompts docs/overview.md docs/wiring-checklist.md tests
```

Expected: no matches.

- [ ] **Step 3: Check git status**

Run:

```bash
git status --short
```

Expected: clean working tree.

- [ ] **Step 4: Push to the new GitHub repo**

Run:

```bash
git push -u origin main
```

Expected: push succeeds to `danielwanyan/pdp-trust-score_EU4-UK`.

- [ ] **Step 5: Verify raw rule URLs**

Run:

```bash
curl -fsSL https://raw.githubusercontent.com/danielwanyan/pdp-trust-score_EU4-UK/main/rules/pdp_trust_rules_compressed_v1.txt | head -n 5
curl -fsSL https://raw.githubusercontent.com/danielwanyan/pdp-trust-score_EU4-UK/main/rules/pdp_trust_rules_structured_v1.json | python3 -m json.tool | head -n 20
```

Expected: first command prints the compressed rulebook header; second command prints valid formatted JSON including `"project": "pdp-trust-score_EU4-UK"`.

- [ ] **Step 6: Prepare Aicolate paste order for the user**

Report the exact paste order:

```text
1. Configure HTTP Request raw URLs to the new repo.
2. Paste Final_data_cleaning full code and update its Output Panel.
3. Paste Rules_Brain full code and update its Output Panel.
4. Paste Context_Builder full code and update its Output Panel.
5. Paste Trust_Evaluator System Prompt.
6. Paste Trust_Evaluator User Prompt.
7. Bind product_main_images and size_chart_images as visual inputs. If only one image array is supported, bind images and use image_manifest for source separation.
8. Run UK and EU4 smoke cases before batch execution.
```

Expected: final implementation response includes the raw URLs, validation command result, commit id, and exact files changed.

