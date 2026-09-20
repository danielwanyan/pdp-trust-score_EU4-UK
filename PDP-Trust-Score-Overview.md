# PDP Trust Score EU4+UK Overview

`pdp-trust-score_EU4-UK` is the isolated merged UK+EU4 PDP Trust Score copybook.

GitHub repository:

```text
https://github.com/danielwanyan/pdp-trust-score_EU4-UK
```

## Purpose

The workflow evaluates whether a careful local TikTok Shop buyer would trust a PDP enough to buy. It is not a pure violation detector and it is not a six-field arithmetic average. The primary axis is user purchase trust: authenticity, delivery, PDP honesty, quality reliability, value, safety, and compliance.

Supported target countries:

```text
UK, DE, FR, ES, IT
```

Each country has its own locale profile. `target_country` controls buyer role, primary language, price semantics, and local value expectations.

## Architecture

The active workflow is a single product per invocation and one product per workflow call.

```text
Start / Excel row
  -> product_image_rpc
  -> product_extra_attributes_rpc
  -> Final_data_cleaning
  -> rules_json_fetch / rules_text_fetch
  -> Rules_Brain
  -> Context_Builder
  -> Trust_Evaluator
  -> End
```

The active workflow has exactly one LLM node: `Trust_Evaluator`. It has only one LLM in the production path.

## Main Inputs

`product_image_rpc` reads `ProductMeta.images` and `Final_data_cleaning` preserves all returned URLs in `product_main_images`. These images may include ordinary main images, detail long images, selling-point images, package images, and specification images.

`product_extra_attributes_rpc` reads:

```text
product_extra_attributes.product_attributes
product_extra_attributes.size_chart
```

`Final_data_cleaning` exposes `product_attributes_text`, `size_chart_images`, `image_manifest`, and combined `images` for model visual input.

## Localized Scoring

Strict target-country language localization applies to `product_name`, `product_desc`, `product_main_images`, `size_chart_images`, and `product_attributes_text`.

If core PDP information is not localized into the target-country primary language, `page_quality <= 3`.

Target primary languages:

```text
UK: English
DE: German
FR: French
ES: Spanish
IT: Italian
```

Price semantics:

```text
UK: sales_price and shipping_fee are native GBP inputs with no conversion.
DE/FR/ES/IT: sales_price and shipping_fee are USD inputs converted to EUR.
list_price_usd: USD anchor only, not part of local landed cost.
```

`is_new_product_30d=true` with `cl_pay_sub_order_cnt < 10` reduces product-review-history weight and shifts quality reliability toward `shop_sales`, `shop_fans`, `shop_final_score`, page completeness, `product_attributes_text`, `product_main_images`, and `size_chart_images`.

New-product tolerance does not override safety, compliance, Stage 1 red flags, IPR or authorization risk, misleading or wrong-item evidence, visible product/spec conflict, or negative `review_contents`.

## Traffic Tiers

```text
1/2 = policy filtering tier
3 = deboost traffic-control tier
4/5 = no control tier
```

Score 3 is not a harmless neutral value. The evaluator needs clear evidence before lowering a product from 4/5 to 3.

## Safety Hard Cap

When PDP or review evidence shows clear bodily harm to the user from avoidable product failure, the final score must not exceed 3. Concentrated injury complaints can support score 2.

## RESULT Contract

The final machine-readable RESULT JSON may contain only:

```text
authenticity_delivery
safety
quality
value
compliance
page_quality
score
b_end_reasons
```
