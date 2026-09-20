# PDP Trust Score EU4+UK

This repository contains the isolated `pdp-trust-score_EU4-UK` Aicolate copybook for the merged UK+EU4 PDP Trust Score workflow.

GitHub repository:

```text
https://github.com/danielwanyan/pdp-trust-score_EU4-UK
```

The active workflow evaluates a single product per invocation and uses exactly one LLM node, `Trust_Evaluator`. The workflow has only one LLM because it is intended for repeated high-volume product scoring.

Supported target countries:

```text
UK, DE, FR, ES, IT
```

Key vNext behavior:

- `product_image_rpc` fetches `ProductMeta.images` and `Final_data_cleaning` preserves all returned URLs as `product_main_images`.
- `product_extra_attributes_rpc` fetches `product_extra_attributes.product_attributes` and `product_extra_attributes.size_chart`.
- `product_attributes_text` gives structured attributes to the model as text.
- `size_chart_images` are separate visual evidence and are included in localization checks.
- `visual_evidence_context` and `image_manifest` preserve source separation between `product_main_images`, `size_chart_images`, and combined `images`.
- Strict target-country language localization applies to title, `product_main_images`, `size_chart_images`, `product_desc`, and `product_attributes_text`.
- Large-scale non-localized core PDP information without target-language translation means `page_quality <= 3`.
- UK `sales_price` and `shipping_fee` are native GBP inputs with no conversion.
- DE, FR, ES, and IT `sales_price` and `shipping_fee` are USD inputs converted to EUR.
- `list_price_usd` is a USD anchor only and is not part of local landed cost.
- `is_new_product_30d` and `new_product_context` reduce product review-history weight for confirmed 30-day new products with fewer than 10 paid orders.
- New-product tolerance does not override safety, compliance, Stage 1 red flags, IPR or authorization risk, misleading or wrong-item evidence, visible product/spec conflict, or negative `review_contents`.
- For products with no historical sales or reviews and neutral evidence, `quality` can default to 4 rather than mechanically staying at 3.

Traffic tiers:

```text
1/2 = policy filtering tier
3 = deboost traffic-control tier
4/5 = no control tier
```

Score 3 is not a harmless neutral value. It has traffic-control impact, so the evaluator must explain the evidence before lowering from 4/5 to 3.

Safety hard cap:

When PDP or review evidence shows clear bodily harm to the user from avoidable product failure, the final score must not exceed 3. Concentrated injury complaints can support score 2.

Final RESULT JSON remains limited to:

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
