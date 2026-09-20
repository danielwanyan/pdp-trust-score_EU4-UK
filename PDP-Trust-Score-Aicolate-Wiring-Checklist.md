# PDP Trust Score EU4+UK Aicolate Wiring Checklist

This checklist is for the isolated `pdp-trust-score_EU4-UK` merged vNext workflow.

## Runtime Shape

The workflow is a single product per invocation and one product per workflow call. It has exactly one LLM node and only one LLM in the production path: `Trust_Evaluator`.

```text
Start / Excel row
  -> product_image_rpc
  -> product_extra_attributes_rpc
  -> Final_data_cleaning
  -> Rules_Brain
  -> Context_Builder
  -> Trust_Evaluator
  -> End
```

## Start Inputs

Use flat variable names:

```text
product_id: String
target_country: String
is_new_product_30d: String
product_name: String
brand_name: String
first_category_name: String
shop_name: String
product_desc: String
comment_summary_text: String
review_contents: String
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

`product_image_rpc` fetches:

```text
ProductMeta.images
```

Map:

```text
rpc_images = product_image_rpc.output
```

`product_extra_attributes_rpc` fetches:

```text
product_extra_attributes.product_attributes
product_extra_attributes.size_chart
```

Map:

```text
product_extra_attributes = product_extra_attributes_rpc.output
```

## Rule Fetch Nodes

Configure HTTP GET nodes after pushing this repository:

```text
rules_text_fetch:
https://raw.githubusercontent.com/danielwanyan/pdp-trust-score_EU4-UK/main/rules/pdp_trust_rules_compressed_v1.txt

rules_json_fetch:
https://raw.githubusercontent.com/danielwanyan/pdp-trust-score_EU4-UK/main/rules/pdp_trust_rules_structured_v1.json
```

Map the compressed rulebook exactly once:

```text
body = rules_text_fetch.body
```

Map the structured rules:

```text
rules_json = rules_json_fetch.body
```

## Final_data_cleaning Output Panel

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

```text
case_state: String
evidence_manifest: String
decision_checklist: String
context_builder_debug: String
```

## Trust_Evaluator Inputs

Use flat names only:

```text
body receives the compressed rulebook from rules_text_fetch
rules_context = Rules_Brain.rules_context
rules_review_context = Rules_Brain.review_context
price_context = Rules_Brain.price_context
locale_context = Rules_Brain.locale_context
visual_evidence_context = Rules_Brain.visual_evidence_context
new_product_context = Rules_Brain.new_product_context
risk_hints = Rules_Brain.risk_hints
evidence_gaps = Rules_Brain.evidence_gaps
case_state = Context_Builder.case_state
evidence_manifest = Context_Builder.evidence_manifest
decision_checklist = Context_Builder.decision_checklist
product_id = Final_data_cleaning.product_id
product_name = Final_data_cleaning.product_name
product_main_images = Final_data_cleaning.product_main_images
size_chart_images = Final_data_cleaning.size_chart_images
images = Final_data_cleaning.images
image_manifest = Final_data_cleaning.image_manifest
product_attributes_text = Final_data_cleaning.product_attributes_text
product_desc = Final_data_cleaning.product_desc
brand_name = Final_data_cleaning.brand_name
first_category_name = Final_data_cleaning.first_category_name
sku_cnt = Final_data_cleaning.sku_cnt
review_cnt_td = Final_data_cleaning.review_cnt_td
comment_cnt_td = Final_data_cleaning.comment_cnt_td
avg_review_star_td = Final_data_cleaning.avg_review_star_td
avg_star_rating = Final_data_cleaning.avg_star_rating
review_contents = Final_data_cleaning.review_contents
cl_pay_sub_order_cnt = Final_data_cleaning.cl_pay_sub_order_cnt
currency = Final_data_cleaning.currency
target_country = Final_data_cleaning.target_country
target_currency = Final_data_cleaning.target_currency
price_input_semantics = Final_data_cleaning.price_input_semantics
localized_price_context = Final_data_cleaning.localized_price_context
is_new_product_30d = Final_data_cleaning.is_new_product_30d
shop_name = Final_data_cleaning.shop_name
is_official_tag = Final_data_cleaning.is_official_tag
shop_final_score = Final_data_cleaning.shop_final_score
shop_sales = Final_data_cleaning.shop_sales
shop_fans = Final_data_cleaning.shop_fans
comment_summary_text = Final_data_cleaning.comment_summary_text
comment_30d_emotion = Final_data_cleaning.comment_30d_emotion
is_free_shipping_fee = Final_data_cleaning.is_free_shipping_fee
shipping_fee = Final_data_cleaning.shipping_fee
has_flash_sale = Final_data_cleaning.has_flash_sale
is_free_return = Final_data_cleaning.is_free_return
onnr15 = Final_data_cleaning.onnr15
onnr30 = Final_data_cleaning.onnr30
shop_info = Final_data_cleaning.shop_info
review_context = Final_data_cleaning.review_context
logistics_info = Final_data_cleaning.logistics_info
governance_metrics = Final_data_cleaning.governance_metrics
```

## Scoring Reminders

- Strict target-country language checks apply to title, `product_main_images`, `size_chart_images`, `product_desc`, and `product_attributes_text`.
- If core PDP information is not localized into the target-country primary language, `page_quality <= 3`.
- UK price fields are native GBP. DE, FR, ES, and IT price fields are USD and converted to EUR in `Final_data_cleaning`.
- `list_price_usd` is an anchor only.
- `is_new_product_30d=true` and fewer than 10 paid orders reduces product-review-history weight and increases reliance on `shop_sales`, `shop_fans`, `shop_final_score`, page completeness, attributes, and image evidence.
- New-product tolerance does not override safety, compliance, Stage 1 red flags, IPR or authorization risk, misleading or wrong-item evidence, visible product/spec conflict, or negative `review_contents`.
- When there is clear bodily harm to the user from avoidable product failure, final score must not exceed 3.
