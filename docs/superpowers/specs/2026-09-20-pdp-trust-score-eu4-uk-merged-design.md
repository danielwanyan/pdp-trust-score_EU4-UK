# PDP Trust Score EU4+UK Merged vNext Design

## Status

Design approved by the user on 2026-09-20 for writing into the new isolated repository:

```text
https://github.com/danielwanyan/pdp-trust-score_EU4-UK
```

This design creates a new `UK+EU4` merged Aicolate workflow line. It must not change, push to, or reuse raw GitHub URLs from the previous `pdp-trust-score` repository.

## Goal

Build a new PDP trust scoring workflow that evaluates TikTok Shop products from the target country's local buyer perspective across:

```text
UK, DE, FR, ES, IT
```

Each country has its own locale profile. The scoring system must be fair and comprehensive from the user perspective, while preserving the existing downstream three-band control meaning:

```text
1/2 = policy filtering tier
3   = deboost traffic-control tier
4/5 = no control tier and traffic recipient tier
```

Because score 3 triggers deboost and 4/5 products receive more traffic when lower tiers are controlled, score 3 is not a harmless neutral value. The model must require clear evidence before moving a product from 4/5 to 3, and stronger evidence before moving it to 1/2.

## Non-Goals

- Do not modify the old `/Users/bytedance/pdp-trust-score` project or its GitHub raw URLs.
- Do not keep UK fixed-buyer and EU4 target-country as separate production lines for this vNext.
- Do not add extra machine-readable RESULT fields.
- Do not add a second LLM, juror, judge, result validator, or fallback LLM to the active high-volume workflow.
- Do not split visual evidence into a separate `detail_images` source. Detail long images can appear inside `product_main_images`.
- Do not let language localization rules change `quality`; they cap `page_quality`.

## Architecture

Use one new isolated repository and one merged Aicolate workflow:

```text
Start / Excel row
  ├─ RPC: product_image_rpc
  │    └─ fetch ProductMeta.images, preserving all returned product images
  ├─ RPC: product_extra_attributes_rpc
  │    └─ fetch product_attributes and size_chart
  ├─ HTTP Request: rules_text_fetch from the new repo
  └─ HTTP Request: rules_json_fetch from the new repo

Start + product_image_rpc + product_extra_attributes_rpc
  → Final_data_cleaning Code Node

Final_data_cleaning + rules_json_fetch
  → Rules_Brain Code Node

Final_data_cleaning + Rules_Brain
  → Context_Builder Code Node

Final_data_cleaning + Rules_Brain + Context_Builder + rules_text_fetch
  → Trust_Evaluator LLM Node

Trust_Evaluator
  → End / RESULT JSON
```

The active workflow stays single product per invocation and exactly one LLM node: `Trust_Evaluator`.

## Repository Layout

The new repository should contain the deployable copybook assets directly:

```text
rules/
  pdp_trust_rules_structured_v1.json
  pdp_trust_rules_compressed_v1.txt

code_nodes/
  final_data_cleaning_pdp_trust_v1.py
  rules_brain_pdp_trust_v1.py
  context_builder_pdp_trust_v1.py

prompts/
  trust_evaluator_system_prompt_v1.txt
  trust_evaluator_user_prompt_v1.txt

docs/
  superpowers/specs/2026-09-20-pdp-trust-score-eu4-uk-merged-design.md
  overview.md
  wiring-checklist.md

tests/
  validate_pdp_trust_assets.py
```

The old repo may be used as a source reference during implementation, but the implementation must create independent files in this new repo.

## Locale Profiles

Supported `target_country` values:

```text
UK -> British TikTok Shop shopper, primary language English, target currency GBP
DE -> German TikTok Shop shopper, primary language German, target currency EUR
FR -> French TikTok Shop shopper, primary language French, target currency EUR
ES -> Spanish TikTok Shop shopper, primary language Spanish, target currency EUR
IT -> Italian TikTok Shop shopper, primary language Italian, target currency EUR
```

`target_country` is required. Unsupported values must be surfaced as unsupported and must not silently fall back to UK.

## Start Inputs

Keep existing PDP Trust input fields and add:

```text
target_country: String
is_new_product_30d: String
```

`is_new_product_30d` must accept common marker values:

```text
true, false, 1, 0, yes, no, y, n
```

Empty or unrecognized values are treated as not a confirmed 30-day new product.

## RPC Inputs And Outputs

### product_image_rpc

Purpose: fetch all product images from `ProductMeta.images`, not only the first image.

Expected source shape:

```text
output.result.ProductMeta.images.feature_value
```

`feature_value` may be a JSON array string, array, nested RPC object, or wrapper object. The Code Node must robustly unwrap the RPC result and preserve all valid URLs in original order.

Output from `Final_data_cleaning`:

```text
product_main_images: Array<String>
```

`product_main_images` is the only product-image visual source. It may contain ordinary main images, detail long images, selling-point images, package/spec images, and other PDP images returned by `ProductMeta.images`.

### product_extra_attributes_rpc

Purpose: fetch size chart images and product attributes.

Observed source shape:

```json
{
  "output": {
    "BaseResp": {
      "StatusCode": 0,
      "StatusMessage": ""
    },
    "result": {
      "product_extra_attributes.product_attributes": {
        "feature_code": "product_attributes",
        "feature_type": "Array",
        "feature_value": "[{\"value\":\"Plain\",\"label\":\"Pattern\"}]"
      },
      "product_extra_attributes.size_chart": {
        "feature_code": "size_chart",
        "feature_type": "Array",
        "feature_value": "[\"https://...\"]"
      }
    }
  }
}
```

Output from `Final_data_cleaning`:

```text
product_attributes_text: String
product_attributes_json: String
size_chart_images: Array<String>
extra_attributes_source: String
```

`product_attributes_text` should be a stable, readable text format such as:

```text
Pattern=Plain; Season=Summer; Material=Strong polyester single jersey; Composition=Polyester 95% Elastane 5%
```

`product_attributes_json` is for debugging and traceability only. It must not be added to the final RESULT JSON.

`size_chart_images` is the second and only other visual source. It is separate from `product_main_images` because a size chart is product-fit evidence, not general PDP imagery.

If Aicolate can bind two image arrays to the LLM, pass both arrays separately:

```text
product_main_images = Final_data_cleaning.product_main_images
size_chart_images = Final_data_cleaning.size_chart_images
```

If Aicolate requires one image array, `Final_data_cleaning` should additionally expose:

```text
images = product_main_images + size_chart_images
image_manifest = product_main_images_count, size_chart_images_count, and source order notes
```

The prompt must still describe the two evidence types clearly.

## Price Semantics

The merged workflow uses mixed input currency semantics:

```text
UK:
  sales_price and shipping_fee are already GBP.
  Do not convert them.
  landed_cost_local = sales_price + shipping_fee.
  target_currency = GBP.

DE, FR, ES, IT:
  sales_price and shipping_fee are USD.
  Convert them to EUR before value reasoning.
  landed_cost_local = (sales_price + shipping_fee) * USD_TO_EUR.
  target_currency = EUR.
```

Use a fixed conversion baseline for EU4:

```text
EXCHANGE_RATE_SOURCE = Frankfurter API
EXCHANGE_RATE_DATE = 2026-08-14
USD_TO_EUR = 0.86453
```

`list_price_usd` remains a USD list/original price anchor for rough discount interpretation. It must not be added into local landed cost.

Derived prompt/context fields:

```text
currency
target_currency
sales_price_local
shipping_fee_local
landed_cost_local
localized_price_context
price_input_semantics
```

`currency` should reflect the input currency of `sales_price` and `shipping_fee`:

```text
UK -> GBP
DE/FR/ES/IT -> USD
```

`localized_price_context` must explicitly state whether a conversion was or was not applied.

## Strict Localization Language Rule

The new workflow uses strict target-country language expectations:

```text
UK -> English
DE -> German
FR -> French
ES -> Spanish
IT -> Italian
```

This is a change from the older broad EU multilingual tolerance rule.

The language-localization check applies to:

```text
product_name / title
product_desc text when present
product_main_images readable text
size_chart_images readable text
product_attributes_text labels and values when they carry core information
```

If core PDP information is mostly or materially in a non-target primary language and lacks equivalent target-language translation:

```text
page_quality <= 3
```

Core PDP information includes:

```text
product identity
material or composition
size or fit
quantity or count
compatibility
usage instructions
safety warnings
warranty or return terms
delivery restrictions
region restrictions
expiry
digital redemption steps and restrictions
```

Non-core language should not trigger the cap by itself. Examples that should not trigger the cap alone:

```text
brand names
model names
international units
small decorative words
short universal words
single SKU labels
isolated non-critical packaging text
```

## Long-Image Description Rule

`product_main_images` may include long detail images with complete product descriptions.

If `product_desc` text is empty but `product_main_images` contain readable and complete product information:

```text
Do not treat the PDP as having no description evidence.
Use the long images as PDP presentation evidence.
```

However, if those long images carry core product descriptions but are not localized into the target country's primary language:

```text
page_quality <= 3
```

If the product depends heavily on the long-image information for size, safety, ingredients, material, compatibility, or usage, and that information is not locally understandable:

```text
page_quality should usually be 2 or 3 depending severity.
```

The model should explain in Chinese reasoning whether it used long-image text as description evidence and whether that evidence was localized.

## Size Chart Localization Rule

`size_chart_images` are both fit evidence and language-localization evidence.

If size or fit matters for the category and the size chart is not in the target country's primary language or lacks an equivalent target-language translation:

```text
page_quality <= 3
```

For clothing, shoes, accessories with fit constraints, child goods, pet goods, furniture, protective equipment, and other size-sensitive goods, an unreadable or non-localized size chart can lower `page_quality` further within the 2-3 range.

## Product Attributes Rule

`product_attributes_text` should strengthen PDP clarity when it supplies structured material, composition, size, season, pattern, style, compatibility, or sensitive-goods data.

The attributes should not be treated as stronger than PDP-visible evidence. If `product_attributes_text` conflicts with title, images, size chart, or product description:

```text
lower page_quality first
lower authenticity_delivery if the conflict affects what the buyer receives
```

If attributes are missing due to RPC failure or empty feature values, do not penalize the product by default. Penalize only when the product category needs the missing attribute to make a sensible local purchase decision.

## New-Product Quality Reliability Rule

The new workflow adds tolerance for confirmed 30-day new products:

```text
is_new_product_30d=true
and cl_pay_sub_order_cnt < 10
```

When both conditions hold:

```text
Do not mechanically lower quality because product-level sales or reviews are sparse.
Reduce the weight of product review history.
Use shop_sales, shop_fans, shop_final_score, official or channel evidence, page completeness, product attributes, product images, and size-chart evidence more heavily.
```

This rule affects `quality` reliability. It does not override:

```text
safety evidence
compliance evidence
Stage 1 red flags
clear misleading or wrong-item evidence
IPR or authorization risk
visible product/spec conflicts
negative review_contents when present
```

For old products or unknown newness:

```text
Use the existing review_cnt_td, comment_cnt_td, avg_review_star_td, avg_star_rating, and review_contents rules normally.
```

For products with no historical sales or review evidence:

```text
quality should rely more on shop_final_score, shop_sales, shop_fans, official/channel evidence, page completeness, and product attributes.
If the evidence is neutral and no clear risk appears, quality should default to 4 rather than being mechanically held at 3.
```

High-sensitivity categories, weak shops, incomplete pages, safety concerns, compliance concerns, IPR risk, and strong PDP inconsistency may still justify lower `quality` and lower final score.

## Trust_Evaluator Prompt Requirements

The `Trust_Evaluator` remains the only LLM node.

The human-readable analysis should be in Chinese. The machine-readable JSON field names remain English.

The prompt must explicitly include:

```text
target_country
target_currency
price_input_semantics
localized_price_context
product_main_images
size_chart_images
product_attributes_text
is_new_product_30d
shop_sales
shop_fans
shop_final_score
cl_pay_sub_order_cnt
review_cnt_td / comment_cnt_td
avg_review_star_td
avg_star_rating
review_contents
rules_context
locale_context
case_state
evidence_manifest
decision_checklist
```

The reasoning format must force these checks:

```text
1. Category sensitivity and special overlays.
2. Product identity, brand, channel, IPR, delivery, and PDP honesty.
3. Product review quality evidence, including new-product tolerance when applicable.
4. Shop-level support evidence when product-level history is sparse.
5. Main-image and size-chart visual evidence.
6. Strict target-country language localization across title, main images, long images, size chart, and attributes.
7. Long-image description handling when text description is empty.
8. Value reasoning with UK GBP native inputs and EU4 USD-to-EUR conversion.
9. Stage 1 red flags.
10. 1/2 vs 3 vs 4/5 tier boundary.
```

## RESULT JSON Contract

The final machine-readable output stays unchanged:

```json
{
  "authenticity_delivery": 4,
  "safety": 5,
  "quality": 4,
  "value": 4,
  "compliance": 5,
  "page_quality": 3,
  "score": 4,
  "b_end_reasons": ["页面关键信息或实物展示不足"]
}
```

Allowed fields only:

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

`b_end_reasons` is optional, max 3 items, and only for score below 4 when clear actionable reasons exist. Do not emit `target_country`, image arrays, price fields, `locale_context`, new-product flags, evidence text, confidence, category, internal panel, or explanations in the RESULT JSON.

## Error Handling

`product_image_rpc` failure:

```text
product_main_images = []
image_source = missing_product_main_images
The model must not pretend visual PDP evidence exists.
```

`product_extra_attributes_rpc` failure:

```text
product_attributes_text = ""
product_attributes_json = ""
size_chart_images = []
extra_attributes_source = missing_product_extra_attributes
```

Do not lower score only because this RPC failed. Lower `page_quality` only when the category needs the missing size or attribute evidence for a sensible purchase decision.

`size_chart` empty:

```text
size_chart_images = []
```

For size-sensitive categories, missing size-chart evidence can lower `page_quality`.

`product_attributes` empty:

```text
product_attributes_text = ""
product_attributes_json = ""
```

Use other PDP evidence. Do not invent attributes.

Unsupported `target_country`:

```text
target_country = original normalized value
target_currency = UNSUPPORTED
localized_price_context explains unsupported country
No fallback to UK
```

Empty `is_new_product_30d`:

```text
Do not enable the new-product tolerance rule.
```

## Validation Requirements

Local tests should prove:

```text
1. The rulebook supports exactly UK, DE, FR, ES, IT locale profiles.
2. `product_image_rpc` parsing preserves all ProductMeta.images URLs in order.
3. `product_extra_attributes.product_attributes.feature_value` becomes readable `product_attributes_text`.
4. `product_extra_attributes.size_chart.feature_value` becomes `size_chart_images`.
5. UK price inputs are treated as native GBP and not converted.
6. DE/FR/ES/IT price inputs are converted from USD to EUR.
7. `list_price_usd` is not included in local landed cost.
8. Strict localization language rules mention `page_quality <= 3`.
9. Long-image description rules mention non-localized long-image descriptions cap `page_quality`.
10. `size_chart_images` are included in localization language checks.
11. `is_new_product_30d` plus `cl_pay_sub_order_cnt < 10` changes `quality` evidence weighting toward shop metrics.
12. Prompt and rulebook say score 3 is a deboost tier, not a harmless neutral score.
13. RESULT JSON schema remains whitelisted to the existing fields.
14. Aicolate variable names are flat and use `{{variable_name}}`.
```

Smoke cases should cover:

```text
1. UK product with GBP price, English title/images/size chart, no conversion.
2. DE product with USD price converted to EUR and German-localized PDP.
3. FR/ES/IT product with English-only large main-image text and no local translation, causing page_quality <= 3.
4. Clothing product with a non-localized size chart, causing page_quality <= 3.
5. Empty product_desc but complete localized long-image description, accepted as description evidence.
6. Empty product_desc with complete non-localized long-image description, page_quality capped <= 3.
7. 30-day new product with cl_pay_sub_order_cnt < 10, no reviews, strong shop metrics, quality can default to 4 when no risk appears.
8. Old product with no reviews, weak shop metrics, and incomplete page, normal caution applies.
9. Product with no history but clear review_contents safety or quality problem, new-product tolerance does not override the issue.
10. Strong IPR, safety, scam, or wrong-item red flag still lands in 1/2 regardless of localization or new-product tolerance.
```

## Deployment Plan

Implementation should proceed after this spec is reviewed:

```text
1. Create the new repo asset structure locally.
2. Copy the useful baseline from the old PDP Trust copybook.
3. Update rule JSON and compressed rulebook for merged UK+EU4 scope.
4. Update Final_data_cleaning to parse two RPC outputs, all product main images, size-chart images, attributes, mixed currency semantics, and new-product flags.
5. Update Rules_Brain to emit locale, price, visual-evidence, attribute, strict-language, and new-product context.
6. Update Context_Builder to expose main image count, size chart count, attribute presence, localization checks, and new-product status.
7. Update Trust_Evaluator prompts while preserving Chinese human-readable output and the RESULT schema.
8. Add local validation tests.
9. Run validation.
10. Commit implementation.
11. Push to the new GitHub repo.
12. Verify raw GitHub URLs.
13. Give one-node-at-a-time Aicolate paste instructions with exact Output panel changes.
```

