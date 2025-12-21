-- Masked Customers Model
-- INSERT into existing table (created by DataSurface with correct schema)

{{ config(materialized='ephemeral') }}

{% set target_table = var('output_customers') %}

{# Execute the INSERT statement #}
{% do run_query("INSERT INTO " ~ target_table ~ " (id, firstname, lastname, dob, email, phone, primaryaddressid, billingaddressid) SELECT id, CONCAT(LEFT(firstname, 1), '***'), CONCAT(LEFT(lastname, 1), '***'), dob, CASE WHEN email IS NOT NULL AND CHARINDEX('@', email) > 0 THEN CONCAT(LEFT(email, 2), '***@', SUBSTRING(email, CHARINDEX('@', email) + 1, LEN(email))) ELSE email END, CASE WHEN phone IS NOT NULL THEN CONCAT('***-***-', RIGHT(phone, 4)) ELSE phone END, primaryaddressid, billingaddressid FROM " ~ source('workspace_inputs', 'Original_Store1_customers')) %}

SELECT 1 as dummy
