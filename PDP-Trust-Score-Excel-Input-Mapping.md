# PDP Trust Score EU4+UK Excel Input Mapping

Repository:

```text
https://github.com/danielwanyan/pdp-trust-score_EU4-UK
```

This mapping is for the merged UK+EU4 vNext workflow. Each Excel row represents one product. The active workflow evaluates a single product per invocation and one product per workflow call with exactly one LLM and only one LLM: `Trust_Evaluator`.

Rule assets:

```text
https://raw.githubusercontent.com/danielwanyan/pdp-trust-score_EU4-UK/main/rules/pdp_trust_rules_compressed_v1.txt
https://raw.githubusercontent.com/danielwanyan/pdp-trust-score_EU4-UK/main/rules/pdp_trust_rules_structured_v1.json
```

## Allowed Start Fields

Only use these Start fields for the copybook input mapping:

```text
product_id
target_country
is_new_product_30d
product_name
brand_name
first_category_name
shop_name
product_desc
review_contents
comment_summary_text
comment_30d_emotion
is_official_tag
is_free_shipping_fee
has_flash_sale
is_free_return
sku_cnt
shop_sales
shop_fans
comment_cnt_td
cl_pay_sub_order_cnt
review_cnt_td
pv_rank
video_product_show_cnt
is_main_img_firstimg_quality
prd_basic_info_score
list_price_usd
sales_price
shop_final_score
avg_review_star_td
with_image_comment_ratio
avg_star_rating
shipping_fee
onnr15
onnr30
```

## Required Fields

```text
product_id: source product identifier, preserve as string
target_country: UK, DE, FR, ES, or IT
is_new_product_30d: true/false style marker for 30-day-new product handling
product_name: title used for product identity and locale checks
sales_price: UK GBP native input or EU4 USD input based on target_country
shipping_fee: UK GBP native input or EU4 USD input based on target_country
list_price_usd: USD list-price anchor only
```

## Locale And Price Handling

- Strict target-country language applies to buyer-facing core information.
- Missing target-country primary language for core purchase facts can cap `page_quality <= 3`.
- UK GBP native inputs: `sales_price` and `shipping_fee` are already GBP.
- EU4 USD-to-EUR conversion: `sales_price` and `shipping_fee` are USD inputs converted to EUR by `Final_data_cleaning`.
- `list_price_usd` is an anchor only and is not part of local landed cost.
- `price_input_semantics` must be carried forward to `Trust_Evaluator`.
- Score 3 is the deboost tier; do not use sparse new-product history alone as a score 3 reason.

## Derived Fields

The workflow derives these fields after Start:

```text
product_main_images
size_chart_images
product_attributes_text
image_manifest
visual_evidence_context
case_state
evidence_manifest
decision_checklist
new_product_context
```

`product_main_images` comes from `ProductMeta.images`. `size_chart_images` and `product_attributes_text` come from `product_extra_attributes`. `new_product_context` comes from `is_new_product_30d` plus product and shop evidence.
