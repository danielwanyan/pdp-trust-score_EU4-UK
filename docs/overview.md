# PDP Trust Score EU4+UK Merged vNext

This repository contains the isolated Aicolate copybook for `pdp-trust-score_EU4-UK`:

```text
https://github.com/danielwanyan/pdp-trust-score_EU4-UK
```

The active workflow is the merged UK+EU4 vNext line for `UK`, `DE`, `FR`, `ES`, and `IT`. It evaluates a single product per invocation and one product per workflow call. The active workflow has exactly one LLM and only one LLM: `Trust_Evaluator`.

## Active Flow

```text
Start
  -> product_image_rpc
  -> product_extra_attributes_rpc
  -> rules_text_fetch
  -> rules_json_fetch
  -> Final_data_cleaning
  -> Rules_Brain
  -> Context_Builder
  -> Trust_Evaluator
  -> End
```

Rules are loaded from the new repo only:

```text
https://raw.githubusercontent.com/danielwanyan/pdp-trust-score_EU4-UK/main/rules/pdp_trust_rules_compressed_v1.txt
https://raw.githubusercontent.com/danielwanyan/pdp-trust-score_EU4-UK/main/rules/pdp_trust_rules_structured_v1.json
```

## vNext Contract

- `target_country` is required and must use strict target-country language expectations.
- `product_image_rpc` preserves `ProductMeta.images` as `product_main_images`.
- `product_extra_attributes_rpc` provides `product_extra_attributes.product_attributes` as `product_attributes_text` and `product_extra_attributes.size_chart` as `size_chart_images`.
- `product_main_images`, `size_chart_images`, `product_attributes_text`, and `visual_evidence_context` are all PDP evidence for locale, specs, safety, fit, and visible consistency checks.
- Missing or non-localized core purchase information in the target-country primary language can cap `page_quality <= 3`.
- `is_new_product_30d` drives `new_product_context`; confirmed 30-day-new products with sparse product history reduce product-review-history weight but do not override concrete negative evidence.
- `price_input_semantics` must be followed: UK uses native GBP inputs, while EU4 uses USD-to-EUR conversion.
- `list_price_usd` is a list-price anchor only and must not be added into local landed cost.
- Score 3 is the deboost tier, not a harmless neutral tier; moving a product from 4/5 to 3 needs concrete evidence.
- When there is clear bodily harm to the user, final score must not exceed 3.

## Price Semantics

UK native inputs:

```text
sales_price and shipping_fee are GBP.
target_currency = GBP
no conversion is applied
```

EU4 conversion:

```text
DE, FR, ES, IT sales_price and shipping_fee are USD inputs.
Convert USD to EUR with the configured workflow rate.
target_currency = EUR
list_price_usd remains a USD anchor only.
```

## Output Shape

The final model-facing context keeps the existing score fields and uses these vNext support fields:

```text
product_main_images
size_chart_images
product_attributes_text
image_manifest
case_state
evidence_manifest
decision_checklist
price_input_semantics
is_new_product_30d
new_product_context
visual_evidence_context
```
