-- Masked Customers Model
-- INSERT into existing table (created by DataSurface with correct schema)
-- No materialization - we don't want dbt to DROP/CREATE the table

{% set target_table = var('output_customers') %}

{% call statement('insert_masked_data', fetch_result=False) %}
INSERT INTO {{ target_table }} (id, firstname, lastname, dob, email, phone, primaryaddressid, billingaddressid)
SELECT
    id,
    CONCAT(LEFT(firstname, 1), '***') AS firstname,
    CONCAT(LEFT(lastname, 1), '***') AS lastname,
    dob,
    CASE
        WHEN email IS NOT NULL AND CHARINDEX('@', email) > 0 THEN
            CONCAT(LEFT(email, 2), '***@', SUBSTRING(email, CHARINDEX('@', email) + 1, LEN(email)))
        ELSE email
    END AS email,
    CASE
        WHEN phone IS NOT NULL THEN
            CONCAT('***-***-', RIGHT(phone, 4))
        ELSE phone
    END AS phone,
    primaryaddressid,
    billingaddressid
FROM {{ source('workspace_inputs', 'Original_Store1_customers') }}
{% endcall %}

-- Ephemeral models need a SELECT statement
SELECT 1 as dummy
