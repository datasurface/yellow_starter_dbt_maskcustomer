-- Masked Customers Model
-- INSERT into existing table (created by DataSurface with correct schema)
-- Dialect-aware: works on both PostgreSQL and SQL Server

{{ config(materialized='view') }}

{% set target_table = var('output_customers') %}
{% set source_table = source('workspace_inputs', 'Original_Store1_customers') %}

{# Build dialect-aware SQL for email masking #}
{% if target.type == 'sqlserver' %}
    {# SQL Server syntax #}
    {% set email_mask = "CASE WHEN email IS NOT NULL AND CHARINDEX('@', email) > 0 THEN CONCAT(LEFT(email, 2), '***@', SUBSTRING(email, CHARINDEX('@', email) + 1, LEN(email))) ELSE email END" %}
{% else %}
    {# PostgreSQL syntax #}
    {% set email_mask = "CASE WHEN email IS NOT NULL AND POSITION('@' IN email) > 0 THEN CONCAT(LEFT(email, 2), '***@', SPLIT_PART(email, '@', 2)) ELSE email END" %}
{% endif %}

{# Execute the INSERT statement during model execution #}
{% set insert_sql %}
INSERT INTO {{ target_table }} (id, firstname, lastname, dob, email, phone, primaryaddressid, billingaddressid)
SELECT 
    id,
    CONCAT(LEFT(firstname, 1), '***') AS firstname,
    CONCAT(LEFT(lastname, 1), '***') AS lastname,
    dob,
    {{ email_mask }} AS email,
    CASE WHEN phone IS NOT NULL THEN CONCAT('***-***-', RIGHT(phone, 4)) ELSE phone END AS phone,
    primaryaddressid,
    billingaddressid
FROM {{ source_table }}
{% endset %}

{% do run_query(insert_sql) %}

{# Return dummy result - the view itself is not used, just triggers the INSERT #}
SELECT 1 as dummy
