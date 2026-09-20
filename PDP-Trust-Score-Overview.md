# PDP Trust Score EU4+UK Merged vNext

This copybook belongs to the new repository and project `pdp-trust-score_EU4-UK`:

```text
https://github.com/danielwanyan/pdp-trust-score_EU4-UK
```

It documents the merged UK+EU4 vNext Aicolate workflow for `UK`, `DE`, `FR`, `ES`, and `IT`. The active workflow evaluates a single product per invocation and one product per workflow call. It has exactly one LLM and only one LLM: `Trust_Evaluator`.

## Active Workflow

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

Use only these raw rule URLs for this repo:

```text
https://raw.githubusercontent.com/danielwanyan/pdp-trust-score_EU4-UK/main/rules/pdp_trust_rules_compressed_v1.txt
https://raw.githubusercontent.com/danielwanyan/pdp-trust-score_EU4-UK/main/rules/pdp_trust_rules_structured_v1.json
```

## vNext Behavior

- Strict target-country language is required for core buyer-facing information.
- Core purchase facts missing the target-country primary language can cap `page_quality <= 3`.
- `product_image_rpc` reads `ProductMeta.images` and preserves them as `product_main_images`.
- `product_extra_attributes_rpc` reads `product_extra_attributes.product_attributes` into `product_attributes_text`.
- `product_extra_attributes_rpc` reads `product_extra_attributes.size_chart` into `size_chart_images`.
- `visual_evidence_context` keeps visible image evidence explicit for localization, fit, specs, package claims, warnings, and image/text consistency.
- `is_new_product_30d` and `new_product_context` reduce product-review-history weight for confirmed new products without overriding real negative evidence.
- `price_input_semantics` controls currency handling: UK GBP native inputs, EU4 USD-to-EUR conversion.
- `list_price_usd` is a list-price anchor only.
- Score 3 is the deboost tier and needs concrete evidence, especially when moving down from 4/5.
- When there is clear bodily harm to the user, final score must not exceed 3.

## Core Model Inputs

```text
product_main_images
size_chart_images
product_attributes_text
image_manifest
case_state
evidence_manifest
decision_checklist
target_country
price_input_semantics
is_new_product_30d
new_product_context
visual_evidence_context
```
