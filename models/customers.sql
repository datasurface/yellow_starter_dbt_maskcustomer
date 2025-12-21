-- Masked Customers Model
-- This dbt model reads from the customers source and masks PII fields
-- Output is written to the DataTransformer output table

{{ config(
    materialized='table',
    alias=var('output_customers', 'customers')
) }}

SELECT
    id,
    -- Mask firstname: keep first letter, replace rest with ***
    CONCAT(LEFT(firstname, 1), '***') AS firstname,
    -- Mask lastname: keep first letter, replace rest with ***
    CONCAT(LEFT(lastname, 1), '***') AS lastname,
    -- Keep dob as-is (or could mask year)
    dob,
    -- Mask email: show first 2 chars and domain (SQL Server compatible)
    CASE
        WHEN email IS NOT NULL AND CHARINDEX('@', email) > 0 THEN
            CONCAT(LEFT(email, 2), '***@', SUBSTRING(email, CHARINDEX('@', email) + 1, LEN(email)))
        ELSE email
    END AS email,
    -- Mask phone: show last 4 digits
    CASE
        WHEN phone IS NOT NULL THEN
            CONCAT('***-***-', RIGHT(phone, 4))
        ELSE phone
    END AS phone,
    primaryaddressid,
    billingaddressid
FROM {{ source('workspace_inputs', 'Original_Store1_customers') }}
