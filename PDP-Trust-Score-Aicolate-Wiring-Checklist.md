# PDP Trust Score EU4+UK Aicolate Wiring Checklist

Repository:

```text
https://github.com/danielwanyan/pdp-trust-score_EU4-UK
```

This copybook is for the merged UK+EU4 vNext workflow. It evaluates a single product per invocation and one product per workflow call. The active workflow has exactly one LLM and only one LLM: `Trust_Evaluator`.

## Node Order

```text
Start
product_image_rpc
product_extra_attributes_rpc
rules_text_fetch
rules_json_fetch
Final_data_cleaning
Rules_Brain
Context_Builder
Trust_Evaluator
End
```

## RPC Nodes

`product_image_rpc` fetches:

```text
ProductMeta.images
```

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

## Rule Fetch Nodes

`rules_text_fetch`:

```text
https://raw.githubusercontent.com/danielwanyan/pdp-trust-score_EU4-UK/main/rules/pdp_trust_rules_compressed_v1.txt
```

`rules_json_fetch`:

```text
https://raw.githubusercontent.com/danielwanyan/pdp-trust-score_EU4-UK/main/rules/pdp_trust_rules_structured_v1.json
```

## Final_data_cleaning Input Variables

```text
product_id = Start.product_id
target_country = Start.target_country
is_new_product_30d = Start.is_new_product_30d
product_name = Start.product_name
brand_name = Start.brand_name
first_category_name = Start.first_category_name
shop_name = Start.shop_name
product_desc = Start.product_desc
review_contents = Start.review_contents
comment_summary_text = Start.comment_summary_text
comment_30d_emotion = Start.comment_30d_emotion
is_official_tag = Start.is_official_tag
is_free_shipping_fee = Start.is_free_shipping_fee
has_flash_sale = Start.has_flash_sale
is_free_return = Start.is_free_return
sku_cnt = Start.sku_cnt
shop_sales = Start.shop_sales
shop_fans = Start.shop_fans
comment_cnt_td = Start.comment_cnt_td
cl_pay_sub_order_cnt = Start.cl_pay_sub_order_cnt
review_cnt_td = Start.review_cnt_td
pv_rank = Start.pv_rank
video_product_show_cnt = Start.video_product_show_cnt
is_main_img_firstimg_quality = Start.is_main_img_firstimg_quality
prd_basic_info_score = Start.prd_basic_info_score
list_price_usd = Start.list_price_usd
sales_price = Start.sales_price
shop_final_score = Start.shop_final_score
avg_review_star_td = Start.avg_review_star_td
with_image_comment_ratio = Start.with_image_comment_ratio
avg_star_rating = Start.avg_star_rating
shipping_fee = Start.shipping_fee
onnr15 = Start.onnr15
onnr30 = Start.onnr30
rpc_images = product_image_rpc.output
product_extra_attributes = product_extra_attributes_rpc.output
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

## Rules_Brain Input Variables

```text
rules_json = rules_json_fetch.body
product_id = Final_data_cleaning.product_id
product_name = Final_data_cleaning.product_name
brand_name = Final_data_cleaning.brand_name
first_category_name = Final_data_cleaning.first_category_name
product_desc = Final_data_cleaning.product_desc
product_main_images = Final_data_cleaning.product_main_images
size_chart_images = Final_data_cleaning.size_chart_images
image_manifest = Final_data_cleaning.image_manifest
product_attributes_text = Final_data_cleaning.product_attributes_text
target_country = Final_data_cleaning.target_country
target_currency = Final_data_cleaning.target_currency
localized_price_context = Final_data_cleaning.localized_price_context
price_input_semantics = Final_data_cleaning.price_input_semantics
is_new_product_30d = Final_data_cleaning.is_new_product_30d
new_product_context = Final_data_cleaning.new_product_context
shop_name = Final_data_cleaning.shop_name
is_official_tag = Final_data_cleaning.is_official_tag
shop_final_score = Final_data_cleaning.shop_final_score
shop_sales = Final_data_cleaning.shop_sales
shop_fans = Final_data_cleaning.shop_fans
review_cnt_td = Final_data_cleaning.review_cnt_td
avg_review_star_td = Final_data_cleaning.avg_review_star_td
avg_star_rating = Final_data_cleaning.avg_star_rating
review_contents = Final_data_cleaning.review_contents
comment_summary_text = Final_data_cleaning.comment_summary_text
cl_pay_sub_order_cnt = Final_data_cleaning.cl_pay_sub_order_cnt
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
rules_review_context: String
rules_version: String
rules_source_warning: String
pdp_debug_summary: String
```

## Context_Builder Input Variables

```text
product_id = Final_data_cleaning.product_id
product_name = Final_data_cleaning.product_name
target_country = Final_data_cleaning.target_country
target_currency = Final_data_cleaning.target_currency
product_main_images = Final_data_cleaning.product_main_images
size_chart_images = Final_data_cleaning.size_chart_images
images = Final_data_cleaning.images
image_manifest = Final_data_cleaning.image_manifest
product_attributes_text = Final_data_cleaning.product_attributes_text
is_new_product_30d = Final_data_cleaning.is_new_product_30d
new_product_context = Rules_Brain.new_product_context
visual_evidence_context = Rules_Brain.visual_evidence_context
locale_context = Rules_Brain.locale_context
price_context = Rules_Brain.price_context
rules_context = Rules_Brain.rules_context
matched_rules = Rules_Brain.matched_rules
risk_hints = Rules_Brain.risk_hints
evidence_gaps = Rules_Brain.evidence_gaps
rules_review_context = Rules_Brain.rules_review_context
```

## Context_Builder Output Panel

Declare:

```text
case_state: String
evidence_manifest: String
decision_checklist: String
context_builder_debug: String
```

## Trust_Evaluator Input Variables

Use flat names only:

```text
body = rules_text_fetch.body
rules_context = Rules_Brain.rules_context
rules_review_context = Rules_Brain.rules_review_context
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
is_main_img_firstimg_quality = Final_data_cleaning.is_main_img_firstimg_quality
prd_basic_info_score = Final_data_cleaning.prd_basic_info_score
list_price_usd = Final_data_cleaning.list_price_usd
sales_price = Final_data_cleaning.sales_price
shipping_fee = Final_data_cleaning.shipping_fee
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
comment_cnt_td = Final_data_cleaning.comment_cnt_td
review_cnt_td = Final_data_cleaning.review_cnt_td
avg_review_star_td = Final_data_cleaning.avg_review_star_td
avg_star_rating = Final_data_cleaning.avg_star_rating
review_contents = Final_data_cleaning.review_contents
cl_pay_sub_order_cnt = Final_data_cleaning.cl_pay_sub_order_cnt
with_image_comment_ratio = Final_data_cleaning.with_image_comment_ratio
comment_summary_text = Final_data_cleaning.comment_summary_text
comment_30d_emotion = Final_data_cleaning.comment_30d_emotion
is_free_shipping_fee = Final_data_cleaning.is_free_shipping_fee
has_flash_sale = Final_data_cleaning.has_flash_sale
is_free_return = Final_data_cleaning.is_free_return
onnr15 = Final_data_cleaning.onnr15
onnr30 = Final_data_cleaning.onnr30
shop_info = Final_data_cleaning.shop_info
review_context = Final_data_cleaning.review_context
logistics_info = Final_data_cleaning.logistics_info
governance_metrics = Final_data_cleaning.governance_metrics
```

## Prompt Checks

- Use strict target-country language for locale-sensitive evidence. If core information is not understandable in the target-country primary language, `page_quality <= 3`.
- `product_main_images`, `size_chart_images`, and `product_attributes_text` must be visible in prompt context.
- `visual_evidence_context`, `case_state`, `evidence_manifest`, and `decision_checklist` must be mapped from the code nodes into `Trust_Evaluator`.
- Follow `price_input_semantics`: UK GBP native inputs, EU4 USD-to-EUR conversion, and `list_price_usd` anchor only.
- Use `is_new_product_30d` and `new_product_context` to prevent a mechanical score 3 deboost tier decision on sparse new products when concrete risk evidence is absent.
