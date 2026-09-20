import html
import json
import re


NULL_STRINGS = {"", "null", "NULL", "None", "none", "nan", "NaN"}
SUPPORTED_TARGET_COUNTRIES = {"UK", "DE", "FR", "ES", "IT"}
TARGET_CURRENCY_BY_COUNTRY = {
    "UK": "GBP",
    "DE": "EUR",
    "FR": "EUR",
    "ES": "EUR",
    "IT": "EUR",
}
EXCHANGE_RATE_TO_TARGET_CURRENCY = {
    "GBP": 0.73874,
    "EUR": 0.86453,
}
EXCHANGE_RATE_DATE = "2026-08-14"
EXCHANGE_RATE_SOURCE = "Frankfurter API"


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


def html_to_text(raw_html):
    text = clean_text(raw_html)
    if not text:
        return ""
    text = re.sub(r"<script[\s\S]*?</script>", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def maybe_json(value):
    value = clean_text(value)
    if not value:
        return None
    if value[0] not in "[{":
        return None
    try:
        return json.loads(value)
    except Exception:
        return None


def split_url_list(value):
    if isinstance(value, list):
        return extract_urls_recursive(value)
    parsed = maybe_json(value)
    if isinstance(parsed, list):
        return extract_urls_recursive(parsed)
    if isinstance(parsed, dict):
        return extract_urls_recursive(parsed)
    text = clean_text(value)
    if not text:
        return []
    candidates = re.split(r"[\n,;|]+", text)
    return [clean_text(x) for x in candidates if clean_text(x).startswith(("http://", "https://"))]


def dedupe_preserve_order(values):
    deduped = []
    seen = set()
    for value in values:
        text = clean_text(value)
        if not text or not text.startswith(("http://", "https://")) or text in seen:
            continue
        deduped.append(text)
        seen.add(text)
    return deduped


def keep_valid_urls(values):
    urls = []
    for value in values:
        text = clean_text(value)
        if text.startswith(("http://", "https://")):
            urls.append(text)
    return urls


def parse_jsonish(value, max_depth=4):
    current = value
    for _ in range(max_depth):
        if isinstance(current, (list, dict)):
            return current
        text = clean_text(current)
        if not text:
            return None
        try:
            parsed = json.loads(text)
        except Exception:
            return text
        current = parsed
    return current


def extract_img_urls_from_html(raw_html):
    text = clean_text(raw_html)
    urls = []
    if not text:
        return urls
    for pattern in (r'<img[^>]+src="([^"]+)"', r"<img[^>]+src='([^']+)'"):
        for url in re.findall(pattern, text, flags=re.IGNORECASE):
            cleaned = clean_text(url)
            if cleaned and cleaned not in urls:
                urls.append(cleaned)
    return urls


def extract_urls_recursive(value):
    urls = []
    if isinstance(value, str):
        parsed = maybe_json(value)
        if parsed is not None:
            return extract_urls_recursive(parsed)
        text = clean_text(value)
        if text.startswith(("http://", "https://")):
            return [text]
        return []
    if isinstance(value, list):
        for item in value:
            for url in extract_urls_recursive(item):
                urls.append(url)
        return urls
    if isinstance(value, dict):
        url_keys = ("url", "uri", "image", "image_url", "origin_url", "originUrl", "thumb_url", "display_url")
        handled_keys = set()
        for key in url_keys:
            if key in value:
                handled_keys.add(key)
                for url in extract_urls_recursive(value.get(key)):
                    urls.append(url)
        for key, item in value.items():
            if key in handled_keys:
                continue
            for url in extract_urls_recursive(item):
                urls.append(url)
    return urls


def unwrap_rpc_payload(value):
    if isinstance(value, str):
        parsed = maybe_json(value)
        if parsed is not None:
            return unwrap_rpc_payload(parsed)
        return value
    if isinstance(value, dict):
        for key in ("output", "body", "data"):
            if key in value:
                return unwrap_rpc_payload(value.get(key))
    return value


def get_result_object(payload):
    payload = unwrap_rpc_payload(payload)
    if isinstance(payload, dict):
        if isinstance(payload.get("result"), dict):
            return payload.get("result")
        if isinstance(payload.get("Result"), dict):
            return payload.get("Result")
    return payload if isinstance(payload, dict) else {}


def has_product_extra_attributes_payload(params):
    extra_attribute_keys = (
        "product_extra_attributes",
        "product_extra_attributes_rpc",
        "product_extra_attributes_output",
        "extra_attributes",
        "extra_attributes_output",
        "product_extra_attributes.product_attributes",
        "product_extra_attributes.product_attributes.feature_value",
        "product_extra_attributes.size_chart",
        "product_extra_attributes.size_chart.feature_value",
    )
    extra_feature_codes = (
        "product_extra_attributes.product_attributes",
        "product_extra_attributes.size_chart",
        "product_attributes",
        "size_chart",
    )

    def contains_extra_attributes(value):
        if isinstance(value, str):
            parsed = maybe_json(value)
            if parsed is not None:
                return contains_extra_attributes(parsed)
            return False
        if isinstance(value, list):
            return any(contains_extra_attributes(item) for item in value)
        if not isinstance(value, dict):
            return False

        if any(key in value for key in extra_attribute_keys):
            return True
        if clean_text(value.get("feature_code")) in extra_feature_codes:
            return True
        return any(contains_extra_attributes(child) for child in value.values())

    return contains_extra_attributes(params)


def get_explicit_image_rpc_payload(params):
    image_keys = (
        "rpc_images",
        "ecom_output",
        "product_image_rpc",
        "product_image_rpc_output",
        "image_rpc",
        "image_rpc_output",
        "ProductMeta_images",
        "rpc_input",
    )
    for key in image_keys:
        if key in params:
            return params.get(key)

    if has_product_extra_attributes_payload(params):
        return None

    for key in ("output", "input"):
        if key in params:
            return params.get(key)
    return None


def extract_rpc_images(params):
    raw_rpc = get_explicit_image_rpc_payload(params)
    if isinstance(raw_rpc, (list, str)):
        direct_urls = split_url_list(raw_rpc)
        if direct_urls:
            return direct_urls

    result = get_result_object(raw_rpc)
    candidates = []
    if isinstance(result, dict):
        if "ecom_output" in result:
            candidates.append(result.get("ecom_output"))
        literal = result.get("ProductMeta.images")
        if isinstance(literal, dict):
            candidates.append(literal.get("feature_value"))
        elif literal is not None:
            candidates.append(literal)
        nested = result.get("ProductMeta")
        if isinstance(nested, dict):
            images = nested.get("images")
            if isinstance(images, dict):
                candidates.append(images.get("feature_value"))
            elif images is not None:
                candidates.append(images)
        for value in result.values():
            if isinstance(value, dict) and value.get("feature_code") in ("images", "ProductMeta.images"):
                candidates.append(value.get("feature_value"))
    for candidate in candidates:
        urls = split_url_list(candidate)
        if urls:
            return urls
    generic_urls = split_url_list(result)
    if generic_urls:
        return generic_urls
    generic_urls = split_url_list(raw_rpc)
    if generic_urls:
        return generic_urls
    recursive_urls = find_product_meta_images_recursive(params)
    if recursive_urls:
        return recursive_urls
    return []


def build_product_main_images(params):
    return keep_valid_urls(extract_rpc_images(params))


def extract_feature_value_by_code(value, accepted_codes):
    if isinstance(value, str):
        parsed = maybe_json(value)
        if parsed is not None:
            return extract_feature_value_by_code(parsed, accepted_codes)
        return None
    if isinstance(value, list):
        for item in value:
            found = extract_feature_value_by_code(item, accepted_codes)
            if found is not None:
                return found
        return None
    if not isinstance(value, dict):
        return None

    feature_code = clean_text(value.get("feature_code"))
    if feature_code in accepted_codes and "feature_value" in value:
        return value.get("feature_value")

    for child in value.values():
        found = extract_feature_value_by_code(child, accepted_codes)
        if found is not None:
            return found
    return None


def extract_nested_value(value, dotted_key):
    current = value
    for part in dotted_key.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current.get(part)
    return current


def extract_feature_value_from_result(result, literal_key, feature_code):
    if not isinstance(result, dict):
        return None

    feature_value_key = literal_key + ".feature_value"
    if feature_value_key in result:
        return result.get(feature_value_key)

    if literal_key in result:
        node = result.get(literal_key)
        if isinstance(node, dict) and "feature_value" in node:
            return node.get("feature_value")
        return node

    nested_value = extract_nested_value(result, feature_value_key)
    if nested_value is not None:
        return nested_value

    nested_node = extract_nested_value(result, literal_key)
    if isinstance(nested_node, dict) and "feature_value" in nested_node:
        return nested_node.get("feature_value")
    if nested_node is not None:
        return nested_node

    accepted_codes = {literal_key, feature_code, literal_key.rsplit(".", 1)[-1]}
    return extract_feature_value_by_code(result, accepted_codes)


def extract_product_extra_result(params):
    raw_rpc = find_param(
        params,
        (
            "product_extra_attributes",
            "product_extra_attributes_rpc",
            "product_extra_attributes_output",
            "extra_attributes",
            "extra_attributes_output",
        ),
    )
    return get_result_object(raw_rpc)


def parse_product_attributes(value):
    parsed = parse_jsonish(value)
    if isinstance(parsed, dict) and "feature_value" in parsed:
        parsed = parse_jsonish(parsed.get("feature_value"))
    if not isinstance(parsed, list):
        return []

    normalized = []
    for item in parsed:
        item = parse_jsonish(item)
        if not isinstance(item, dict):
            continue
        label = clean_text(
            item.get("label")
            or item.get("name")
            or item.get("key")
            or item.get("attribute_name")
            or item.get("attributeLabel")
        )
        value_text = clean_text(
            item.get("value")
            or item.get("attribute_value")
            or item.get("attributeValue")
            or item.get("feature_value")
        )
        if label or value_text:
            normalized.append({"label": label, "value": value_text})
    return normalized


def build_extra_attributes(params):
    result = extract_product_extra_result(params)
    product_attributes_value = extract_feature_value_from_result(
        result,
        "product_extra_attributes.product_attributes",
        "product_extra_attributes.product_attributes",
    )
    size_chart_value = extract_feature_value_from_result(
        result,
        "product_extra_attributes.size_chart",
        "product_extra_attributes.size_chart",
    )

    product_attributes = parse_product_attributes(product_attributes_value)
    product_attributes_text = "; ".join(
        f"{item['label']}={item['value']}" if item["label"] else item["value"]
        for item in product_attributes
        if item.get("label") or item.get("value")
    )
    product_attributes_json = json.dumps(product_attributes, ensure_ascii=False) if product_attributes else ""
    size_chart_images = dedupe_preserve_order(split_url_list(size_chart_value))

    source_parts = [
        f"product_attributes={'yes' if product_attributes else 'no'}",
        f"size_chart_images_count={len(size_chart_images)}",
    ]
    if not product_attributes and not size_chart_images:
        source_parts.append("missing_product_extra_attributes")

    return {
        "product_attributes_text": product_attributes_text,
        "product_attributes_json": product_attributes_json,
        "size_chart_images": size_chart_images,
        "extra_attributes_source": "; ".join(source_parts),
    }


def find_product_meta_images_recursive(value):
    if isinstance(value, str):
        parsed = maybe_json(value)
        if parsed is not None:
            return find_product_meta_images_recursive(parsed)
        return []
    if isinstance(value, list):
        for item in value:
            urls = find_product_meta_images_recursive(item)
            if urls:
                return urls
        return []
    if not isinstance(value, dict):
        return []

    if "ProductMeta.images" in value:
        node = value.get("ProductMeta.images")
        if isinstance(node, dict) and "feature_value" in node:
            urls = split_url_list(node.get("feature_value"))
        else:
            urls = split_url_list(node)
        if urls:
            return urls

    if value.get("feature_code") in ("images", "ProductMeta.images") and "feature_value" in value:
        urls = split_url_list(value.get("feature_value"))
        if urls:
            return urls

    for child in value.values():
        urls = find_product_meta_images_recursive(child)
        if urls:
            return urls
    return []


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


def format_money(value):
    if value is None:
        return ""
    return f"{value:.2f}"


def parse_bool_flag(value):
    text = clean_text(value)
    if text in {"1", "1.0", "true", "True", "YES", "yes", "Y", "y"}:
        return True
    if text in {"0", "0.0", "false", "False", "NO", "no", "N", "n"}:
        return False
    return None


def join_nonempty(parts, sep="; "):
    cleaned = [clean_text(x) for x in parts]
    return sep.join(x for x in cleaned if x)


def normalize_target_country(params):
    return get_text(params, "target_country", "Target_country", "targetCountry").upper()


def build_localized_price_fields(params):
    target_country = normalize_target_country(params)
    sales_price = parse_float(get_text(params, "sales_price"))
    list_price = parse_float(get_text(params, "list_price_usd"))
    shipping_fee = parse_float(get_text(params, "shipping_fee"))
    landed_cost = None
    if sales_price is not None or shipping_fee is not None:
        landed_cost = (sales_price or 0.0) + (shipping_fee or 0.0)

    if target_country not in SUPPORTED_TARGET_COUNTRIES:
        context = (
            f"unsupported target_country={target_country or 'missing'}; "
            "supported values are UK, DE, FR, ES, IT; no local currency conversion applied"
        )
        return {
            "target_country": target_country,
            "target_currency": "UNSUPPORTED",
            "exchange_rate_to_target_currency": "",
            "exchange_rate_date": EXCHANGE_RATE_DATE,
            "sales_price_local": "",
            "list_price_local": "",
            "shipping_fee_local": "",
            "landed_cost_usd": format_money(landed_cost),
            "landed_cost_local": "",
            "localized_price_context": context,
        }

    target_currency = TARGET_CURRENCY_BY_COUNTRY[target_country]
    rate = EXCHANGE_RATE_TO_TARGET_CURRENCY[target_currency]

    sales_local = None if sales_price is None else sales_price * rate
    list_local = None if list_price is None else list_price * rate
    shipping_local = None if shipping_fee is None else shipping_fee * rate
    landed_local = None if landed_cost is None else landed_cost * rate

    context_parts = [
        f"target_country={target_country}",
        "input_currency=USD",
        f"target_currency={target_currency}",
        f"exchange_rate_source={EXCHANGE_RATE_SOURCE}",
        f"exchange_rate_date={EXCHANGE_RATE_DATE}",
        f"exchange_rate=1 USD to {format_money(rate)} {target_currency}",
    ]
    if sales_price is not None:
        context_parts.append(f"sales_price={format_money(sales_price)} USD -> {format_money(sales_local)} {target_currency}")
    if list_price is not None:
        context_parts.append(f"list_price_usd={format_money(list_price)} USD -> {format_money(list_local)} {target_currency}")
    if shipping_fee is not None:
        context_parts.append(f"shipping_fee={format_money(shipping_fee)} USD -> {format_money(shipping_local)} {target_currency}")
    if landed_cost is not None:
        context_parts.append(f"landed_cost={format_money(landed_cost)} USD -> {format_money(landed_local)} {target_currency}")
    if sales_price == 0:
        context_parts.append("sales_price=0 should be treated as missing or polluted price data, not as value evidence or low-price bait by itself")

    return {
        "target_country": target_country,
        "target_currency": target_currency,
        "exchange_rate_to_target_currency": str(rate),
        "exchange_rate_date": EXCHANGE_RATE_DATE,
        "sales_price_local": format_money(sales_local),
        "list_price_local": format_money(list_local),
        "shipping_fee_local": format_money(shipping_local),
        "landed_cost_usd": format_money(landed_cost),
        "landed_cost_local": format_money(landed_local),
        "localized_price_context": "; ".join(context_parts),
    }


def build_logistics_info(params):
    return join_nonempty(
        [
            f"is_free_shipping_fee={get_text(params, 'is_free_shipping_fee')}" if get_text(params, "is_free_shipping_fee") else "",
            f"shipping_fee={get_text(params, 'shipping_fee')}" if get_text(params, "shipping_fee") else "",
            f"has_flash_sale={get_text(params, 'has_flash_sale')}" if get_text(params, "has_flash_sale") else "",
            f"is_free_return={get_text(params, 'is_free_return')}" if get_text(params, "is_free_return") else "",
        ]
    )


def build_shop_info(params):
    return join_nonempty(
        [
            f"shop_name={get_text(params, 'shop_name')}" if get_text(params, "shop_name") else "",
            f"is_official_tag={get_text(params, 'is_official_tag')}" if get_text(params, "is_official_tag") else "",
            f"shop_final_score={get_text(params, 'shop_final_score')}" if get_text(params, "shop_final_score") else "",
            f"shop_sales={get_text(params, 'shop_sales')}" if get_text(params, "shop_sales") else "",
            f"shop_fans={get_text(params, 'shop_fans')}" if get_text(params, "shop_fans") else "",
        ]
    )


def build_governance_metrics(params):
    return join_nonempty(
        [
            f"onnr15={get_text(params, 'onnr15')}" if get_text(params, "onnr15") else "",
            f"onnr30={get_text(params, 'onnr30')}" if get_text(params, "onnr30") else "",
        ]
    )


def build_review_context(params):
    return join_nonempty(
        [
            f"comment_cnt_td={get_text(params, 'comment_cnt_td')}" if get_text(params, "comment_cnt_td") else "",
            f"avg_review_star_td={get_text(params, 'avg_review_star_td')}" if get_text(params, "avg_review_star_td") else "",
            f"avg_star_rating={get_text(params, 'avg_star_rating')}" if get_text(params, "avg_star_rating") else "",
            f"review_contents={get_text(params, 'review_contents')}" if get_text(params, "review_contents") else "",
            f"cl_pay_sub_order_cnt={get_text(params, 'cl_pay_sub_order_cnt')}" if get_text(params, "cl_pay_sub_order_cnt") else "",
            f"with_image_comment_ratio={get_text(params, 'with_image_comment_ratio')}" if get_text(params, "with_image_comment_ratio") else "",
            f"comment_summary_text={get_text(params, 'comment_summary_text')}" if get_text(params, "comment_summary_text") else "",
            f"comment_30d_emotion={get_text(params, 'comment_30d_emotion')}" if get_text(params, "comment_30d_emotion") else "",
        ]
    )


def build_images(params):
    product_main_images = build_product_main_images(params)
    extra_attributes = build_extra_attributes(params)
    size_chart_images = extra_attributes["size_chart_images"]
    images = dedupe_preserve_order(product_main_images + size_chart_images)

    if product_main_images and size_chart_images:
        image_source = "rpc_ProductMeta.images+product_extra_attributes.size_chart"
    elif product_main_images:
        image_source = "rpc_ProductMeta.images"
    elif size_chart_images:
        image_source = "missing_product_main_images+product_extra_attributes.size_chart"
    else:
        image_source = "missing_product_main_images"

    image_manifest = "; ".join(
        [
            f"product_main_images_count={len(product_main_images)}",
            f"size_chart_images_count={len(size_chart_images)}",
            "order=product_main_images_then_size_chart_images_deduped",
        ]
    )
    return {
        "product_main_images": product_main_images,
        "size_chart_images": size_chart_images,
        "images": images,
        "image_source": image_source,
        "image_manifest": image_manifest,
        "extra_attributes": extra_attributes,
    }


def build_debug_mapping(params, output):
    source_columns = [
        "product_id",
        "product_name",
        "brand_name",
        "first_category_name",
        "shop_name",
        "comment_30d_emotion",
        "ext_price_tag",
        "first_image",
        "product_desc",
        "comment_summary_text",
        "review_contents",
        "is_official_tag",
        "is_free_shipping_fee",
        "has_flash_sale",
        "is_free_return",
        "sku_cnt",
        "shop_sales",
        "shop_fans",
        "comment_cnt_td",
        "cl_pay_sub_order_cnt",
        "review_cnt_td",
        "pv_rank",
        "video_product_show_cnt",
        "is_main_img_firstimg_quality",
        "prd_basic_info_score",
        "list_price_usd",
        "sales_price",
        "shop_final_score",
        "avg_review_star_td",
        "with_image_comment_ratio",
        "avg_star_rating",
        "shipping_fee",
        "onnr15",
        "onnr30",
        "target_country",
    ]
    present = [col for col in source_columns if clean_text(find_param(params, (col,)))]
    return (
        "source_columns_present="
        + ",".join(present)
        + f"; images_count={len(output.get('images', []))}"
        + f"; product_main_images_count={len(output.get('product_main_images', []))}"
        + f"; size_chart_images_count={len(output.get('size_chart_images', []))}"
        + f"; image_source={output.get('image_source', '')}"
        + f"; extra_attributes_source={output.get('extra_attributes_source', '')}"
    )


def build_output(params):
    product_desc = html_to_text(find_param(params, ("product_desc",)))
    image_fields = build_images(params)
    extra_attributes = image_fields["extra_attributes"]
    localized_price_fields = build_localized_price_fields(params)
    output = {
        "product_id": get_text(params, "product_id"),
        "product_name": get_text(params, "product_name"),
        "images": image_fields["images"],
        "product_main_images": image_fields["product_main_images"],
        "size_chart_images": image_fields["size_chart_images"],
        "image_source": image_fields["image_source"],
        "image_manifest": image_fields["image_manifest"],
        "product_attributes_text": extra_attributes["product_attributes_text"],
        "product_attributes_json": extra_attributes["product_attributes_json"],
        "extra_attributes_source": extra_attributes["extra_attributes_source"],
        "product_desc": product_desc,
        "brand_name": get_text(params, "brand_name"),
        "first_category_name": get_text(params, "first_category_name"),
        "sku_cnt": get_text(params, "sku_cnt"),
        "is_main_img_firstimg_quality": get_text(params, "is_main_img_firstimg_quality"),
        "prd_basic_info_score": get_text(params, "prd_basic_info_score"),
        "list_price_usd": get_text(params, "list_price_usd"),
        "sales_price": get_text(params, "sales_price"),
        "shop_name": get_text(params, "shop_name"),
        "is_official_tag": get_text(params, "is_official_tag"),
        "shop_final_score": get_text(params, "shop_final_score"),
        "shop_sales": get_text(params, "shop_sales"),
        "shop_fans": get_text(params, "shop_fans"),
        "comment_cnt_td": get_text(params, "comment_cnt_td"),
        "review_cnt_td": get_text(params, "review_cnt_td"),
        "avg_review_star_td": get_text(params, "avg_review_star_td"),
        "avg_star_rating": get_text(params, "avg_star_rating"),
        "review_contents": get_text(params, "review_contents"),
        "cl_pay_sub_order_cnt": get_text(params, "cl_pay_sub_order_cnt"),
        "with_image_comment_ratio": get_text(params, "with_image_comment_ratio"),
        "comment_summary_text": get_text(params, "comment_summary_text"),
        "comment_30d_emotion": get_text(params, "comment_30d_emotion"),
        "is_free_shipping_fee": get_text(params, "is_free_shipping_fee"),
        "shipping_fee": get_text(params, "shipping_fee"),
        "has_flash_sale": get_text(params, "has_flash_sale"),
        "is_free_return": get_text(params, "is_free_return"),
        "onnr15": get_text(params, "onnr15"),
        "onnr30": get_text(params, "onnr30"),
        "currency": "USD",
        "target_country": localized_price_fields["target_country"],
        "target_currency": localized_price_fields["target_currency"],
        "exchange_rate_to_target_currency": localized_price_fields["exchange_rate_to_target_currency"],
        "exchange_rate_date": localized_price_fields["exchange_rate_date"],
        "sales_price_local": localized_price_fields["sales_price_local"],
        "list_price_local": localized_price_fields["list_price_local"],
        "shipping_fee_local": localized_price_fields["shipping_fee_local"],
        "landed_cost_usd": localized_price_fields["landed_cost_usd"],
        "landed_cost_local": localized_price_fields["landed_cost_local"],
        "localized_price_context": localized_price_fields["localized_price_context"],
        "shop_info": build_shop_info(params),
        "review_context": build_review_context(params),
        "logistics_info": build_logistics_info(params),
        "governance_metrics": build_governance_metrics(params),
    }
    output["final_data_cleaning_debug"] = build_debug_mapping(params, output)
    return output


async def main(args: Args) -> Output:
    params = args.params
    ret = build_output(params)
    return ret
