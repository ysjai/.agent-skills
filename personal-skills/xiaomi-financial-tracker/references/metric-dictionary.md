# Metric Dictionary

`can_derive_quarter=yes` means the metric is a flow metric that can be derived with cumulative subtraction when periods, units, and segment match.

| segment | metric | canonical_unit | value_kind | can_derive_quarter | notes |
|---|---|---|---|---|---|
| Group | total_revenue | RMB bn | actual_flow | yes | Total group revenue |
| Group | gross_margin | % | actual_flow | no | Ratio, do not subtract |
| Group | net_profit | RMB bn | actual_flow | yes | Reported net profit |
| Group | adjusted_net_profit | RMB bn | actual_flow | yes | Non-IFRS adjusted net profit |
| Group | r_and_d_expenses | RMB bn | actual_flow | yes | R&D spending |
| Group | cash_reserve | RMB bn | actual_stock | no | Point-in-time cash resources |
| Group | operating_cash_flow | RMB bn | actual_flow | yes | Operating cash flow |
| Group | free_cash_flow | RMB bn | actual_flow | yes | Free cash flow if disclosed |
| Group | sales_and_marketing_expenses | RMB bn | actual_flow | yes | Sales and promotion expense |
| Group | employee_count | people | actual_stock | no | Point-in-time headcount |
| Group | r_and_d_employee_count | people | actual_stock | no | Point-in-time R&D headcount |
| Smartphone | smartphone_revenue | RMB bn | actual_flow | yes | Smartphone segment revenue |
| Smartphone | smartphone_gross_margin | % | actual_flow | no | Ratio, do not subtract |
| Smartphone | smartphone_shipments | million units | actual_flow | yes | Global smartphone shipments |
| Smartphone | smartphone_asp | RMB | actual_flow | no | Average selling price |
| Smartphone | global_market_share | % | actual_flow | no | Market share |
| Smartphone | china_market_share | % | actual_flow | no | Market share |
| Smartphone | global_rank | rank | actual_stock | no | Ranking |
| Smartphone | china_rank | rank | actual_stock | no | Ranking |
| Smartphone | premium_shipments_mix | % | actual_flow | no | High-end shipment mix |
| AIoT | aiot_revenue | RMB bn | actual_flow | yes | AIoT segment revenue |
| AIoT | aiot_gross_margin | % | actual_flow | no | Ratio, do not subtract |
| AIoT | connected_devices | million devices | actual_stock | no | Excluding phones, tablets, laptops when applicable |
| AIoT | five_plus_device_users | million users | actual_stock | no | Users with 5+ connected devices |
| AIoT | air_conditioner_shipments | million units | actual_flow | yes | Air conditioner shipments |
| AIoT | refrigerator_shipments | million units | actual_flow | yes | Refrigerator shipments |
| AIoT | washing_machine_shipments | million units | actual_flow | yes | Washing machine shipments |
| AIoT | tablet_rank | rank | actual_stock | no | Ranking |
| AIoT | wearable_rank | rank | actual_stock | no | Ranking |
| AIoT | tws_rank | rank | actual_stock | no | Ranking |
| AIoT | tv_rank | rank | actual_stock | no | Ranking |
| Internet Services | internet_services_revenue | RMB bn | actual_flow | yes | Internet services revenue |
| Internet Services | internet_services_gross_margin | % | actual_flow | no | Ratio, do not subtract |
| Internet Services | global_mau | million users | actual_stock | no | Monthly active users |
| Internet Services | china_mau | million users | actual_stock | no | China MAU |
| Internet Services | advertising_revenue | RMB bn | actual_flow | yes | If disclosed |
| Internet Services | gaming_revenue | RMB bn | actual_flow | yes | If disclosed |
| Internet Services | value_added_services_revenue | RMB bn | actual_flow | yes | If disclosed |
| Smart EV, AI and Other New Initiatives | smart_ev_revenue | RMB bn | actual_flow | yes | Smart EV and related revenue |
| Smart EV, AI and Other New Initiatives | smart_ev_gross_margin | % | actual_flow | no | Ratio, do not subtract |
| Smart EV, AI and Other New Initiatives | smart_ev_operating_profit | RMB bn | actual_flow | yes | Profit or loss from operations |
| Smart EV, AI and Other New Initiatives | smart_ev_adjusted_profit | RMB bn | actual_flow | yes | Adjusted profit or loss |
| Smart EV, AI and Other New Initiatives | smart_ev_deliveries | vehicles | actual_flow | yes | Vehicle deliveries |
| Smart EV, AI and Other New Initiatives | smart_ev_asp | RMB | actual_flow | no | Average selling price |
| Smart EV, AI and Other New Initiatives | stores | stores | actual_stock | no | Point-in-time store count |
| Smart EV, AI and Other New Initiatives | covered_cities | cities | actual_stock | no | Point-in-time city coverage |
| Smart EV, AI and Other New Initiatives | annual_delivery_target | vehicles | forecast | no | Official guidance or forecast, not fact |
| Smart EV, AI and Other New Initiatives | smart_ev_r_and_d_expenses | RMB bn | actual_flow | yes | EV R&D spending if disclosed |
| Valuation | ttm_pe | multiple | actual_stock | no | Historical valuation metric |
| Valuation | adjusted_ttm_pe | multiple | actual_stock | no | Historical adjusted PE |
| Valuation | forward_pe | multiple | forecast | no | Forecast metric, not used for historical percentile |
| Valuation | pb | multiple | actual_stock | no | Historical valuation metric |
