import ast
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "rules/pdp_trust_rules_structured_v1.json",
    "rules/pdp_trust_rules_compressed_v1.txt",
    "code_nodes/final_data_cleaning_pdp_trust_v1.py",
    "code_nodes/rules_brain_pdp_trust_v1.py",
    "code_nodes/context_builder_pdp_trust_v1.py",
    "prompts/trust_evaluator_system_prompt_v1.txt",
    "prompts/trust_evaluator_user_prompt_v1.txt",
    "PDP-Trust-Score-Excel-Input-Mapping.md",
    "PDP-Trust-Score-Aicolate-Wiring-Checklist.md",
    "PDP-Trust-Score-Overview.md",
]

FORBIDDEN_INPUT_FIELDS = [
    "shop_positive_rate",
    "ontime_delivery_rate",
    "average_process_time",
    "customer_service_satisfaction_rate",
    "avatar_uri",
    "sku_name_list",
    "shop_idendity_type",
    "shop_identity_type",
    "star_ratings",
    "is_fast_refund",
]

FORBIDDEN_PROMPT_VARIABLES = [
    "{{title}}",
    "{{seller_name}}",
    "{{platform_badges}}",
    "{{product_category}}",
    "{{description}}",
    "{{sku}}",
    "{{specs}}",
    "{{price}}",
    "{{delivery_info}}",
    "{{rating}}",
    "{{review_count}}",
    "{{Product_images}}",
    "{{first_image}}",
]

FORBIDDEN_LOCALE_PHRASES = [
    "US online shopper",
    "US shopper",
    "US buyer",
    "US consumer",
    "US common-sense",
    "US common sense",
    "United States",
    "EU+UK",
    "European online shopper",
    "European shopper",
    "European consumer",
]

SYSTEM_PROMPTS = [
    "prompts/trust_evaluator_system_prompt_v1.txt",
]

FORBIDDEN_SYSTEM_SNIPPETS = ["```", "`", "**", "#", "|", "{{Product_images}}", "{{All_images}}"]

REQUIRED_SCORE_FIELDS = {
    "authenticity_delivery",
    "safety",
    "quality",
    "value",
    "compliance",
    "page_quality",
    "score",
}

ALLOWED_B_END_REASONS = [
    "正品、品牌或渠道可信度不足",
    "商品信息存在误导或货不对板风险",
    "安全风险",
    "内容合规或侵权风险",
    "履约或售后保障不足",
    "评分或评价表现偏弱",
    "质量问题集中",
    "页面关键信息或实物展示不足",
    "价格或到手价不具备竞争力",
    "低价异常导致不可信",
    "特殊商品关键信息披露不足",
]

SUPPORTED_TARGET_COUNTRIES = {"UK", "DE", "FR", "ES", "IT"}
EXPECTED_TARGET_CURRENCIES = {"UK": "GBP", "DE": "EUR", "FR": "EUR", "ES": "EUR", "IT": "EUR"}
USD_TO_EUR = "0.86453"
EXCHANGE_RATE_DATE = "2026-08-14"


def load_code_node(rel_path):
    code_path = ROOT / rel_path
    namespace = {"Args": object, "Output": dict}
    source = code_path.read_text()
    exec(compile(source, str(code_path), "exec"), namespace)
    return namespace


def test_required_files_exist():
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]
    assert not missing, f"missing required files: {missing}"


def test_structured_rules_schema():
    data = json.loads((ROOT / "rules/pdp_trust_rules_structured_v1.json").read_text())
    assert data["project"] == "pdp-trust-score_EU4-UK"
    assert data["version"] == "2026-09-20-vnext"
    assert data["locale"] == "merged_uk_eu4_target_country"
    assert "UK, DE, FR, ES, IT" in data["goal"]
    assert set(data["locale_profiles"]) == SUPPORTED_TARGET_COUNTRIES
    for target_country, expected_currency in EXPECTED_TARGET_CURRENCIES.items():
        profile = data["locale_profiles"][target_country]
        assert profile["target_currency"] == expected_currency
        assert profile["primary_language"]
        assert profile["buyer_persona"]
    assert data["score_fields"] == sorted(REQUIRED_SCORE_FIELDS)
    assert data["allowed_b_end_reasons"] == ALLOWED_B_END_REASONS
    rule_ids = {rule["id"] for rule in data["rules"]}
    for required in ["CORE-01", "STAGE1-05", "SPECIAL-06", "BEND-01"]:
        assert required in rule_ids
    for required in [
        "BOUNDARY-01",
        "BOUNDARY-02",
        "BOUNDARY-03",
        "BOUNDARY-04",
        "BOUNDARY-05",
        "BOUNDARY-06",
        "BOUNDARY-07",
        "BOUNDARY-08",
    ]:
        assert required in rule_ids
    for required in [
        "IPR-01",
        "IPR-02",
        "REVIEW-05",
        "REVIEW-06",
        "BOUNDARY-09",
        "BRAND-02",
    ]:
        assert required in rule_ids


def test_rulebook_contains_strict_localization_and_new_product_rules():
    structured_text = (ROOT / "rules/pdp_trust_rules_structured_v1.json").read_text()
    compressed_text = (ROOT / "rules/pdp_trust_rules_compressed_v1.txt").read_text()
    combined = structured_text + "\n" + compressed_text
    for expected in [
        "page_quality <= 3",
        "size_chart_images",
        "product_main_images",
        "target-country primary language",
        "is_new_product_30d",
        "cl_pay_sub_order_cnt < 10",
        "shop_sales",
        "shop_fans",
        "shop_final_score",
        "score 3 is not a harmless neutral value",
    ]:
        assert expected in combined


def test_prompts_include_new_visual_attribute_and_new_product_inputs():
    system_text = (ROOT / "prompts/trust_evaluator_system_prompt_v1.txt").read_text()
    user_text = (ROOT / "prompts/trust_evaluator_user_prompt_v1.txt").read_text()
    combined = system_text + "\n" + user_text
    for expected in [
        "{{product_main_images}}",
        "{{size_chart_images}}",
        "{{product_attributes_text}}",
        "{{image_manifest}}",
        "{{price_input_semantics}}",
        "{{is_new_product_30d}}",
        "{{new_product_context}}",
        "{{visual_evidence_context}}",
        "page_quality <= 3",
        "主图",
        "尺码图",
        "长图",
        "新品",
        "3 分不是普通中性分",
    ]:
        assert expected in combined


def test_system_prompts_are_aicolate_safe_plain_text():
    for rel_path in SYSTEM_PROMPTS:
        text = (ROOT / rel_path).read_text()
        for snippet in FORBIDDEN_SYSTEM_SNIPPETS:
            assert snippet not in text, f"{rel_path} contains forbidden system prompt snippet: {snippet}"
        assert "{{rules_context}}" in text


def test_user_prompts_contain_visual_inputs_and_result_contract():
    for rel_path in ["prompts/trust_evaluator_user_prompt_v1.txt"]:
        text = (ROOT / rel_path).read_text()
        assert "{{images}}" in text
        assert "{{case_state}}" in text
        assert "{{evidence_manifest}}" in text
        assert "{{decision_checklist}}" in text
        assert "<RESULT>" in text
        assert '"authenticity_delivery"' in text
        assert "b_end_reasons" in text
        assert "avg_star_rating" in text
        assert "{{review_contents}}" in text
        assert "3/4 boundary" in text
        assert "internal panel" in text
        assert "Part 1 和 Part 2 必须用中文输出" in text
        assert "不要用英文输出人工可读分析" in text
        for variable in FORBIDDEN_PROMPT_VARIABLES:
            assert variable not in text, f"{rel_path} contains forbidden alias variable {variable}"


def test_trust_evaluator_prompts_require_chinese_human_readable_output():
    system_text = (ROOT / "prompts/trust_evaluator_system_prompt_v1.txt").read_text()
    user_text = (ROOT / "prompts/trust_evaluator_user_prompt_v1.txt").read_text()
    for text in (system_text, user_text):
        assert "中文" in text
        assert "RESULT" in text
    assert "人工可读分析必须用中文输出" in system_text
    assert "JSON 字段名保持英文" in system_text
    assert "中文输出格式" in user_text


def test_trust_evaluator_prompts_harden_safety_value_visual_consistency():
    system_text = (ROOT / "prompts/trust_evaluator_system_prompt_v1.txt").read_text()
    user_text = (ROOT / "prompts/trust_evaluator_user_prompt_v1.txt").read_text()
    combined = system_text + "\n" + user_text
    assert "{{case_state}}" in combined
    assert "{{evidence_manifest}}" in combined
    assert "{{decision_checklist}}" in combined
    assert "safety must not remain 5" in combined
    assert "value=5 requires" in combined
    assert "Visible image/text consistency check" in combined
    assert "sales_price is USD" in combined
    assert "free shipping" in combined
    assert "buy one get one" in combined


def test_trust_evaluator_prompts_use_recent_review_contents_for_quality_reliability():
    system_text = (ROOT / "prompts/trust_evaluator_system_prompt_v1.txt").read_text()
    user_text = (ROOT / "prompts/trust_evaluator_user_prompt_v1.txt").read_text()
    combined = system_text + "\n" + user_text
    assert "review_contents" in combined
    assert "质量可靠性" in combined
    assert "最近 10 条评论" in combined
    assert "only for negative calibration" in combined
    assert "avg_review_star_td" in combined


def test_trust_evaluator_prompts_include_k_column_calibration_rules():
    system_text = (ROOT / "prompts/trust_evaluator_system_prompt_v1.txt").read_text()
    user_text = (ROOT / "prompts/trust_evaluator_user_prompt_v1.txt").read_text()
    combined = system_text + "\n" + user_text
    assert "IPR authorization ladder" in system_text
    assert "unsupported official" in system_text
    assert "4.6" in combined
    assert "Score 5" in combined
    assert "Sparse review evidence" in system_text
    assert "Official backing boundary" in system_text
    assert "IPR / 授权梯度检查" in user_text
    assert "5 分资格检查" in user_text
    assert "官方/品牌背书边界" in user_text


def test_active_workflow_has_exactly_one_llm_node():
    checked_files = [
        "PDP-Trust-Score-Overview.md",
        "PDP-Trust-Score-Aicolate-Wiring-Checklist.md",
        "PDP-Trust-Score-Workflow-Guide.html",
        "PDP-Trust-Score-Workflow-Diagram.svg",
    ]
    combined = "\n".join((ROOT / path).read_text() for path in checked_files)
    assert "Trust_Evaluator" in combined
    assert "exactly one LLM" in combined
    assert "only one LLM" in combined
    for stale in ["Juror_1", "Juror_2", "Juror_3", "Chief_Judge", "3 Jurors", "Chief Judge", "Result_Validator", "result_validator"]:
        assert stale not in combined, f"active workflow still mentions stale multi-LLM node: {stale}"


def test_active_workflow_is_single_product_per_invocation():
    checked_files = [
        "PDP-Trust-Score-Overview.md",
        "PDP-Trust-Score-Aicolate-Wiring-Checklist.md",
        "PDP-Trust-Score-Workflow-Guide.html",
    ]
    combined = "\n".join((ROOT / path).read_text() for path in checked_files)
    assert "single product per invocation" in combined
    assert "one product per workflow call" in combined
    for misleading in ["multi-product batch", "batch execution", "batch runs", "批量跑数"]:
        assert misleading not in combined, f"active workflow has misleading volume wording: {misleading}"


def test_rules_brain_code_node_parses_and_declares_main():
    code_path = ROOT / "code_nodes/rules_brain_pdp_trust_v1.py"
    source = code_path.read_text()
    tree = ast.parse(source)
    async_funcs = [node.name for node in tree.body if isinstance(node, ast.AsyncFunctionDef)]
    assert "main" in async_funcs
    assert "async def main(args: Args) -> Output:" in source
    assert "rules_context" in source
    assert "matched_rules" in source
    assert "risk_hints" in source
    assert "evidence_gaps" in source


def test_rules_brain_does_not_route_generic_beauty_to_fragrance():
    code_path = ROOT / "code_nodes/rules_brain_pdp_trust_v1.py"
    namespace = {"Args": object, "Output": dict}
    source = code_path.read_text()
    exec(compile(source, str(code_path), "exec"), namespace)
    rules = json.loads((ROOT / "rules/pdp_trust_rules_structured_v1.json").read_text())
    output = namespace["build_output"](
        {
            "rules_json": rules,
            "product_id": "1729699349693110915",
            "product_name": "Philips OneBlade 360 mit App Face + Body QP4631/65",
            "brand_name": "PHILIPS",
            "first_category_name": "Beauty & Personal Care",
            "product_desc": "Electric shaver for face and body.",
            "shop_name": "Philips Germany",
            "is_official_tag": "1",
            "sales_price": "57.156067",
            "list_price_usd": "85.739817",
            "shipping_fee": "4.99",
            "avg_review_star_td": "4.478571",
            "review_cnt_td": "135",
            "comment_summary_text": "Customers say it works for face and body.",
        }
    )
    assert "fragrance" not in output["pdp_debug_summary"]
    assert "strong_brand_attention" not in output["risk_hints"]
    assert "category_sensitivity_hint: Level 2: high trust sensitivity" in output["rules_context"]
    assert "power" not in output["pdp_debug_summary"]
    assert "charger" not in output["pdp_debug_summary"]


def test_rules_brain_still_routes_real_power_bank_to_power_level():
    code_path = ROOT / "code_nodes/rules_brain_pdp_trust_v1.py"
    namespace = {"Args": object, "Output": dict}
    source = code_path.read_text()
    exec(compile(source, str(code_path), "exec"), namespace)
    rules = json.loads((ROOT / "rules/pdp_trust_rules_structured_v1.json").read_text())
    output = namespace["build_output"](
        {
            "rules_json": rules,
            "product_id": "1729791252554095538",
            "product_name": "Magnetic Wireless Power Bank 5000mAh",
            "brand_name": "FullEra",
            "first_category_name": "Phones & Electronics",
            "product_desc": "5000mAh magnetic portable charger with USB-C charging.",
            "sales_price": "10.74695",
            "shipping_fee": "3.99",
            "avg_review_star_td": "3.886738",
            "review_cnt_td": "1656",
        }
    )
    assert "power" in output["pdp_debug_summary"]
    assert "charger" in output["pdp_debug_summary"]
    assert "category_sensitivity_hint: Level 1" in output["rules_context"]


def test_final_data_cleaning_code_node_parses_and_maps_rpc_images():
    code_path = ROOT / "code_nodes/final_data_cleaning_pdp_trust_v1.py"
    source = code_path.read_text()
    tree = ast.parse(source)
    async_funcs = [node.name for node in tree.body if isinstance(node, ast.AsyncFunctionDef)]
    assert "main" in async_funcs
    assert "async def main(args: Args) -> Output:" in source
    namespace = {"Args": object, "Output": dict}
    exec(compile(source, str(code_path), "exec"), namespace)
    sample = {
        "product_id": "1729791252554095538",
        "product_name": "Magnetic Wireless Power Bank 5000mAh",
        "brand_name": "FullEra",
        "first_category_name": "Phones & Electronics",
        "shop_name": "FullEra Official",
        "first_image": "https://example.com/main.image?",
        "product_desc": '<p>Compact charger</p><img src="https://example.com/detail.jpeg?x=1">',
        "comment_summary_text": "Customers mention slow charging and weak magnet.",
        "review_contents": "[\"Stops charging after a week\", \"Weak magnet but OK\", \"Works fine\"]",
        "star_ratings": "[1,3,5]",
        "is_official_tag": "0",
        "is_free_shipping_fee": "0",
        "has_flash_sale": "1",
        "is_free_return": "1",
        "sku_cnt": "8",
        "review_cnt_td": "1656",
        "avg_review_star_td": "3.886738",
        "avg_star_rating": "3.3",
        "list_price_usd": "21.50735",
        "sales_price": "10.74695",
        "shipping_fee": "3.99",
        "onnr15": "0.05",
        "onnr30": "0.08",
        "shop_positive_rate": "0.99",
        "ontime_delivery_rate": "0.91",
        "average_process_time": "12",
        "customer_service_satisfaction_rate": "0.92",
        "rpc_images": {
            "result": {
                "ProductMeta.images": {
                    "feature_value": "[\"https://example.com/hd1.jpeg\", \"https://example.com/hd2.jpeg\"]"
                }
            }
        },
    }
    output = namespace["build_output"](sample)
    assert output["product_id"] == "1729791252554095538"
    assert output["product_name"] == "Magnetic Wireless Power Bank 5000mAh"
    assert output["first_category_name"] == "Phones & Electronics"
    assert output["shop_name"] == "FullEra Official"
    assert output["sales_price"] == "10.74695"
    assert output["list_price_usd"] == "21.50735"
    assert output["avg_review_star_td"] == "3.886738"
    assert output["avg_star_rating"] == "3.3"
    assert output["review_contents"] == "[\"Stops charging after a week\", \"Weak magnet but OK\", \"Works fine\"]"
    assert output["review_cnt_td"] == "1656"
    assert output["product_main_images"] == ["https://example.com/hd1.jpeg", "https://example.com/hd2.jpeg"]
    assert output["images"] == ["https://example.com/hd1.jpeg", "https://example.com/hd2.jpeg"]
    assert output["image_source"] == "rpc_ProductMeta.images"
    assert "flash_sale" in output["logistics_info"]
    assert "free_return" in output["logistics_info"]
    assert "onnr15=0.05" in output["governance_metrics"]
    assert "onnr30=0.08" in output["governance_metrics"]
    assert "slow charging" in output["comment_summary_text"].lower()
    assert "Stops charging after a week" in output["review_context"]
    assert "star_ratings" not in output["review_context"]
    assert "Compact charger" in output["product_desc"]
    assert "https://example.com/detail.jpeg" not in output["product_desc"]
    assert "first_image" not in output
    for forbidden in FORBIDDEN_INPUT_FIELDS:
        assert forbidden not in output


def test_final_data_cleaning_preserves_all_product_main_images():
    namespace = load_code_node("code_nodes/final_data_cleaning_pdp_trust_v1.py")
    payload = {
        "output": {
            "BaseResp": {"StatusCode": 0, "StatusMessage": ""},
            "result": {
                "ProductMeta.images": {
                    "feature_code": "ProductMeta.images",
                    "feature_type": "Array",
                    "feature_value": json.dumps(["https://example.com/main-1.jpeg", "https://example.com/main-1.jpeg", "https://example.com/main-2.jpeg"]),
                }
            },
        }
    }
    output = namespace["build_output"]({"product_id": "all-images-case", "product_name": "All Image Case", "target_country": "UK", "rpc_images": payload})
    assert output["product_main_images"] == ["https://example.com/main-1.jpeg", "https://example.com/main-1.jpeg", "https://example.com/main-2.jpeg"]
    assert output["images"] == ["https://example.com/main-1.jpeg", "https://example.com/main-2.jpeg"]
    assert "product_main_images_count=3" in output["image_manifest"]
    assert "first image only" not in output["final_data_cleaning_debug"].lower()


def test_final_data_cleaning_uses_native_gbp_for_uk_prices():
    namespace = load_code_node("code_nodes/final_data_cleaning_pdp_trust_v1.py")
    output = namespace["build_output"](
        {
            "target_country": "UK",
            "sales_price": "100",
            "shipping_fee": "10",
            "list_price_usd": "150",
        }
    )

    assert output["currency"] == EXPECTED_TARGET_CURRENCIES["UK"]
    assert output["target_currency"] == EXPECTED_TARGET_CURRENCIES["UK"]
    assert output["price_input_semantics"] == "UK sales_price and shipping_fee are native GBP; no conversion applied"
    assert output["sales_price_local"] == "100.00"
    assert output["shipping_fee_local"] == "10.00"
    assert output["landed_cost_local"] == "110.00"
    assert "no conversion applied" in output["localized_price_context"]
    assert "list_price_usd=150.00 USD anchor only" in output["localized_price_context"]
    assert " -> " not in output["localized_price_context"]
    assert "exchange_rate" not in output["localized_price_context"]


def test_final_data_cleaning_converts_eu4_usd_prices_to_eur():
    namespace = load_code_node("code_nodes/final_data_cleaning_pdp_trust_v1.py")
    for target_country in sorted(SUPPORTED_TARGET_COUNTRIES - {"UK"}):
        output = namespace["build_output"](
            {
                "target_country": target_country,
                "sales_price": "100",
                "shipping_fee": "10",
                "list_price_usd": "150",
            }
        )

        assert output["currency"] == "USD"
        assert output["target_currency"] == EXPECTED_TARGET_CURRENCIES[target_country]
        assert output["exchange_rate_to_target_currency"] == USD_TO_EUR
        assert output["exchange_rate_date"] == EXCHANGE_RATE_DATE
        assert output["price_input_semantics"] == "EU4 sales_price and shipping_fee are USD; converted to EUR"
        assert output["sales_price_local"] == "86.45"
        assert output["shipping_fee_local"] == "8.65"
        assert output["landed_cost_local"] == "95.10"
        assert "100.00 USD -> 86.45 EUR" in output["localized_price_context"]
        assert "110.00 USD -> 95.10 EUR" in output["localized_price_context"]


def test_final_data_cleaning_normalizes_new_product_30d_flag():
    namespace = load_code_node("code_nodes/final_data_cleaning_pdp_trust_v1.py")

    new_low_sales = namespace["build_output"](
        {
            "target_country": "UK",
            "is_new_product_30d": "1",
            "cl_pay_sub_order_cnt": "9",
        }
    )
    assert new_low_sales["is_new_product_30d"] is True
    assert new_low_sales["new_product_context"] == (
        "is_new_product_30d=true; cl_pay_sub_order_cnt=9; new_product_low_sales=yes"
    )

    established_or_unknown = namespace["build_output"](
        {
            "target_country": "UK",
            "is_new_product_30d": "",
            "cl_pay_sub_order_cnt": "0",
        }
    )
    assert established_or_unknown["is_new_product_30d"] is False
    assert "new_product_low_sales=no" in established_or_unknown["new_product_context"]


def test_final_data_cleaning_parses_product_extra_attributes_rpc():
    namespace = load_code_node("code_nodes/final_data_cleaning_pdp_trust_v1.py")
    payload = {
        "output": {
            "BaseResp": {"StatusCode": 0, "StatusMessage": ""},
            "result": {
                "product_extra_attributes.product_attributes": {
                    "feature_code": "product_extra_attributes.product_attributes",
                    "feature_type": "Array",
                    "feature_value": json.dumps([
                        {"label": "Pattern", "value": "Plain"},
                        {"label": "Season", "value": "All Seasons"},
                        {"label": "Style", "value": "Casual"},
                        {"label": "Stretch", "value": "Slight Stretch"},
                        {"label": "Washing instructions", "value": "Machine wash, do not dry clean"},
                        {"label": "Material", "value": "Strong polyester single jersey"},
                        {"label": "Composition", "value": "Polyester 95%Elastane 5%"},
                        {"label": "Weaving method", "value": "Knit Fabric"},
                        {"label": "Sensitive goods type", "value": "Ordinary Goods"},
                        {"label": "Batch number", "value": "AW2026-09"},
                    ]),
                },
                "product_extra_attributes.size_chart": {
                    "feature_code": "product_extra_attributes.size_chart",
                    "feature_type": "Array",
                    "feature_value": json.dumps(["https://example.com/size-chart.jpeg"]),
                },
            },
        }
    }
    output = namespace["build_output"](
        {
            "product_id": "extra-attributes-case",
            "product_name": "Extra Attributes Case",
            "target_country": "DE",
            "product_extra_attributes": payload,
        }
    )
    assert output["size_chart_images"] == ["https://example.com/size-chart.jpeg"]
    assert "Pattern=Plain" in output["product_attributes_text"]
    assert "Material=Strong polyester single jersey" in output["product_attributes_text"]
    assert "Composition=Polyester 95%Elastane 5%" in output["product_attributes_text"]
    assert '"label": "Pattern"' in output["product_attributes_json"]
    assert "product_attributes=yes" in output["extra_attributes_source"]
    assert "size_chart_images_count=1" in output["image_manifest"]


def test_final_data_cleaning_does_not_duplicate_object_shaped_product_images():
    namespace = load_code_node("code_nodes/final_data_cleaning_pdp_trust_v1.py")
    payload = {
        "output": {
            "result": {
                "ProductMeta.images": {
                    "feature_code": "ProductMeta.images",
                    "feature_type": "Array",
                    "feature_value": json.dumps([
                        {"url": "https://example.com/object-main-1.jpeg"},
                        {"url": "https://example.com/object-main-2.jpeg"},
                    ]),
                }
            }
        }
    }
    output = namespace["build_output"]({"product_id": "object-images-case", "target_country": "UK", "rpc_images": payload})
    assert output["product_main_images"] == ["https://example.com/object-main-1.jpeg", "https://example.com/object-main-2.jpeg"]
    assert output["images"] == ["https://example.com/object-main-1.jpeg", "https://example.com/object-main-2.jpeg"]


def test_final_data_cleaning_falls_back_to_generic_rpc_url_wrapper():
    namespace = load_code_node("code_nodes/final_data_cleaning_pdp_trust_v1.py")
    output = namespace["build_output"](
        {
            "product_id": "generic-url-wrapper-case",
            "target_country": "UK",
            "rpc_images": {"output": {"url": "https://example.com/generic-main.jpeg"}},
        }
    )
    assert output["product_main_images"] == ["https://example.com/generic-main.jpeg"]
    assert output["images"] == ["https://example.com/generic-main.jpeg"]
    assert output["image_source"] == "rpc_ProductMeta.images"


def test_final_data_cleaning_parses_literal_extra_attributes_with_short_feature_codes():
    namespace = load_code_node("code_nodes/final_data_cleaning_pdp_trust_v1.py")
    payload = {
        "output": {
            "result": {
                "product_extra_attributes.product_attributes": {
                    "feature_code": "product_attributes",
                    "feature_value": json.dumps([{"label": "Material", "value": "Cotton"}]),
                },
                "product_extra_attributes.size_chart": {
                    "feature_code": "size_chart",
                    "feature_value": json.dumps(["https://example.com/short-size-chart.jpeg"]),
                },
            }
        }
    }
    output = namespace["build_output"]({"product_id": "short-feature-code-case", "target_country": "UK", "product_extra_attributes": payload})
    assert output["product_attributes_text"] == "Material=Cotton"
    assert '"label": "Material"' in output["product_attributes_json"]
    assert output["size_chart_images"] == ["https://example.com/short-size-chart.jpeg"]
    assert output["images"] == ["https://example.com/short-size-chart.jpeg"]


def test_final_data_cleaning_does_not_treat_extra_attributes_size_chart_as_product_main_images():
    namespace = load_code_node("code_nodes/final_data_cleaning_pdp_trust_v1.py")
    size_url = "https://example.com/extra-only-size-chart.jpeg"
    payload = {
        "output": {
            "result": {
                "product_extra_attributes.size_chart": {
                    "feature_code": "product_extra_attributes.size_chart",
                    "feature_type": "Array",
                    "feature_value": json.dumps([size_url]),
                },
            }
        }
    }
    output = namespace["build_output"](
        {
            "product_id": "extra-attributes-only-case",
            "target_country": "UK",
            "product_extra_attributes": payload,
        }
    )
    assert output["product_main_images"] == []
    assert output["size_chart_images"] == [size_url]
    assert output["images"] == [size_url]
    assert "rpc_ProductMeta.images" not in output["image_source"]


def test_final_data_cleaning_does_not_treat_nested_extra_attributes_size_chart_as_product_main_images():
    namespace = load_code_node("code_nodes/final_data_cleaning_pdp_trust_v1.py")
    size_url = "https://example.com/nested-extra-only-size-chart.jpeg"
    payload = {
        "output": {
            "result": {
                "product_extra_attributes.size_chart": {
                    "feature_code": "product_extra_attributes.size_chart",
                    "feature_type": "Array",
                    "feature_value": json.dumps([size_url]),
                },
            }
        }
    }
    output = namespace["build_output"](
        {
            "product_id": "nested-extra-attributes-only-case",
            "target_country": "UK",
            "input": {"product_extra_attributes": payload},
        }
    )
    assert output["product_main_images"] == []
    assert output["size_chart_images"] == [size_url]
    assert output["images"] == [size_url]
    assert "rpc_ProductMeta.images" not in output["image_source"]


def test_context_builder_code_node_builds_single_llm_status_fields():
    code_path = ROOT / "code_nodes/context_builder_pdp_trust_v1.py"
    source = code_path.read_text()
    tree = ast.parse(source)
    async_funcs = [node.name for node in tree.body if isinstance(node, ast.AsyncFunctionDef)]
    assert "main" in async_funcs
    assert "async def main(args: Args) -> Output:" in source
    namespace = {"Args": object, "Output": dict}
    exec(compile(source, str(code_path), "exec"), namespace)

    output = namespace["build_output"](
        {
            "product_id": "1729554479247563473",
            "product_name": "120W Power Bank 50000mAh Compact Portable USB Fast Charging",
            "brand_name": "Slick Link",
            "first_category_name": "Phones & Electronics",
            "image_source": "rpc_ProductMeta.images+product_desc_images",
            "images": ["https://example.com/main.jpeg", "https://example.com/detail.jpeg"],
            "product_desc": "Ultra-high capacity 50000mAh power bank with USB-C charging.",
            "sales_price": "29.36",
            "list_price_usd": "90",
            "currency": "USD",
            "shipping_fee": "3.99",
            "avg_review_star_td": "3.87",
            "avg_star_rating": "3.40",
            "review_cnt_td": "155",
            "review_contents": "[\"Actual capacity is nowhere near 50000mAh\", \"Slow charging\", \"Works fine\"]",
            "comment_summary_text": "A few buyers note the actual capacity appears below the 50,000mAh claim.",
            "rules_context": "category_sensitivity_hint: Level 1: very high trust sensitivity",
            "matched_rules": "BOUNDARY-01,BOUNDARY-08",
            "risk_hints": "claim_review_conflict_attention; recent_rating_downshift_attention",
            "evidence_gaps": "No official authorization proof; no visible safety certification",
            "price_context": "landed_cost=33.35 USD",
            "rules_review_context": "review_contents shows direct recent buyer text",
        }
    )

    assert set(output) == {
        "case_state",
        "evidence_manifest",
        "decision_checklist",
        "context_builder_debug",
    }
    assert "single-LLM PDP Trust evaluation" in output["case_state"]
    assert "product_id=1729554479247563473" in output["case_state"]
    assert "images_count=2" in output["evidence_manifest"]
    assert "review_contents_present=yes" in output["evidence_manifest"]
    assert "matched_rules=BOUNDARY-01,BOUNDARY-08" in output["evidence_manifest"]
    assert "Visible image/text consistency" in output["decision_checklist"]
    assert "Score 5 gate" in output["decision_checklist"]
    assert "context_builder_version=2026-08-17-v1" in output["context_builder_debug"]


def test_final_data_cleaning_accepts_loop_ecom_output_url_array():
    code_path = ROOT / "code_nodes/final_data_cleaning_pdp_trust_v1.py"
    namespace = {"Args": object, "Output": dict}
    source = code_path.read_text()
    exec(compile(source, str(code_path), "exec"), namespace)
    image_url = "https://p19-oec-eu-common-no.tiktokcdn-eu.com/tos-no1a-i-t5fjg24jzw-no/3685bac2e59d4c21bc3b3ad5ceab3cb4.jpeg"
    output = namespace["build_output"](
        {
            "product_id": "1729405015928311764",
            "product_name": "NobleNature Vitamin B12",
            "product_desc": "Nutritional Information for capsules.",
            "output": [image_url],
        }
    )
    assert output["images"] == [image_url]
    assert output["image_source"] == "rpc_ProductMeta.images"
    assert "images_count=1" in output["final_data_cleaning_debug"]


def test_rules_brain_flags_claim_review_conflict_zero_price_and_recent_rating_downshift():
    code_path = ROOT / "code_nodes/rules_brain_pdp_trust_v1.py"
    namespace = {"Args": object, "Output": dict}
    source = code_path.read_text()
    exec(compile(source, str(code_path), "exec"), namespace)
    rules = json.loads((ROOT / "rules/pdp_trust_rules_structured_v1.json").read_text())
    output = namespace["build_output"](
        {
            "rules_json": rules,
            "product_id": "1729554479247563473",
            "product_name": "120W Power Bank 50000mAh Compact Portable USB Fast Charging",
            "brand_name": "Slick Link",
            "first_category_name": "Phones & Electronics",
            "product_desc": "Ultra-high capacity 50000mAh power bank with multiple charging ports.",
            "sales_price": "29.36",
            "list_price_usd": "90",
            "shipping_fee": "3.99",
            "avg_review_star_td": "3.87",
            "avg_star_rating": "3.40",
            "star_ratings": "[1,3,4,4,5,4,3,5,4,1]",
            "review_cnt_td": "155",
            "review_contents": "[\"Actual capacity is nowhere near 50000mAh\", \"Slow charging\", \"Works fine\"]",
            "comment_summary_text": "A few buyers note the actual capacity appears below the 50,000mAh claim.",
        }
    )
    assert "BOUNDARY-01" in output["matched_rules"]
    assert "BOUNDARY-08" in output["matched_rules"]
    assert "claim_review_conflict_attention" in output["risk_hints"]
    assert "recent_rating_downshift_attention" in output["risk_hints"]
    assert "recent_review_contents_attention" in output["risk_hints"]
    assert "review_contents shows direct recent buyer text" in output["review_context"]
    assert "avg_star_rating: 3.40" in output["pdp_debug_summary"]
    assert "star_ratings" not in output["pdp_debug_summary"]

    zero_price = namespace["build_output"](
        {
            "rules_json": rules,
            "product_id": "1729877523630168204",
            "product_name": "Portable Mini Turbo Fan",
            "first_category_name": "Household Appliances",
            "sales_price": "0",
            "shipping_fee": "8.97",
            "review_cnt_td": "0",
        }
    )
    assert "BOUNDARY-06" in zero_price["matched_rules"]
    assert "zero_price_pollution_attention" in zero_price["risk_hints"]
    assert "do not evaluate value from sales_price=0" in zero_price["price_context"]


def test_rules_brain_does_not_upgrade_when_recent_rating_is_higher_than_historical():
    code_path = ROOT / "code_nodes/rules_brain_pdp_trust_v1.py"
    namespace = {"Args": object, "Output": dict}
    source = code_path.read_text()
    exec(compile(source, str(code_path), "exec"), namespace)
    rules = json.loads((ROOT / "rules/pdp_trust_rules_structured_v1.json").read_text())
    output = namespace["build_output"](
        {
            "rules_json": rules,
            "product_id": "recent-higher",
            "product_name": "Portable Home Appliance",
            "first_category_name": "Household Appliances",
            "sales_price": "49.99",
            "avg_review_star_td": "3.40",
            "avg_star_rating": "4.70",
            "review_cnt_td": "200",
            "comment_summary_text": "Customers say the item works, but some report reliability issues.",
        }
    )
    assert "BOUNDARY-08" not in output["matched_rules"]
    assert "recent_rating_downshift_attention" not in output["risk_hints"]
    assert "higher recent avg_star_rating must not upgrade" in output["review_context"]


def test_rules_brain_flags_auction_and_child_safety():
    code_path = ROOT / "code_nodes/rules_brain_pdp_trust_v1.py"
    namespace = {"Args": object, "Output": dict}
    source = code_path.read_text()
    exec(compile(source, str(code_path), "exec"), namespace)
    rules = json.loads((ROOT / "rules/pdp_trust_rules_structured_v1.json").read_text())
    auction = namespace["build_output"](
        {
            "rules_json": rules,
            "product_id": "1729526442548890934",
            "product_name": "Designer Fragrance - No CANCELLATIONS",
            "first_category_name": "Beauty & Personal Care",
            "product_desc": "Auction listing. No cancellations.",
            "sales_price": "0",
            "review_cnt_td": "0",
        }
    )
    assert "BOUNDARY-07" in auction["matched_rules"]
    assert "auction_exclusion_attention" in auction["risk_hints"]

    child_safety = namespace["build_output"](
        {
            "rules_json": rules,
            "product_id": "1729601257574865792",
            "product_name": "Trampoline with Safety Net Cover 200KG Load Outdoor & Indoor Play for Kids",
            "first_category_name": "Sports & Outdoor",
            "comment_summary_text": "Some report the safety net zip and spring cover don't stay secure or padded.",
            "avg_review_star_td": "4.30",
            "review_cnt_td": "1301",
        }
    )
    assert "BOUNDARY-03" in child_safety["matched_rules"]
    assert "child_safety_cap_attention" in child_safety["risk_hints"]


def test_rules_brain_flags_new_review_regression_patterns():
    code_path = ROOT / "code_nodes/rules_brain_pdp_trust_v1.py"
    namespace = {"Args": object, "Output": dict}
    source = code_path.read_text()
    exec(compile(source, str(code_path), "exec"), namespace)
    rules = json.loads((ROOT / "rules/pdp_trust_rules_structured_v1.json").read_text())

    hellstar = namespace["build_output"](
        {
            "rules_json": rules,
            "product_id": "1729770707678238721",
            "product_name": "Vintage Dark Streetwear Star Flame Graphic T-Shirt",
            "first_category_name": "Menswear & Underwear",
            "product_desc": "Dark streetwear graphic tee with heaven hell star flame motif.",
            "comment_summary_text": "Few reviews.",
        }
    )
    assert "streetwear_brand_ip_attention" in hellstar["risk_hints"]

    shipping_mismatch = namespace["build_output"](
        {
            "rules_json": rules,
            "product_id": "1729477930798652055",
            "product_name": "[Free Shipping] Memory pillow slow rebound neck protection",
            "first_category_name": "Textiles & Soft Furnishings",
            "shipping_fee": "8.99",
            "sales_price": "14.00",
        }
    )
    assert "shipping_claim_mismatch_attention" in shipping_mismatch["risk_hints"]
    assert "shipping_fee conflicts with free shipping claim" in shipping_mismatch["price_context"]

    safety_terms = namespace["build_output"](
        {
            "rules_json": rules,
            "product_id": "1729770617549396226",
            "product_name": "Hogwarts Magic Wand Replica",
            "first_category_name": "Toys & Hobbies",
            "comment_summary_text": "Customers report the wand shoots real flame.",
        }
    )
    assert "safety_related_review_attention" in safety_terms["risk_hints"]

    body_harm = namespace["build_output"](
        {
            "rules_json": rules,
            "product_id": "1729402710285192680",
            "product_name": "Lash Growth Serum",
            "first_category_name": "Beauty & Personal Care",
            "review_contents": "[\"Caused a stye and eye injury\", \"Burning around my eye after use\"]",
            "comment_summary_text": "Customers report stye, eye injury, and burning after using the applicator.",
        }
    )
    assert "BOUNDARY-05" in body_harm["matched_rules"]
    assert "body_harm_nuance_attention" in body_harm["risk_hints"]
    assert "final score must not exceed 3" in body_harm["risk_hints"]


def test_rules_brain_flags_ipr_authorization_ladder_and_score5_gate():
    code_path = ROOT / "code_nodes/rules_brain_pdp_trust_v1.py"
    namespace = {"Args": object, "Output": dict}
    source = code_path.read_text()
    exec(compile(source, str(code_path), "exec"), namespace)
    rules = json.loads((ROOT / "rules/pdp_trust_rules_structured_v1.json").read_text())

    unsupported_official_ipr = namespace["build_output"](
        {
            "rules_json": rules,
            "product_id": "row-426-1729734954462124608",
            "product_name": "47 Brand San Diego Padres Clean Up Relaxed Cap Official Major League Baseball licensed product",
            "brand_name": "No brand",
            "first_category_name": "Fashion Accessories",
            "shop_name": "Sports Outlet UK",
            "is_official_tag": "0",
            "sales_price": "24.99",
            "shipping_fee": "0",
            "review_cnt_td": "0",
        }
    )
    assert "IPR-01" in unsupported_official_ipr["matched_rules"]
    assert "IPR-02" in unsupported_official_ipr["matched_rules"]
    assert "ipr_authorization_ladder_attention" in unsupported_official_ipr["risk_hints"]
    assert "unsupported_official_claim_attention" in unsupported_official_ipr["risk_hints"]

    score_5_candidate = namespace["build_output"](
        {
            "rules_json": rules,
            "product_id": "score-5-candidate",
            "product_name": "Ninja Thirsti Travel Bottle",
            "brand_name": "Ninja",
            "first_category_name": "Kitchenware",
            "shop_name": "Ninja UK",
            "is_official_tag": "1",
            "sales_price": "19.99",
            "shipping_fee": "0",
            "avg_review_star_td": "4.72",
            "avg_star_rating": "4.8",
            "review_cnt_td": "1200",
            "review_contents": "[\"Excellent bottle\", \"No leaks\", \"Keeps drinks cold\"]",
            "comment_summary_text": "Customers are positive and do not report objective defects.",
        }
    )
    assert "REVIEW-05" in score_5_candidate["matched_rules"]
    assert "score_5_candidate_attention" in score_5_candidate["risk_hints"]

    sparse_objective_issue = namespace["build_output"](
        {
            "rules_json": rules,
            "product_id": "sparse-objective-issue",
            "product_name": "Portable garment steamer",
            "first_category_name": "Home Appliances",
            "review_cnt_td": "3",
            "avg_review_star_td": "3.8",
            "avg_star_rating": "3.5",
            "review_contents": "[\"Arrived missing parts\", \"Leaked water\", \"Works okay\"]",
        }
    )
    assert "REVIEW-06" in sparse_objective_issue["matched_rules"]
    assert "sparse_review_objective_issue_cap_attention" in sparse_objective_issue["risk_hints"]

    ml_conflict = namespace["build_output"](
        {
            "rules_json": rules,
            "product_id": "1729793703628675180",
            "product_name": "Hismile Tooth Armour 60 ml serum",
            "first_category_name": "Beauty & Personal Care",
            "product_desc": "Main package image text says 20 ml / 0.67 fl oz.",
        }
    )
    assert "visible_image_text_consistency_attention" in ml_conflict["risk_hints"]


def test_rules_brain_risk_hints_separate_triggered_signals_from_checklist_reminders():
    code_path = ROOT / "code_nodes/rules_brain_pdp_trust_v1.py"
    namespace = {"Args": object, "Output": dict}
    source = code_path.read_text()
    exec(compile(source, str(code_path), "exec"), namespace)
    rules = json.loads((ROOT / "rules/pdp_trust_rules_structured_v1.json").read_text())

    ulike = namespace["build_output"](
        {
            "rules_json": rules,
            "product_id": "1729685220404009673",
            "product_name": "Ulike Air 10 IPL Laser Hair Removal Device Nearly Painless",
            "brand_name": "Ulike",
            "first_category_name": "Beauty & Personal Care",
            "shop_name": "Ulike UK",
            "is_official_tag": "1",
            "sales_price": "497.95104199999997",
            "shipping_fee": "0",
            "avg_review_star_td": "4.5294119999999998",
            "avg_star_rating": "4.5",
            "review_cnt_td": "146",
            "review_contents": "[\"Looks good and really easy to use\", \"Didn’t really work\", \"It does slightly burn a little sometimes but its easily bearable\"]",
            "comment_summary_text": "Most customers are positive but some mention limited effect and slight burning.",
        }
    )
    risk_hints = ulike["risk_hints"]
    assert "TRIGGERED DETERMINISTIC SIGNALS" in risk_hints
    assert "CHECKLIST REMINDERS ONLY" in risk_hints
    triggered = risk_hints.split("CHECKLIST REMINDERS ONLY", 1)[0]
    checklist = risk_hints.split("CHECKLIST REMINDERS ONLY", 1)[1]
    assert "category_sensitivity_hint: Level 2" in checklist
    assert "body_contact_category_check" in checklist
    assert "official_backing_boundary_check" in checklist
    assert "ipr_authorization_ladder_check" in checklist
    assert "strong_brand_attention" not in triggered
    assert "ipr_authorization_ladder_attention" not in triggered
    assert "used_refurbished_overlay" not in risk_hints
    assert "recent_review_contents_signal" in triggered
    assert "score_5_blocker_signal" in triggered

    zero_price = namespace["build_output"](
        {
            "rules_json": rules,
            "product_id": "zero-price",
            "product_name": "[Free Shipping] Portable Mini Fan",
            "first_category_name": "Household Appliances",
            "sales_price": "0",
            "shipping_fee": "8.99",
        }
    )
    zero_triggered = zero_price["risk_hints"].split("CHECKLIST REMINDERS ONLY", 1)[0]
    assert "zero_price_pollution_signal" in zero_triggered
    assert "shipping_claim_mismatch_signal" in zero_triggered


def test_rules_brain_does_not_treat_using_as_used_refurbished_condition():
    code_path = ROOT / "code_nodes/rules_brain_pdp_trust_v1.py"
    namespace = {"Args": object, "Output": dict}
    source = code_path.read_text()
    exec(compile(source, str(code_path), "exec"), namespace)
    rules = json.loads((ROOT / "rules/pdp_trust_rules_structured_v1.json").read_text())

    normal_use = namespace["build_output"](
        {
            "rules_json": rules,
            "product_id": "normal-use",
            "product_name": "Ulike Air 10 IPL Laser Hair Removal Device",
            "brand_name": "Ulike",
            "first_category_name": "Beauty & Personal Care",
            "shop_name": "Ulike UK",
            "is_official_tag": "1",
            "review_contents": "[\"I have been using it for two weeks\", \"Easy to use\", \"Used it before my night routine\"]",
            "comment_summary_text": "Customers mention using the machine regularly.",
        }
    )
    assert "used_refurbished_check" not in normal_use["risk_hints"]
    routing_tags = normal_use["pdp_debug_summary"].split("routing_tags: ", 1)[1]
    assert "used" not in routing_tags
    assert "refurbished" not in routing_tags

    refurbished = namespace["build_output"](
        {
            "rules_json": rules,
            "product_id": "refurbished-condition",
            "product_name": "Refurbished iPhone 13 Open Box Grade A",
            "brand_name": "Apple",
            "first_category_name": "Phones & Electronics",
            "product_desc": "This is a refurbished open-box phone with condition grade A.",
        }
    )
    assert "used_refurbished_check" in refurbished["risk_hints"]
    routing_tags = refurbished["pdp_debug_summary"].split("routing_tags: ", 1)[1]
    assert "refurbished" in routing_tags


def test_rules_brain_does_not_route_official_own_brand_to_ipr_ladder():
    code_path = ROOT / "code_nodes/rules_brain_pdp_trust_v1.py"
    namespace = {"Args": object, "Output": dict}
    source = code_path.read_text()
    exec(compile(source, str(code_path), "exec"), namespace)
    rules = json.loads((ROOT / "rules/pdp_trust_rules_structured_v1.json").read_text())

    official_own_brand = namespace["build_output"](
        {
            "rules_json": rules,
            "product_id": "1729685220404009673",
            "product_name": "Ulike Air 10 IPL Laser Hair Removal Device",
            "brand_name": "Ulike",
            "first_category_name": "Beauty & Personal Care",
            "shop_name": "Ulike UK",
            "is_official_tag": "1",
            "product_desc": "Ulike hair removal device with official warranty and safety details.",
            "review_cnt_td": "135",
            "avg_review_star_td": "4.52",
            "avg_star_rating": "4.5",
        }
    )
    routing_tags = official_own_brand["pdp_debug_summary"].split("routing_tags: ", 1)[1]
    assert "ipr_authorization_ladder" not in routing_tags
    assert "ipr" not in routing_tags
    assert "ip," not in routing_tags + ","
    assert "IPR-01" not in official_own_brand["matched_rules"]
    assert "IPR-02" not in official_own_brand["matched_rules"]
    assert "official_authentic_claim_check" in official_own_brand["risk_hints"]

    unsupported_official_ipr = namespace["build_output"](
        {
            "rules_json": rules,
            "product_id": "row-426-1729734954462124608",
            "product_name": "47 Brand San Diego Padres Clean Up Relaxed Cap Official Major League Baseball licensed product",
            "brand_name": "No brand",
            "first_category_name": "Fashion Accessories",
            "shop_name": "Sports Outlet UK",
            "is_official_tag": "0",
            "sales_price": "24.99",
            "shipping_fee": "0",
            "review_cnt_td": "0",
        }
    )
    routing_tags = unsupported_official_ipr["pdp_debug_summary"].split("routing_tags: ", 1)[1]
    assert "ipr_authorization_ladder" in routing_tags
    assert "IPR-01" in unsupported_official_ipr["matched_rules"]
    assert "IPR-02" in unsupported_official_ipr["matched_rules"]
    assert "unsupported_official_claim_signal" in unsupported_official_ipr["risk_hints"]


def test_final_data_cleaning_recursively_finds_aicolate_rpc_output_shape():
    code_path = ROOT / "code_nodes/final_data_cleaning_pdp_trust_v1.py"
    namespace = {"Args": object, "Output": dict}
    source = code_path.read_text()
    exec(compile(source, str(code_path), "exec"), namespace)
    sample = {
        "product_id": "1729699349693110915",
        "product_name": "Philips OneBlade 360 mit App Face + Body QP4631/65",
        "output": {
            "BaseResp": {"StatusCode": 0, "StatusMessage": ""},
            "result": {
                "ProductMeta.images": {
                    "feature_code": "images",
                    "feature_type": "Array",
                    "feature_value": "[\"https://example.com/philips-hd-1.jpeg\", \"https://example.com/philips-hd-2.jpeg\"]",
                    "is_bolt_usable": True,
                }
            },
        },
    }
    output = namespace["build_output"](sample)
    assert output["product_main_images"] == ["https://example.com/philips-hd-1.jpeg", "https://example.com/philips-hd-2.jpeg"]
    assert output["images"] == ["https://example.com/philips-hd-1.jpeg", "https://example.com/philips-hd-2.jpeg"]
    assert output["image_source"] == "rpc_ProductMeta.images"


def test_compressed_rulebook_mentions_output_contract():
    text = (ROOT / "rules/pdp_trust_rules_compressed_v1.txt").read_text()
    for field in REQUIRED_SCORE_FIELDS:
        assert field in text
    for reason in ALLOWED_B_END_REASONS:
        assert reason in text


def test_forbidden_fields_removed_from_copybook_assets():
    checked_files = [
        "code_nodes/final_data_cleaning_pdp_trust_v1.py",
        "code_nodes/rules_brain_pdp_trust_v1.py",
        "code_nodes/context_builder_pdp_trust_v1.py",
        "prompts/trust_evaluator_user_prompt_v1.txt",
        "PDP-Trust-Score-Aicolate-Wiring-Checklist.md",
        "PDP-Trust-Score-Excel-Input-Mapping.md",
    ]
    for rel_path in checked_files:
        text = (ROOT / rel_path).read_text()
        for forbidden in FORBIDDEN_INPUT_FIELDS:
            assert forbidden not in text, f"{rel_path} still mentions forbidden field {forbidden}"


def test_wiring_uses_rpc_and_final_data_cleaning_only():
    text = (ROOT / "PDP-Trust-Score-Aicolate-Wiring-Checklist.md").read_text()
    assert "product_image_rpc" in text
    assert "ProductMeta.images" in text
    assert "Final_data_cleaning" in text
    assert "Context_Builder" in text
    assert "Trust_Evaluator" in text
    assert "Result_Validator" not in text
    assert "result_validator" not in text
    assert "Excel_Row_Cleaning" not in text
    assert "images: Array<String>" in text
    assert "case_state: String" in text
    assert "evidence_manifest: String" in text
    assert "decision_checklist: String" in text
    assert text.count("body = rules_text_fetch.body") == 1


def test_model_facing_text_uses_eu_uk_locale_not_us_locale():
    checked_files = [
        "rules/pdp_trust_rules_compressed_v1.txt",
        "rules/pdp_trust_rules_structured_v1.json",
        "prompts/trust_evaluator_system_prompt_v1.txt",
        "prompts/trust_evaluator_user_prompt_v1.txt",
    ]
    for rel_path in checked_files:
        text = (ROOT / rel_path).read_text()
        for phrase in FORBIDDEN_LOCALE_PHRASES:
            assert phrase not in text, f"{rel_path} still contains US locale phrase: {phrase}"
    combined = "\n".join((ROOT / path).read_text() for path in checked_files)
    assert "British" in combined
    assert "UK" in combined


def test_clear_user_bodily_harm_caps_final_score_at_three():
    structured = json.loads((ROOT / "rules/pdp_trust_rules_structured_v1.json").read_text())
    boundary_05 = next(rule for rule in structured["rules"] if rule["id"] == "BOUNDARY-05")
    required_phrase = "clear bodily harm to the user"
    assert required_phrase in boundary_05["text"]
    assert "final score must not exceed 3" in boundary_05["text"]

    checked_files = [
        "rules/pdp_trust_rules_compressed_v1.txt",
        "code_nodes/rules_brain_pdp_trust_v1.py",
        "prompts/trust_evaluator_system_prompt_v1.txt",
        "prompts/trust_evaluator_user_prompt_v1.txt",
        "PDP-Trust-Score-Overview.md",
    ]
    for rel_path in checked_files:
        text = (ROOT / rel_path).read_text()
        assert required_phrase in text, f"{rel_path} misses clear bodily harm hard cap wording"
        assert "final score must not exceed 3" in text, f"{rel_path} misses final score hard cap wording"
