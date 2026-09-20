import json
import re


VERSION = "2026-08-17-v1"
NULL_STRINGS = {"", "null", "NULL", "None", "none", "nan", "NaN"}


def clean_text(value):
    if value is None:
        return ""
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    text = str(value).strip()
    if text in NULL_STRINGS:
        return ""
    return text


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


def get_text(params, *names):
    return clean_text(find_param(params, names))


def parse_json_like(value):
    if isinstance(value, (list, dict)):
        return value
    text = clean_text(value)
    if not text or text[0] not in "[{":
        return None
    try:
        return json.loads(text)
    except Exception:
        return None


def parse_images(value):
    parsed = parse_json_like(value)
    if isinstance(parsed, list):
        return [clean_text(item) for item in parsed if clean_text(item)]
    if isinstance(value, list):
        return [clean_text(item) for item in value if clean_text(item)]
    text = clean_text(value)
    if not text:
        return []
    urls = []
    for candidate in re.split(r"[\n,;|]+", text):
        candidate = candidate.strip()
        if candidate.startswith(("http://", "https://")) and candidate not in urls:
            urls.append(candidate)
    return urls


def parse_float(value):
    text = clean_text(value)
    if not text:
        return None
    cleaned = re.sub(r"[^0-9.\-]", "", text)
    if cleaned in {"", "-", ".", "-."}:
        return None
    try:
        return float(cleaned)
    except Exception:
        return None


def parse_int(value):
    number = parse_float(value)
    if number is None:
        return None
    return int(number)


def yes_no(condition):
    return "yes" if condition else "no"


def has_text(params, *names):
    return bool(get_text(params, *names))


def trim(text, limit=520):
    text = re.sub(r"\s+", " ", clean_text(text)).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def build_landed_cost(params):
    price = parse_float(get_text(params, "sales_price"))
    shipping = parse_float(get_text(params, "shipping_fee"))
    if price is None and shipping is None:
        return ""
    total = (price or 0) + (shipping or 0)
    return str(round(total, 2))


def build_case_state(params, images):
    landed_cost = build_landed_cost(params)
    parts = [
        "Context Builder status for single-LLM PDP Trust evaluation.",
        f"product_id={get_text(params, 'product_id') or 'missing'}",
        f"product_name={trim(get_text(params, 'product_name'), 180) or 'missing'}",
        f"category={get_text(params, 'first_category_name') or 'missing'}",
        f"brand_name={get_text(params, 'brand_name') or 'missing'}",
        f"shop_name={get_text(params, 'shop_name') or 'missing'}",
        f"target_country={get_text(params, 'target_country') or 'missing'}",
        f"target_currency={get_text(params, 'target_currency') or 'missing'}",
        f"is_official_tag={get_text(params, 'is_official_tag') or 'missing'}",
        f"sales_price={get_text(params, 'sales_price') or 'missing'}",
        f"shipping_fee={get_text(params, 'shipping_fee') or 'missing'}",
        f"currency={get_text(params, 'currency') or 'missing'}",
        f"landed_cost={landed_cost or 'missing'}",
        f"localized_price_context={trim(get_text(params, 'localized_price_context'), 220) or 'missing'}",
        f"review_cnt_td={get_text(params, 'review_cnt_td', 'comment_cnt_td') or 'missing'}",
        f"avg_review_star_td={get_text(params, 'avg_review_star_td') or 'missing'}",
        f"avg_star_rating={get_text(params, 'avg_star_rating') or 'missing'}",
        f"images_count={len(images)}",
        f"image_sources=product_main_images and size_chart_images are separate source lists when provided; images is the combined visual list",
    ]
    return "\n".join(parts)


def build_evidence_manifest(params, images):
    matched_rules = get_text(params, "matched_rules")
    risk_hints = get_text(params, "risk_hints")
    evidence_gaps = get_text(params, "evidence_gaps")
    rules_review_context = get_text(params, "rules_review_context", "review_context")
    price_context = get_text(params, "price_context")
    locale_context = get_text(params, "locale_context")
    localized_price_context = get_text(params, "localized_price_context")
    product_desc = get_text(params, "product_desc")
    review_contents = get_text(params, "review_contents")
    comment_summary = get_text(params, "comment_summary_text")
    governance = get_text(params, "governance_metrics")

    manifest = [
        "Evidence manifest. Treat these as orientation notes, not as extra rules.",
        f"images_count={len(images)}",
        f"image_source={get_text(params, 'image_source') or 'missing'}",
        f"product_desc_present={yes_no(bool(product_desc))}",
        f"review_contents_present={yes_no(bool(review_contents))}",
        f"comment_summary_present={yes_no(bool(comment_summary))}",
        f"governance_metrics_present={yes_no(bool(governance))}",
        f"rules_context_present={yes_no(has_text(params, 'rules_context'))}",
        f"matched_rules={matched_rules or 'none'}",
        f"risk_hints={risk_hints or 'none'}",
        f"evidence_gaps={evidence_gaps or 'none'}",
        f"locale_context={trim(locale_context, 700) or 'missing'}",
        f"localized_price_context={trim(localized_price_context, 500) or 'missing'}",
        f"rules_review_context={trim(rules_review_context, 700) or 'none'}",
        f"price_context={trim(price_context, 500) or 'none'}",
        f"recent_review_contents_sample={trim(review_contents, 700) or 'missing'}",
    ]
    return "\n".join(manifest)


def build_decision_checklist(params, images):
    rating = parse_float(get_text(params, "avg_review_star_td"))
    recent_rating = parse_float(get_text(params, "avg_star_rating"))
    review_count = parse_int(get_text(params, "review_cnt_td", "comment_cnt_td"))
    checklist = [
        "Decision checklist for the single Trust_Evaluator LLM.",
        "1. Start from category sensitivity and special overlays; do not average the six dimensions.",
        "2. Use rules_context as high-priority guidance and body as fallback rulebook.",
        "3. Use evidence_manifest to avoid missing image count, review text, price, shipping, and evidence gaps.",
        "4. Use target-country language and value context: role, strict primary-language rule, localized GBP/EUR landed cost, returns/warranty, plug/voltage, compatibility, and digital redemption region.",
        "5. Visible image/text consistency: compare title, product_main_images, size_chart_images, detail images, quantity, capacity, free shipping, promotion, included items, and core specs.",
        "6. Review calibration: avg_review_star_td is the primary historical rating; avg_star_rating only supports negative recent downshift, not upgrade.",
        "7. Score 5 gate: require strong trust, clear PDP, healthy reviews, no objective review problem, no safety/IPR/authorization/core-claim/fulfillment instability.",
        "8. Safety hard caps: child-use, powered, battery, heating, eye-contact, ingestible, and body-contact risks need explicit safety consistency checking.",
        "9. IPR authorization ladder: clear IPR without credible authorization usually 2; suspected IPR without strong proof usually 3; above 3 needs credible official or authorization proof.",
        "10. If score is below 4, b_end_reasons must be exact allowed Chinese strings and max 3.",
        "11. RESULT JSON may contain only authenticity_delivery, safety, quality, value, compliance, page_quality, score, and optional b_end_reasons.",
    ]
    if not images:
        checklist.append("Runtime attention: no image URLs reached the LLM; do not pretend visual PDP evidence exists.")
    if rating is not None and recent_rating is not None and review_count is not None and review_count >= 30:
        if recent_rating <= rating - 0.3:
            checklist.append("Runtime attention: avg_star_rating is meaningfully lower than avg_review_star_td; check review_contents before downgrade.")
        elif recent_rating > rating:
            checklist.append("Runtime attention: higher recent avg_star_rating must not upgrade beyond historical rating and rule evidence.")
    if parse_float(get_text(params, "sales_price")) == 0:
        checklist.append("Runtime attention: sales_price=0 should be treated as missing or polluted price data, not value evidence or low-price bait by itself.")
    return "\n".join(checklist)


def build_debug(params, images):
    return "; ".join(
        [
            f"context_builder_version={VERSION}",
            f"target_country={get_text(params, 'target_country') or 'missing'}",
            f"target_currency={get_text(params, 'target_currency') or 'missing'}",
            f"images_count={len(images)}",
            f"has_rules_context={yes_no(has_text(params, 'rules_context'))}",
            f"has_risk_hints={yes_no(has_text(params, 'risk_hints'))}",
            f"has_review_contents={yes_no(has_text(params, 'review_contents'))}",
            f"has_product_desc={yes_no(has_text(params, 'product_desc'))}",
        ]
    )


def build_output(params):
    images = parse_images(find_param(params, ("images", "Product_images", "product_images")))
    return {
        "case_state": build_case_state(params, images),
        "evidence_manifest": build_evidence_manifest(params, images),
        "decision_checklist": build_decision_checklist(params, images),
        "context_builder_debug": build_debug(params, images),
    }


async def main(args: Args) -> Output:
    params = args.params
    ret = build_output(params)
    return ret
