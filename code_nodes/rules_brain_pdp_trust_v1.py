import json
import re


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


def minimal_fallback_rules():
    return {
        "project": "pdp-trust-score_EU4-UK",
        "version": "2026-09-20-vnext-fallback",
        "locale": "merged_uk_eu4_target_country",
        "exchange_rate_baseline": {
            "source": "Frankfurter API",
            "date": "2026-08-14",
            "base": "USD",
            "rates": {"GBP": 0.73874, "EUR": 0.86453},
        },
        "locale_profiles": {
            "UK": {
                "buyer_persona": "British TikTok Shop shopper",
                "primary_language": "English",
                "tolerated_languages": ["English"],
                "target_currency": "GBP",
                "strict_language_rule": "Strict UK localization: core PDP info in non-target primary language without target-language translation means page_quality <= 3.",
                "language_tolerance": "Only brand names, model names, international measurement units, and non-critical decorative text may remain outside English without penalty. Core purchase info must be available in English or page_quality <= 3.",
                "value_judgment": "Use native GBP landed cost for coarse UK buyer value reasoning.",
            },
            "DE": {
                "buyer_persona": "German TikTok Shop shopper",
                "primary_language": "German",
                "tolerated_languages": ["German"],
                "target_currency": "EUR",
                "strict_language_rule": "Strict DE localization: core PDP info in non-target primary language without target-language translation means page_quality <= 3.",
                "language_tolerance": "Only brand names, model names, international measurement units, and non-critical decorative text may remain outside German without penalty. Core purchase info must be available in German or page_quality <= 3.",
                "value_judgment": "Use localized EUR landed cost converted from USD for coarse German buyer value reasoning.",
            },
            "FR": {
                "buyer_persona": "French TikTok Shop shopper",
                "primary_language": "French",
                "tolerated_languages": ["French"],
                "target_currency": "EUR",
                "strict_language_rule": "Strict FR localization: core PDP info in non-target primary language without target-language translation means page_quality <= 3.",
                "language_tolerance": "Only brand names, model names, international measurement units, and non-critical decorative text may remain outside French without penalty. Core purchase info must be available in French or page_quality <= 3.",
                "value_judgment": "Use localized EUR landed cost converted from USD for coarse French buyer value reasoning.",
            },
            "ES": {
                "buyer_persona": "Spanish TikTok Shop shopper",
                "primary_language": "Spanish",
                "tolerated_languages": ["Spanish"],
                "target_currency": "EUR",
                "strict_language_rule": "Strict ES localization: core PDP info in non-target primary language without target-language translation means page_quality <= 3.",
                "language_tolerance": "Only brand names, model names, international measurement units, and non-critical decorative text may remain outside Spanish without penalty. Core purchase info must be available in Spanish or page_quality <= 3.",
                "value_judgment": "Use localized EUR landed cost converted from USD for coarse Spanish buyer value reasoning.",
            },
            "IT": {
                "buyer_persona": "Italian TikTok Shop shopper",
                "primary_language": "Italian",
                "tolerated_languages": ["Italian"],
                "target_currency": "EUR",
                "strict_language_rule": "Strict IT localization: core PDP info in non-target primary language without target-language translation means page_quality <= 3.",
                "language_tolerance": "Only brand names, model names, international measurement units, and non-critical decorative text may remain outside Italian without penalty. Core purchase info must be available in Italian or page_quality <= 3.",
                "value_judgment": "Use localized EUR landed cost converted from USD for coarse Italian buyer value reasoning.",
            },
        },
        "score_fields": [
            "authenticity_delivery",
            "compliance",
            "page_quality",
            "quality",
            "safety",
            "score",
            "value",
        ],
        "allowed_b_end_reasons": ALLOWED_B_END_REASONS,
        "rules": [
            {
                "id": "CORE-01",
                "category": "core",
                "text": "Score is not a six-field average. Authenticity, delivery, quality, safety, scam, counterfeit, wrong-item, invalid-code, and PDP honesty define the baseline. Price only adjusts after trust is credible.",
                "applies_to": ["all"],
            },
            {
                "id": "STAGE1-05",
                "category": "red_flag",
                "text": "Do not downscore ordinary fan-style/IP decoration automatically. International big brands and strong genuine-market brands are stricter: clear logo-like, monogram, packaging, bottle, shoe, bag, classic colorway, naming structure, or trade dress imitation can support score 2 even without explicit brand words.",
                "applies_to": ["brand", "ip", "luxury"],
            },
            {
                "id": "IPR-01",
                "category": "red_flag",
                "text": "Use a three-step IPR authorization ladder: clear IPR without credible official authorization usually scores 2; suspected IPR without abnormal price or strong impersonation usually scores 3; score above 3 requires credible official store, brand flagship, platform official tag, authorization, authentication, or equivalent proof.",
                "applies_to": ["ipr_authorization_ladder", "ipr", "ip", "licensed", "official", "authentic", "brand"],
            },
            {
                "id": "IPR-02",
                "category": "red_flag",
                "text": "Unsupported official, licensed, authentic, genuine, or authorized claims are not proof by themselves. If channel evidence does not support the claim, cap at 3 by default and downgrade to 2 when abnormal price, strong visual imitation, weak white-label evidence, or strong official impersonation is also present.",
                "applies_to": ["unsupported_official_claim", "official", "licensed", "authentic", "genuine", "authorized"],
            },
            {
                "id": "REVIEW-05",
                "category": "review_logic",
                "text": "Score 5 is allowed when avg_review_star_td and avg_star_rating are both at least 4.6 and review_contents shows no clear objective negative review, safety issue, IPR or authorization issue, hard claim conflict, or unstable fulfillment evidence.",
                "applies_to": ["score_5_candidate", "score_5_blocker", "review_volume_absorbs_limited_negatives"],
            },
            {
                "id": "REVIEW-06",
                "category": "review_logic",
                "text": "Sparse review evidence plus objective product, quality, fulfillment, missing-part, leaking, wrong-item, core-function, or safety complaints usually caps the final score at 3 unless strong official/channel/page evidence clearly shows the issue is isolated and low impact.",
                "applies_to": ["sparse_review_objective_issue_cap", "reviews", "quality", "fulfillment"],
            },
            {
                "id": "BRAND-02",
                "category": "arbitration",
                "text": "Official store, brand flagship, platform official tag, and strong brand-channel evidence protect authenticity and delivery confidence, but do not override clear IPR risk, unsupported official claims, hard PDP claim conflicts, safety concerns, repeated core quality failures, or strong misleading evidence.",
                "applies_to": ["official_backing_protection_boundary", "official", "brand", "authorized", "channel"],
            },
            {
                "id": "BOUNDARY-09",
                "category": "boundary_calibration",
                "text": "Clear core-claim or core-information conflict can override positive social proof. If the mismatch affects what the buyer receives, repaired/refurbished condition, quantity, volume, core ingredients, safety disclosure, or food/supplement trust, cap at 3 and consider score 2 when severe.",
                "applies_to": ["hard_claim_spec_conflict", "hard_misleading_conflict", "page_spec_conflict", "refurbished", "oral care", "beauty", "food", "child_safety"],
            },
            {
                "id": "BOUNDARY-05",
                "category": "boundary_calibration",
                "text": "For body-contact goods, mild inherent reaction can be a small downgrade, but when PDP or review evidence shows clear bodily harm to the user from avoidable product failure, the final score must not exceed 3. Concentrated injury complaints can support score 2.",
                "applies_to": ["body_harm", "clear_bodily_harm_hard_cap", "beauty", "personal care", "health", "safety"],
            },
            {
                "id": "SPECIAL-06",
                "category": "special_overlay",
                "text": "Digital cards/codes are near Level 1. Evaluate official or authorized channel, delivery method, region, currency, face value, expiry, restrictions, refund policy, works/redeemed reviews, and invalid/already redeemed/never received/scam reviews.",
                "applies_to": ["digital code", "gift card"],
            },
            {
                "id": "BEND-01",
                "category": "output",
                "text": "Only output b_end_reasons when score is below 4 and a clear actionable main cause exists. Use at most 3 reasons, exactly from the allowed list.",
                "applies_to": ["all"],
            },
            {
                "id": "BOUNDARY-01",
                "category": "boundary_calibration",
                "text": "If a core PDP promise conflicts with review evidence, do not keep score 4; usually reduce authenticity_delivery and quality and cap high-risk categories at 3.",
                "applies_to": ["claim_review_conflict"],
            },
            {
                "id": "BOUNDARY-06",
                "category": "boundary_calibration",
                "text": "sales_price=0 is missing or polluted price data for normal PDPs, not strong value or low-price bait by itself.",
                "applies_to": ["zero_price"],
            },
            {
                "id": "BOUNDARY-07",
                "category": "boundary_calibration",
                "text": "Auction or bidding listings are not comparable fixed-price PDPs; exclude from normal PDP Trust Score calibration when detected.",
                "applies_to": ["auction_listing"],
            },
            {
                "id": "BOUNDARY-08",
                "category": "boundary_calibration",
                "text": "Use avg_review_star_td as the primary historical rating. Use avg_star_rating only for negative calibration when recent rating is meaningfully lower; a higher recent rating must not upgrade the score.",
                "applies_to": ["recent_rating_downshift"],
            },
        ],
        "routing_hints": {
            "level_1_keywords": ["food", "supplement", "baby", "pet food", "battery", "charger", "luxury", "sneaker", "collectible", "gift card", "redeem code"],
            "level_2_keywords": ["beauty", "fragrance", "hair dryer", "small appliance", "fitness", "massager"],
            "level_4_5_keywords": ["phone case", "sticker", "keychain", "party", "decoration", "novelty"],
            "digital_keywords": ["gift card", "redeem code", "pin code", "top up", "voucher"],
            "tcg_keywords": ["trading card", "tcg", "pokemon", "booster", "random lot"],
            "used_keywords": ["used", "refurbished", "open box"],
            "custom_keywords": ["custom", "personalized", "handmade"],
            "regulated_keywords": ["adult", "weapon", "medical", "drug", "cannabis"],
            "big_brand_keywords": ["nike", "adidas", "jordan", "gucci", "lv", "chanel", "dior", "prada", "rolex", "fragrance"],
        },
    }


def unwrap_body(value):
    if isinstance(value, str):
        text = value.strip()
        if text.startswith("{") or text.startswith("["):
            try:
                return unwrap_body(json.loads(text))
            except Exception:
                return value
        return value
    if isinstance(value, dict):
        for key in ("body", "Body", "data", "content", "output", "result"):
            if key in value:
                return unwrap_body(value.get(key))
    return value


def find_param(params, names):
    for name in names:
        if name in params:
            return params.get(name)
    for value in params.values():
        if isinstance(value, dict):
            found = find_param(value, names)
            if found is not None:
                return found
    return None


def text_param(params, *names):
    value = find_param(params, names)
    value = unwrap_body(value)
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (int, float)):
        return str(value)
    return json.dumps(value, ensure_ascii=False)


def parse_float(text):
    if text is None:
        return None
    if isinstance(text, (int, float)):
        return float(text)
    cleaned = re.sub(r"[^0-9.\\-]", "", str(text))
    if not cleaned or cleaned in ("-", ".", "-."):
        return None
    try:
        return float(cleaned)
    except Exception:
        return None


def parse_int(text):
    number = parse_float(text)
    if number is None:
        return None
    return int(number)


def parse_rules_json(raw_rules):
    raw_rules = unwrap_body(raw_rules)
    if isinstance(raw_rules, dict):
        return raw_rules, ""
    if isinstance(raw_rules, str) and raw_rules.strip():
        try:
            parsed = json.loads(raw_rules)
        except Exception as exc:
            return {}, f"rules_json parse failed: {exc}"
        if isinstance(parsed, dict):
            return parsed, ""
        return {}, "rules_json parsed but is not an object"
    return {}, "rules_json is empty or missing"


def load_rules(params):
    raw_rules = find_param(params, ("rules_json", "Rules_JSON", "rules_body", "body"))
    rules, warning = parse_rules_json(raw_rules)
    if not rules:
        return minimal_fallback_rules(), warning or "using minimal fallback rules"
    if not isinstance(rules.get("rules"), list):
        return minimal_fallback_rules(), "rules_json missing rules list; using minimal fallback rules"
    return rules, warning


def collect_pdp(params):
    price = text_param(params, "sales_price", "price", "product_price", "sale_price", "min_price", "Product_min_price")
    shipping_fee = text_param(params, "shipping_fee", "shipping", "freight", "postage")
    landed = None
    price_number = parse_float(price)
    shipping_number = parse_float(shipping_fee)
    if price_number is not None or shipping_number is not None:
        landed = (price_number or 0) + (shipping_number or 0)
    return {
        "product_id": text_param(params, "product_id", "Product_id", "item_id"),
        "title": text_param(params, "product_name", "title", "product_title", "Product_title"),
        "description": text_param(params, "product_desc", "description", "product_description", "desc"),
        "category": text_param(params, "first_category_name", "product_category", "category", "Product_category"),
        "brand_name": text_param(params, "brand_name", "brand", "Product_brand"),
        "seller_name": text_param(params, "shop_name", "seller_name", "store_name"),
        "platform_badges": text_param(params, "is_official_tag", "has_flash_sale", "is_free_shipping_fee"),
        "price": price,
        "list_price_usd": text_param(params, "list_price_usd", "list_price", "original_price"),
        "shipping_fee": shipping_fee,
        "currency": text_param(params, "currency", "Product_currency"),
        "target_country": text_param(params, "target_country"),
        "target_currency": text_param(params, "target_currency"),
        "exchange_rate_to_target_currency": text_param(params, "exchange_rate_to_target_currency"),
        "exchange_rate_date": text_param(params, "exchange_rate_date"),
        "sales_price_local": text_param(params, "sales_price_local"),
        "list_price_local": text_param(params, "list_price_local"),
        "shipping_fee_local": text_param(params, "shipping_fee_local"),
        "landed_cost_usd": text_param(params, "landed_cost_usd"),
        "landed_cost_local": text_param(params, "landed_cost_local"),
        "localized_price_context": text_param(params, "localized_price_context"),
        "landed_cost": "" if landed is None else str(round(landed, 2)),
        "rating": text_param(params, "avg_review_star_td", "rating", "product_rating", "review_rating"),
        "avg_star_rating": text_param(params, "avg_star_rating"),
        "recent_review_contents": text_param(params, "review_contents", "recent_review_contents", "raw_review_contents"),
        "review_count": text_param(params, "review_cnt_td", "comment_cnt_td", "review_count", "reviews_count", "rating_count"),
        "category_rating_p10": text_param(params, "category_rating_p10", "p10"),
        "category_rating_p50": text_param(params, "category_rating_p50", "p50"),
        "reviews_text": text_param(params, "review_contents", "comment_summary_text", "comment_30d_emotion", "reviews_text", "review_text", "comments_text", "buyer_reviews"),
        "sku": text_param(params, "sku_cnt", "sku", "sku_info", "variant_info"),
        "specs": text_param(params, "prd_basic_info_score", "is_main_img_firstimg_quality", "with_image_comment_ratio", "specs", "specifications", "attributes"),
        "delivery_info": text_param(params, "shop_info", "delivery_info", "fulfillment_info", "shipping_info"),
        "logistics_info": text_param(params, "logistics_info"),
        "governance_metrics": text_param(params, "governance_metrics"),
        "digital_delivery": text_param(params, "digital_delivery", "redeem_info", "redemption_info"),
        "face_value": text_param(params, "face_value", "card_value", "voucher_value"),
        "excel_metric_context": text_param(params, "excel_metric_context"),
    }


def normalized_text(pdp):
    return " ".join(str(value or "") for value in pdp.values()).lower()


def contains_any(text, keywords):
    return any(contains_term(text, keyword) for keyword in keywords or [])


def contains_term(text, keyword):
    keyword = str(keyword or "").strip().lower()
    if not keyword:
        return False
    if re.search(r"[a-z0-9]", keyword):
        return re.search(r"(?<![a-z0-9])" + re.escape(keyword) + r"(?![a-z0-9])", text) is not None
    return keyword in text


def matched_rule_ids_for_rule(rule, tags, text):
    applies = [str(x).lower() for x in rule.get("applies_to", [])]
    if "all" in applies:
        return True
    rule_id = str(rule.get("id", "")).upper()
    ipr_rule_ids = {"IPR-01", "IPR-02"}
    ipr_tags = {
        "ipr",
        "ip",
        "ipr_authorization_ladder",
        "unsupported_official_claim",
        "clear_ipr_with_weak_authorization",
        "streetwear_brand_ip",
    }
    if rule_id in ipr_rule_ids:
        return any(tag.lower() in ipr_tags for tag in tags)
    for tag in tags:
        if tag.lower() in applies:
            return True
    for term in applies:
        if term and term in text:
            return True
    return False


def infer_tags(rules, pdp):
    hints = rules.get("routing_hints", {})
    text = normalized_text(pdp)
    tags = set(["all"])
    broad_level_1_exclusions = {"battery", "charger", "power bank", "phone", "computer"}
    level_1_keywords = [kw for kw in hints.get("level_1_keywords", []) if kw not in broad_level_1_exclusions]
    if contains_any(text, level_1_keywords):
        tags.add("level_1")
    if contains_any(text, hints.get("level_2_keywords")):
        tags.add("level_2")
    if contains_any(text, hints.get("level_4_5_keywords")):
        tags.add("level_4_5")
    if contains_any(text, hints.get("digital_keywords")):
        tags.update(["digital", "digital code", "gift card"])
    if contains_any(text, hints.get("tcg_keywords")):
        tags.update(["tcg", "collectible", "trading card"])
    if detect_used_refurbished_condition(pdp):
        tags.update(["used", "refurbished"])
    if contains_any(text, hints.get("custom_keywords")):
        tags.update(["custom", "handmade"])
    if contains_any(text, hints.get("regulated_keywords")):
        tags.update(["regulated", "adult", "weapon"])
    if contains_any(text, hints.get("big_brand_keywords")):
        tags.update(["brand", "luxury", "fragrance", "sneaker", "strong genuine market"])

    category = (pdp.get("category") or "").lower()
    title = (pdp.get("title") or "").lower()
    desc = (pdp.get("description") or "").lower()
    title_category_desc = " ".join([title, category, desc])
    if any(contains_term(title_category_desc, term) for term in ("food", "beverage", "snack", "candy", "supplement", "vitamin", "protein")):
        tags.update(["food", "supplement", "perishable"])
    if any(contains_term(title_category_desc, term) for term in ("beauty", "skin", "makeup", "hair", "personal care", "shaver", "razor", "grooming")):
        tags.add("beauty")
    if any(contains_term(title_category_desc, term) for term in ("fragrance", "perfume", "cologne", "scent", "eau de parfum", "eau de toilette")):
        tags.add("fragrance")
    if any(contains_term(title_category_desc, term) for term in ("baby", "kids", "child", "pet")):
        tags.update(["baby", "pet"])
    if any(contains_term(title_category_desc, term) for term in ("kid", "kids", "child", "children", "toddler", "baby")):
        tags.update(["child", "child_safety", "safety"])
    power_core_terms = (
        "power bank",
        "portable charger",
        "wall charger",
        "phone charger",
        "battery pack",
        "power supply",
        "power adapter",
        "charging adapter",
        "outlet",
        "socket",
        "extension cord",
        "usb-c charger",
    )
    if any(contains_term(title_category_desc, term) for term in power_core_terms):
        tags.update(["power", "charger", "safety"])
    if pdp.get("reviews_text"):
        tags.add("reviews")
    if pdp.get("price") or pdp.get("shipping_fee"):
        tags.update(["price", "shipping"])
    if parse_float(pdp.get("price")) == 0:
        tags.update(["zero_price", "price"])
    if pdp.get("category_rating_p10") or pdp.get("category_rating_p50"):
        tags.update(["category_rating_p10", "category_rating_p50"])
    if detect_auction_listing(pdp):
        tags.update(["auction_listing", "auction"])
    if detect_claim_review_conflict(pdp):
        tags.update(["claim_review_conflict", "misleading"])
    if detect_page_spec_conflict(pdp):
        tags.update(["page_spec_conflict", "misleading"])
    if detect_child_safety(pdp):
        tags.update(["child_safety", "safety"])
    if detect_food_packaging_risk(pdp):
        tags.update(["food_packaging_risk", "food", "perishable"])
    if detect_body_harm(pdp):
        tags.update(["body_harm", "safety"])
    if detect_recent_rating_downshift(pdp):
        tags.update(["recent_rating_downshift", "reviews", "quality"])
    if has_recent_review_contents(pdp):
        tags.update(["recent_review_contents", "reviews", "quality"])
    if detect_streetwear_brand_ip(pdp):
        tags.update(["brand", "streetwear_brand_ip", "strong genuine market"])
    if detect_shipping_claim_mismatch(pdp):
        tags.update(["shipping_claim_mismatch", "misleading", "shipping"])
    if detect_safety_related_reviews(pdp):
        tags.update(["safety_related_review", "safety"])
    if detect_visible_image_text_consistency_issue(pdp):
        tags.update(["visible_image_text_consistency", "page_spec_conflict", "misleading"])
    if detect_ipr_authorization_ladder(pdp):
        tags.update(["ipr_authorization_ladder", "ipr", "ip", "brand"])
    if detect_unsupported_official_claim(pdp):
        tags.update(["unsupported_official_claim", "official", "licensed", "authentic"])
    if detect_clear_ipr_with_weak_authorization(pdp):
        tags.update(["clear_ipr_with_weak_authorization", "ipr_authorization_ladder", "ipr", "brand"])
    if detect_score_5_candidate(pdp):
        tags.update(["score_5_candidate", "review_volume_absorbs_limited_negatives"])
    if detect_score_5_blocker(pdp):
        tags.update(["score_5_blocker"])
    if detect_sparse_review_objective_issue_cap(pdp):
        tags.update(["sparse_review_objective_issue_cap", "reviews", "quality", "fulfillment"])
    if detect_hard_claim_spec_conflict(pdp):
        tags.update(["hard_claim_spec_conflict", "hard_misleading_conflict", "page_spec_conflict", "misleading"])
    if detect_official_backing_protection_boundary(pdp):
        tags.update(["official_backing_protection_boundary", "official", "channel"])
    return sorted(tags)


def detect_auction_listing(pdp):
    text = normalized_text(pdp)
    price = parse_float(pdp.get("price"))
    auction_terms = ("auction", "bid", "bidding", "no cancellations", "no cancellation")
    return contains_any(text, auction_terms) or (price == 0 and contains_any(text, ("no cancellations", "auction", "bid")))


def detect_used_refurbished_condition(pdp):
    title_category_desc = " ".join(
        [
            pdp.get("title", ""),
            pdp.get("category", ""),
            pdp.get("description", ""),
            pdp.get("sku", ""),
        ]
    ).lower()
    condition_patterns = (
        r"\brefurbished\b",
        r"\brenewed\b",
        r"\bpre[-\s]?owned\b",
        r"\bopen[-\s]?box\b",
        r"\bused\s+(condition|item|phone|device|product|goods|grade)\b",
        r"\bsecond[-\s]?hand\b",
        r"\bcondition\s+grade\b",
        r"\bgrade\s+[abc]\b",
        r"\bdefect\s+disclosed\b",
    )
    return any(re.search(pattern, title_category_desc) for pattern in condition_patterns)


def detect_claim_review_conflict(pdp):
    title_desc = " ".join([pdp.get("title", ""), pdp.get("description", "")]).lower()
    reviews = (pdp.get("reviews_text") or "").lower()
    if not title_desc or not reviews:
        return False
    claim_terms = (
        "heavy duty",
        "50000mah",
        "50,000mah",
        "high capacity",
        "fast charging",
        "multilingual translation",
        "translation",
        "waterproof",
        "strong suction",
        "large water tank",
        "200kg",
        "safety net",
        "wobble-free",
    )
    conflict_terms = (
        "below",
        "lower than",
        "appears below",
        "unreliable",
        "unsafe",
        "not secure",
        "don't stay secure",
        "doesn't stay secure",
        "not padded",
        "wobbly",
        "wobble",
        "leak",
        "missing",
        "not as described",
        "actual capacity",
        "slow charging",
        "struggle to hold charge",
        "run hot",
        "falls",
        "fall off",
    )
    return contains_any(title_desc, claim_terms) and contains_any(reviews, conflict_terms)


def detect_page_spec_conflict(pdp):
    text = normalized_text(pdp)
    conflict_markers = (
        "mismatch",
        "inconsistent",
        "conflict",
        "different from",
        "vs",
        "servings",
        "pads",
        "pieces",
        "capacity",
    )
    title_desc = " ".join([pdp.get("title", ""), pdp.get("description", "")]).lower()
    has_count_or_capacity = re.search(r"\b\d+\s?(mah|servings|pads|pieces|pcs|kg|w|ml|l)\b", title_desc) is not None
    return has_count_or_capacity and contains_any(text, conflict_markers) and contains_any(text, ("mismatch", "inconsistent", "conflict", "vs", "different"))


def detect_child_safety(pdp):
    text = normalized_text(pdp)
    if not contains_any(text, ("kid", "kids", "child", "children", "toddler", "baby")):
        return False
    return contains_any(
        text,
        (
            "safety net",
            "spring cover",
            "zip",
            "padding",
            "padded",
            "not secure",
            "don't stay secure",
            "doesn't stay secure",
            "loose",
            "unstable",
            "wobbly",
        ),
    )


def detect_food_packaging_risk(pdp):
    text = normalized_text(pdp)
    if not contains_any(text, ("food", "supplement", "protein", "creatine", "candy", "sweet", "drink", "beverage", "ingestible")):
        return False
    return contains_any(text, ("open", "opened", "leaking", "leak", "broken seal", "damaged packaging", "packaging arriving", "replacement", "spoiled", "contaminated"))


def detect_body_harm(pdp):
    text = normalized_text(pdp)
    if not contains_any(text, ("beauty", "personal care", "lash", "serum", "skin", "hair", "body", "health", "face")):
        return False
    return contains_any(
        text,
        (
            "irritation",
            "redness",
            "burning",
            "burn",
            "scald",
            "allergy",
            "allergic",
            "rash",
            "overheating",
            "electric shock",
            "eye injury",
            "stye",
            "chemical leak",
            "leaking chemical",
            "unsafe applicator",
            "structural failure",
            "bodily harm",
            "injury",
        ),
    )


def detect_recent_rating_downshift(pdp):
    rating = parse_float(pdp.get("rating"))
    avg_star = parse_float(pdp.get("avg_star_rating"))
    review_count = parse_int(pdp.get("review_count"))
    if rating is None or avg_star is None:
        return False
    if review_count is not None and review_count < 30:
        return False
    return avg_star <= rating - 0.3


def has_recent_review_contents(pdp):
    return bool((pdp.get("recent_review_contents") or "").strip())


def detect_streetwear_brand_ip(pdp):
    text = normalized_text(pdp)
    return contains_any(
        text,
        (
            "hellstar",
            "hell star",
            "heaven hell",
            "dark streetwear",
            "star flame",
            "flame graphic",
            "vintage dark streetwear",
        ),
    )


def detect_shipping_claim_mismatch(pdp):
    title_desc = " ".join([pdp.get("title", ""), pdp.get("description", "")]).lower()
    if not contains_any(title_desc, ("free shipping", "free delivery", "free postage")):
        return False
    shipping = parse_float(pdp.get("shipping_fee"))
    return shipping is not None and shipping > 0


def detect_safety_related_reviews(pdp):
    text = normalized_text(pdp)
    return contains_any(
        text,
        (
            "shoots real flame",
            "real flame",
            "fire",
            "overheat",
            "overheating",
            "run hot",
            "heating up",
            "charging port",
            "charge port",
            "cannot power on",
            "won't power on",
            "e04",
            "unsafe",
            "flagged unsafe",
            "burning",
            "red eye",
            "stye",
            "leaking applicator",
            "battery safety",
            "certification",
            "protection missing",
        ),
    )


def detect_visible_image_text_consistency_issue(pdp):
    text = normalized_text(pdp)
    if contains_any(text, ("free shipping", "free delivery")) and detect_shipping_claim_mismatch(pdp):
        return True
    quantity_conflict_pairs = (
        ("60 ml", "20 ml"),
        ("60ml", "20ml"),
        ("1 pack", "2 pack"),
        ("buy 1 get 1", "received one"),
        ("buy one get one", "received one"),
    )
    return any(a in text and b in text for a, b in quantity_conflict_pairs)


def has_official_channel_evidence(pdp):
    badge = (pdp.get("platform_badges") or "").lower()
    seller = (pdp.get("seller_name") or "").lower()
    brand = (pdp.get("brand_name") or "").lower()
    if re.search(r"(^|[^0-9])1([^0-9]|$)", badge):
        return True
    if brand and brand not in ("no brand", "none", "null", "unknown") and brand in seller and contains_any(seller, ("official", "uk", "store", "shop")):
        return True
    return False


def detect_ipr_authorization_ladder(pdp):
    text = normalized_text(pdp)
    ip_terms = (
        "ipr",
        "licensed",
        "pokemon",
        "k-pop",
        "demon hunters",
        "huntrix",
        "makita",
        "mobilgas",
        "owala",
        "crocs",
        "major league baseball",
        "padres",
        "aladdin",
        "jasmine",
        "princess",
        "grey's anatomy",
        "character",
        "cartoon",
    )
    return contains_any(text, ip_terms)


def detect_unsupported_official_claim(pdp):
    text = normalized_text(pdp)
    claim_terms = ("official", "licensed", "authentic", "genuine", "authorized")
    return contains_any(text, claim_terms) and not has_official_channel_evidence(pdp)


def detect_clear_ipr_with_weak_authorization(pdp):
    text = normalized_text(pdp)
    weak_channel = not has_official_channel_evidence(pdp)
    strong_ip_terms = (
        "makita",
        "pokemon",
        "k-pop demon hunters",
        "huntrix",
        "grey's anatomy",
        "major league baseball",
        "padres",
        "aladdin",
        "jasmine princess",
    )
    return weak_channel and contains_any(text, strong_ip_terms)


def detect_score_5_candidate(pdp):
    rating = parse_float(pdp.get("rating"))
    avg_star = parse_float(pdp.get("avg_star_rating"))
    if rating is None or avg_star is None:
        return False
    if rating < 4.6 or avg_star < 4.6:
        return False
    return not detect_score_5_blocker(pdp)


def detect_score_5_blocker(pdp):
    return any(
        [
            detect_ipr_authorization_ladder(pdp) and not has_official_channel_evidence(pdp),
            detect_claim_review_conflict(pdp),
            detect_page_spec_conflict(pdp),
            detect_hard_claim_spec_conflict(pdp),
            detect_safety_related_reviews(pdp),
            detect_sparse_review_objective_issue_cap(pdp),
            detect_recent_rating_downshift(pdp),
        ]
    )


def detect_sparse_review_objective_issue_cap(pdp):
    review_count = parse_int(pdp.get("review_count"))
    if review_count is None or review_count >= 10:
        return False
    text = normalized_text(pdp)
    issue_terms = (
        "missing parts",
        "missing part",
        "arrived missing",
        "leaked",
        "leaking",
        "wrong item",
        "not as described",
        "broken",
        "does not work",
        "doesn't work",
        "failed",
        "unsafe",
        "damaged",
        "quality issue",
        "poor quality",
    )
    return contains_any(text, issue_terms)


def detect_hard_claim_spec_conflict(pdp):
    text = normalized_text(pdp)
    hard_terms = (
        "misleading",
        "refurbished",
        "renewed",
        "repair",
        "repaired",
        "description mismatch",
        "not match",
        "does not match",
        "quantity mismatch",
        "volume mismatch",
        "core information missing",
        "tooth whitening",
        "teeth whitening",
        "missing ingredients",
        "missing safety",
    )
    return contains_any(text, hard_terms) or detect_visible_image_text_consistency_issue(pdp)


def detect_official_backing_protection_boundary(pdp):
    text = normalized_text(pdp)
    return has_official_channel_evidence(pdp) or contains_any(text, ("official", "brand flagship", "authorized", "authentic"))


def infer_category_level(pdp, tags):
    if any(tag in tags for tag in ("digital", "digital code", "gift card", "food", "supplement", "baby", "pet", "power", "charger", "luxury", "sneaker", "collectible", "tcg")):
        return "Level 1: very high trust sensitivity or high direct-loss sensitivity"
    if any(tag in tags for tag in ("beauty", "fragrance", "safety")):
        return "Level 2: high trust sensitivity"
    if "level_4_5" in tags:
        return "Level 4-5 candidate: low brand sensitivity style or disposable low-risk goods"
    return "Level 3 default candidate: medium trust sensitivity unless PDP evidence shows higher or lower risk"


def format_rule(rule):
    return f"{rule.get('id', '')} {rule.get('name', '')}: {rule.get('text', '')}".strip()


def select_rules(rules, pdp, tags):
    text = normalized_text(pdp)
    selected = []
    for rule in rules.get("rules", []):
        if matched_rule_ids_for_rule(rule, tags, text):
            selected.append(rule)
    required_ids = {"CORE-01", "CORE-02", "CORE-03", "CORE-04", "PAGE-01", "RULECAP-01", "BEND-01", "OUTPUT-01"}
    existing = {rule.get("id") for rule in selected}
    for rule in rules.get("rules", []):
        if rule.get("id") in required_ids and rule.get("id") not in existing:
            selected.append(rule)
    return selected


def infer_review_warning(pdp):
    review_count = parse_int(pdp.get("review_count"))
    rating = parse_float(pdp.get("rating"))
    avg_star = parse_float(pdp.get("avg_star_rating"))
    p10 = parse_float(pdp.get("category_rating_p10"))
    p50 = parse_float(pdp.get("category_rating_p50"))
    parts = []
    if review_count is None:
        parts.append("review_count missing: do not penalize by itself; use PDP evidence and category sensitivity")
    elif review_count == 0:
        parts.append("0 reviews: not automatic negative; Level 1/2 white labels need more caution")
    elif review_count < 10:
        parts.append("1-9 reviews: tiny sample; read all visible comments; do not mechanically use p10/p50 or one ordinary complaint for score 2")
    elif review_count < 30:
        parts.append("10-29 reviews: small sample; rating matters but comment content still controls")
    elif review_count < 100:
        parts.append("30-99 reviews: medium sample; below p10 is meaningful but brand/channel and complaint severity decide 2 vs 3")
    else:
        parts.append("100+ reviews: rating percentile and repeated complaints are stable evidence")
    if rating is not None and p10 is not None:
        if rating < p10:
            parts.append(f"rating {rating} is below category p10 {p10}: strong negative if review sample is not tiny")
        elif rating <= p10 + 0.1:
            parts.append(f"rating {rating} is near category p10 {p10}: cautious, especially white-label or high-sensitivity goods")
    if rating is not None and p50 is not None:
        if rating >= p50 + 0.2:
            parts.append(f"rating {rating} is clearly above category p50 {p50}: positive review signal, not red-flag override")
        elif rating < p50:
            parts.append(f"rating {rating} is below category p50 {p50}: ordinary weak to weak review signal")
    if avg_star is not None:
        parts.append(f"avg_star_rating {avg_star}: recent-review signal; use only for negative calibration against avg_review_star_td, not for score upgrades")
    if pdp.get("recent_review_contents"):
        parts.append("review_contents shows direct recent buyer text; evaluate it under quality reliability first and use it to confirm whether recent rating signals reflect objective product, fulfillment, safety, or PDP-claim problems")
    if rating is not None and avg_star is not None:
        if review_count is not None and review_count >= 30 and avg_star <= rating - 0.3:
            parts.append("recent rating downshift: avg_star_rating is meaningfully lower than avg_review_star_td on a non-tiny sample; treat as recent deterioration and consider downgrading quality or final score if comments support it")
        elif avg_star > rating:
            parts.append("higher recent avg_star_rating must not upgrade the score or override avg_review_star_td; keep avg_review_star_td as the primary historical rating")
        if rating >= 4.6 and avg_star >= 4.6:
            parts.append("score 5 gate: both historical and recent ratings are at least 4.6; score 5 can be considered only if review_contents has no objective quality, fulfillment, safety, IPR, authorization, or hard claim-conflict blocker")
        elif rating < 4.6 or avg_star < 4.6:
            parts.append("score 5 caution: at least one of historical or recent rating is below 4.6, so score 5 needs unusually strong clean evidence and usually score 4 is the safer high-trust ceiling")
    if detect_sparse_review_objective_issue_cap(pdp):
        parts.append("sparse objective issue cap: review sample is sparse and contains objective quality or fulfillment issues; usually cap final score at 3 unless strong official/channel/page evidence proves the issue is isolated and low impact")
    return "; ".join(parts)


def infer_price_warning(pdp, tags):
    price = parse_float(pdp.get("price"))
    list_price = parse_float(pdp.get("list_price_usd"))
    shipping = parse_float(pdp.get("shipping_fee"))
    face_value = parse_float(pdp.get("face_value"))
    parts = []
    if pdp.get("landed_cost"):
        parts.append(f"landed_cost = product price + shipping = {pdp.get('landed_cost')} {pdp.get('currency') or ''}".strip())
    else:
        parts.append("landed_cost missing or partially missing: judge value from visible price/shipping fields only")
    if price == 0:
        parts.append("sales_price=0 appears to be missing or polluted price data: do not evaluate value from sales_price=0, do not treat it as strong value or low-price bait by itself")
    if pdp.get("localized_price_context"):
        parts.append(pdp.get("localized_price_context"))
    elif pdp.get("currency") == "USD" or pdp.get("price"):
        parts.append("price_input_semantics missing; use Final_data_cleaning localized_price_context when available; UK prices are native GBP, DE/FR/ES/IT prices are USD converted to EUR")
    if "shipping_claim_mismatch" in tags:
        parts.append("shipping_fee conflicts with free shipping claim in title or PDP text; lower page_quality and consider authenticity_delivery/fulfillment risk")
    if list_price is not None and price is not None and list_price > 0:
        discount_ratio = 1 - (price / list_price)
        if discount_ratio >= 0.5:
            parts.append("sales_price is less than half of list_price_usd; check whether this is credible promotion, ordinary discount, low-price bait, or strong-brand risk")
        elif discount_ratio > 0:
            parts.append("sales_price is below list_price_usd; treat as a possible value signal only after trust is credible")
    if price is not None and shipping is not None and price > 0:
        ratio = shipping / (price + shipping) if (price + shipping) > 0 else 0
        if ratio >= 0.35:
            parts.append("shipping is a large share of landed cost; check low-price bait or poor value, especially for small/light goods")
    if "digital" in tags and face_value is not None and price is not None:
        if price < face_value * 0.85:
            parts.append("digital code price is far below face value; treat as trust risk unless channel/reviews strongly explain it")
        elif price > face_value:
            parts.append("digital code price exceeds face value; value is weak unless extra value is explained")
        else:
            parts.append("digital code price is near face value; value is usually neutral if delivery/redeem trust holds")
    return "; ".join(parts)


def build_locale_context(rules, pdp):
    target_country = (pdp.get("target_country") or "").upper()
    profiles = rules.get("locale_profiles") or {}
    profile = profiles.get(target_country)
    if not profile:
        return (
            f"target_country={target_country or 'missing'} is unsupported; "
            "supported target countries are UK, DE, FR, ES, IT; do not silently fallback to UK"
        )

    tolerated = ", ".join(profile.get("tolerated_languages", []))
    localized_price = pdp.get("localized_price_context") or "localized price context missing"
    exchange = rules.get("exchange_rate_baseline") or {}
    return "\n".join(
        [
            "TARGET_COUNTRY_LOCALE_CONTEXT",
            f"target_country={target_country}",
            f"buyer_persona={profile.get('buyer_persona', '')}",
            f"primary_language={profile.get('primary_language', '')}",
            f"tolerated_languages={tolerated}",
            f"target_currency={profile.get('target_currency', pdp.get('target_currency', ''))}",
            f"exchange_rate_source={exchange.get('source', 'Frankfurter API')}",
            f"exchange_rate_date={exchange.get('date', pdp.get('exchange_rate_date', ''))}",
            f"exchange_rate_to_target_currency={pdp.get('exchange_rate_to_target_currency', '')}",
            f"localized_price_context={localized_price}",
            f"strict_language_rule={profile.get('strict_language_rule', '')}",
            f"language_tolerance={profile.get('language_tolerance', '')}",
            f"value_judgment={profile.get('value_judgment', '')}",
            "target-country strict language rule: core PDP info in non-target primary language without target-language translation means page_quality <= 3; only brand names, model names, international measurement units, and non-critical decorative text may remain outside the primary language without penalty.",
        ]
    )


def infer_risk_hints(pdp, tags):
    text = normalized_text(pdp)
    triggered = []
    checklist = []

    def add_trigger(name, message, legacy_name=""):
        label = name
        if legacy_name:
            label = f"{name} / {legacy_name}"
        triggered.append(f"{label}: {message}")

    def add_check(name, message):
        checklist.append(f"{name}: {message}")

    add_check("category_sensitivity_hint", infer_category_level(pdp, tags))
    if "digital" in tags:
        add_check("digital_code_overlay_check", "evaluate official/authorized channel, delivery method, face value, region, currency, expiry, restrictions, refund policy, works/redeemed reviews, invalid/already redeemed/never received/scam reviews")
    if "tcg" in tags:
        add_check("tcg_overlay_check", "secondary circulation is normal; pulls bad/no hits are not wrong item; focus on unit, series, language, version, sealed state, count, fake/resealed/tampered/wrong item/missing packs/not as described")
    if "used" in tags or "refurbished" in tags:
        add_check("used_refurbished_check", "transparent disclosure can be normal; hidden condition or new-product imagery that misleads lowers authenticity_delivery")
    if "custom" in tags or "handmade" in tags:
        add_check("custom_overlay_check", "page must explain customization input, material, size, timing, and return/cancel limits")
    if "brand" in tags or "luxury" in tags or "fragrance" in tags or "sneaker" in tags:
        add_check("strong_brand_channel_check", "brand, luxury, fragrance, sneaker, or strong-genuine-market goods need channel and visual-trade-dress checking; do not treat this reminder as proof of risk")
    if any(tag in tags for tag in ("beauty", "personal care", "health")) or contains_any(text, ("ipl", "laser hair removal", "skin", "body-contact", "body contact", "lash", "serum", "hair removal")):
        add_check("body_contact_category_check", "body-contact or efficacy beauty goods need safety and review-content checking; this reminder is not evidence that harm exists")
    if pdp.get("brand_name") or has_official_channel_evidence(pdp):
        add_check("ipr_authorization_ladder_check", "if IP, logo, official identity, or brand authenticity is core to the transaction, check authorization ladder; this reminder is not proof of IPR risk")
    if detect_official_backing_protection_boundary(pdp):
        add_check("official_backing_boundary_check", "official or brand backing can protect authenticity/delivery confidence, but cannot override hard evidence of IPR, unsupported claims, safety, repeated quality failure, or misleading conflict")
    if any(term in text for term in ("official", "authentic", "genuine", "authorized", "licensed", "1:1", "replica", "same as original")):
        if detect_unsupported_official_claim(pdp):
            add_trigger("unsupported_official_claim_signal", "official/licensed/authentic/genuine/authorized wording appears without matching shop/channel proof; cap at 3 by default and downgrade only with abnormal price, strong imitation, weak white-label evidence, or strong impersonation", "unsupported_official_claim_attention")
        else:
            add_check("official_authentic_claim_check", "verify whether PDP channel and evidence support official/authentic/authorized identity; supported claims are not negative evidence")
    if any(term in text for term in ("fake", "counterfeit", "not genuine", "not authentic", "invalid code", "already redeemed", "never received", "scam", "not as described", "wrong item", "missing parts", "resealed", "tampered")):
        add_trigger("hard_review_terms_signal", "review/PDP text contains hard terms such as fake, counterfeit, invalid code, already redeemed, never received, scam, not as described, wrong item, missing parts, resealed, or tampered; inspect repeat rate and evidence strength")
    if "claim_review_conflict" in tags:
        add_trigger("claim_review_conflict_signal", "title/images/description emphasize a core promise but review text conflicts with that promise; do not keep score 4, lower authenticity_delivery and quality, and cap high-risk categories at 3 unless conflict is isolated", "claim_review_conflict_attention")
    if "page_spec_conflict" in tags:
        add_trigger("page_spec_conflict_signal", "visible quantity/spec/capacity/accessory inconsistency should lower page_quality first and authenticity_delivery if it affects what the buyer receives", "page_spec_conflict_attention")
    if "child_safety" in tags:
        add_trigger("child_safety_cap_signal", "child-use products with insecure safety net, padding, zip, spring cover, frame, or stability evidence should lower safety; if safety is 2, final score cannot exceed 3", "child_safety_cap_attention")
    if "food_packaging_risk" in tags:
        add_trigger("food_packaging_risk_signal", "ingestible packaging opened/leaking/damaged/replacement evidence lowers quality and can cap final score at 3 if edibility or food-safety trust is affected", "food_packaging_risk_attention")
    if "body_harm" in tags:
        add_trigger("body_harm_nuance_signal", "mild inherent reaction can be a small downgrade, but clear bodily harm to the user from avoidable product failure means the final score must not exceed 3; concentrated injury complaints can support score 2", "body_harm_nuance_attention")
    if "zero_price" in tags:
        add_trigger("zero_price_pollution_signal", "sales_price=0 is missing or polluted value data for normal PDPs; set value around neutral unless other price evidence exists", "zero_price_pollution_attention")
    if "auction_listing" in tags:
        add_trigger("auction_exclusion_signal", "auction or bidding listing is not comparable to fixed-price PDP Trust Score; exclude from calibration or explain not comparable if forced to score", "auction_exclusion_attention")
    if "recent_rating_downshift" in tags:
        add_trigger("recent_rating_downshift_signal", "avg_review_star_td is the primary historical rating; avg_star_rating is meaningfully lower, so use it only to downgrade or increase caution, not to upgrade", "recent_rating_downshift_attention")
    if "recent_review_contents" in tags:
        add_trigger("recent_review_contents_signal", "review_contents is available as latest buyer text for quality reliability; downgrade only for objective, repeated, or severe product/function/packaging/fulfillment/safety/PDP-claim issues", "recent_review_contents_attention")
    if "streetwear_brand_ip" in tags:
        add_trigger("streetwear_brand_ip_signal", "dark streetwear, Hellstar-like heaven/hell/star/flame motifs, or celebrity streetwear references can be strong brand/IP risk even when brand_name is empty; inspect images and title before treating it as ordinary generic apparel", "streetwear_brand_ip_attention")
    if "shipping_claim_mismatch" in tags:
        add_trigger("shipping_claim_mismatch_signal", "title/PDP claims free shipping or free delivery but shipping_fee is positive; treat as visible claim mismatch and lower page_quality, with authenticity_delivery impact if it affects buyer landed cost", "shipping_claim_mismatch_attention")
    if "safety_related_review" in tags:
        add_trigger("safety_related_review_signal", "reviews or PDP mention fire/flame/overheating/charging failure/app flagged unsafe/eye injury/battery certification gaps; safety must not remain 5 unless evidence is clearly irrelevant or isolated misuse", "safety_related_review_attention")
    if "visible_image_text_consistency" in tags:
        add_trigger("visible_image_text_consistency_signal", "compare product_name/title against readable image/package/detail text for volume, count, free shipping, buy one get one, included items, and core specs; mismatch lowers page_quality and may lower authenticity_delivery", "visible_image_text_consistency_attention")
    if "ipr_authorization_ladder" in tags:
        if detect_unsupported_official_claim(pdp) or detect_clear_ipr_with_weak_authorization(pdp):
            add_trigger("ipr_authorization_ladder_signal", "IP/brand/character/team/logo-core identity appears with weak or unsupported authorization evidence; apply authorization ladder before allowing score above 3", "ipr_authorization_ladder_attention")
        else:
            add_check("ipr_authorization_ladder_check", "IP/brand/character/team/logo-core goods require authorization ladder checking; this reminder is not proof that IPR risk exists")
    if "unsupported_official_claim" in tags:
        add_trigger("unsupported_official_claim_signal", "official/licensed/authentic/genuine/authorized wording is not proof by itself; if shop/channel evidence does not support it, cap at 3 by default and downgrade to 2 only with abnormal price, strong visual imitation, weak white-label evidence, or strong official impersonation", "unsupported_official_claim_attention")
    if "clear_ipr_with_weak_authorization" in tags:
        add_trigger("clear_ipr_with_weak_authorization_signal", "known IP or brand identity appears central while channel proof is weak; treat as clear IPR risk unless PDP provides credible authorization", "clear_ipr_with_weak_authorization_attention")
    if "score_5_candidate" in tags:
        add_trigger("score_5_candidate_signal", "avg_review_star_td and avg_star_rating are both at least 4.6 and no obvious hard blocker was detected; score 5 can be considered if page, channel, claim consistency, safety, and review_contents remain clean", "score_5_candidate_attention")
    if "score_5_blocker" in tags:
        add_trigger("score_5_blocker_signal", "do not give score 5 when objective quality/fulfillment negatives, IPR or authorization risk, hard claim conflict, safety concern, recent rating downshift, or sparse objective issue remains unresolved", "score_5_blocker_attention")
    rating = parse_float(pdp.get("rating"))
    avg_star = parse_float(pdp.get("avg_star_rating"))
    if rating is not None and avg_star is not None and (rating < 4.6 or avg_star < 4.6):
        add_trigger("score_5_blocker_signal", "at least one of avg_review_star_td or avg_star_rating is below 4.6, so score 5 needs unusually strong clean evidence and score 4 is usually the safer high-trust ceiling")
    if "sparse_review_objective_issue_cap" in tags:
        add_trigger("sparse_review_objective_issue_cap_signal", "sparse review evidence plus objective product, fulfillment, missing-part, leaking, wrong-item, core-function, or safety complaints usually caps final score at 3 unless strong evidence proves it is isolated and low impact", "sparse_review_objective_issue_cap_attention")
    if "hard_claim_spec_conflict" in tags:
        add_trigger("hard_claim_spec_conflict_signal", "clear core-claim or core-information conflict can override positive social proof; cap at 3, and consider 2 if the conflict affects what the buyer receives or sensitive safety/food/body-contact trust", "hard_claim_spec_conflict_attention")
    if "official_backing_protection_boundary" in tags:
        add_check("official_backing_protection_boundary_check", "official or brand backing protects authenticity and delivery confidence, but cannot override clear IPR risk, unsupported official claims, hard claim conflicts, safety concerns, repeated core quality failures, or strong misleading evidence")
    if not pdp.get("description") and not pdp.get("specs"):
        add_trigger("page_gap_signal", "description/specs appear missing; this matters more for high-sensitivity, digital, collectible, beauty, electronics, child/pet, or detail-dependent goods", "page_gap_attention")
    add_check("b_end_reason_guard", "output b_end_reasons only if score <4 and cause is clear; max 3 exact strings")

    lines = [
        "TRIGGERED DETERMINISTIC SIGNALS",
        "These are field, price, review-text, or explicit-claim signals detected by code. They are not final judgments, but must be checked carefully against PDP-visible evidence.",
    ]
    if triggered:
        lines.extend(f"- {hint}" for hint in triggered)
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "CHECKLIST REMINDERS ONLY",
            "These reminders come from category, brand, or workflow context. Do not treat them as evidence that a risk exists.",
        ]
    )
    if checklist:
        lines.extend(f"- {hint}" for hint in checklist)
    else:
        lines.append("- none")
    return "\n".join(lines)


def infer_evidence_gaps(pdp, rules_warning):
    gaps = []
    if rules_warning:
        gaps.append(f"rules_json warning: {rules_warning}")
    for key, label in (
        ("category", "product_category missing; category level must rely on title/images/specs"),
        ("brand_name", "brand_name missing; do not penalize by itself"),
        ("seller_name", "seller_name missing; channel judgment may be limited"),
        ("price", "price missing; value judgment limited"),
        ("shipping_fee", "shipping_fee missing; landed cost incomplete"),
        ("reviews_text", "reviews_text missing; do not invent review content"),
        ("sku", "SKU/variant info missing; identity/spec clarity may be limited"),
    ):
        if not pdp.get(key):
            gaps.append(label)
    if not gaps:
        gaps.append("no obvious metadata gap from Rules Brain; still rely on PDP-visible evidence and images")
    return "\n".join(f"- {gap}" for gap in gaps)


def build_rules_context(rules, pdp, selected_rules, tags, warning):
    lines = []
    lines.append("PDP_TRUST_SCORE_RULES_CONTEXT")
    lines.append(f"rules_version: {rules.get('version', '')}")
    lines.append(f"category_sensitivity_hint: {infer_category_level(pdp, tags)}")
    lines.append("Use this context as high-priority routing guidance. Use PDP-visible image/text/review evidence for the actual judgment.")
    lines.append("Do not average the six dimensions. First set trust baseline, then apply value adjustment.")
    lines.append("If any Stage 1 red flag is established or compliance is 2 or below, final score must be 1 or 2.")
    lines.append("Safety and compliance default to 5 and only go down when evidence triggers them.")
    lines.append("Do not punish unknown brand, empty brand_name, no reviews, ordinary white label, polished images, no backend data, or no price anchor by themselves.")
    lines.append("Machine JSON must only contain authenticity_delivery, safety, quality, value, compliance, page_quality, score, and optional b_end_reasons.")
    lines.append("Use locale_context for target-country role, strict primary-language rule, and localized GBP/EUR value reasoning.")
    lines.append("Apply target-country strict language rule: core PDP info in non-target primary language without target-language translation means page_quality <= 3; only brand names, model names, international measurement units, and non-critical decorative text may remain outside the primary language without penalty.")
    if warning:
        lines.append(f"rules_warning: {warning}")
    lines.append("")
    lines.append("Selected rules:")
    for rule in selected_rules:
        lines.append("- " + format_rule(rule))
    lines.append("")
    lines.append("Allowed B-end reasons:")
    for reason in rules.get("allowed_b_end_reasons", ALLOWED_B_END_REASONS):
        lines.append("- " + reason)
    return "\n".join(lines)


def build_matched_rules(selected_rules):
    return ", ".join(rule.get("id", "") for rule in selected_rules if rule.get("id"))


def build_debug_summary(pdp, tags):
    keys = ["product_id", "title", "category", "brand_name", "seller_name", "price", "list_price_usd", "shipping_fee", "currency", "target_country", "target_currency", "landed_cost_usd", "landed_cost_local", "rating", "avg_star_rating", "review_count", "category_rating_p10", "category_rating_p50"]
    lines = ["PDP_FIELD_SUMMARY"]
    for key in keys:
        value = pdp.get(key, "")
        if value:
            lines.append(f"{key}: {value}")
    lines.append("routing_tags: " + ", ".join(tags))
    return "\n".join(lines)


def build_output(params):
    rules, warning = load_rules(params)
    pdp = collect_pdp(params)
    tags = infer_tags(rules, pdp)
    selected_rules = select_rules(rules, pdp, tags)
    locale_context = build_locale_context(rules, pdp)
    review_warning = infer_review_warning(pdp)
    price_warning = infer_price_warning(pdp, tags)
    risk_hints = infer_risk_hints(pdp, tags)
    evidence_gaps = infer_evidence_gaps(pdp, warning)
    return {
        "rules_context": build_rules_context(rules, pdp, selected_rules, tags, warning),
        "matched_rules": build_matched_rules(selected_rules),
        "locale_context": locale_context,
        "risk_hints": risk_hints,
        "evidence_gaps": evidence_gaps,
        "review_context": review_warning,
        "price_context": price_warning,
        "rules_version": str(rules.get("version", "")),
        "rules_source_warning": warning,
        "pdp_debug_summary": build_debug_summary(pdp, tags),
    }


async def main(args: Args) -> Output:
    params = args.params
    ret = build_output(params)
    return ret
