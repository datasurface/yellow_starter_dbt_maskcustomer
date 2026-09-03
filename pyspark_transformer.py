"""PySpark implementation of the masked-customer DataTransformer."""

from typing import Any


def maskCustomers(customers: Any) -> Any:
    """Return the customer rows with direct identifiers masked."""
    from pyspark.sql import functions as F

    email = F.col("email")
    phone = F.col("phone")
    return customers.select(
        F.col("id").alias("id"),
        F.concat(F.substring(F.col("firstName"), 1, 1), F.lit("***")).alias(
            "firstname"
        ),
        F.concat(F.substring(F.col("lastName"), 1, 1), F.lit("***")).alias(
            "lastname"
        ),
        F.col("dob").alias("dob"),
        F.when(
            email.isNotNull() & (F.instr(email, "@") > 0),
            F.concat(
                F.substring(email, 1, 2),
                F.lit("***@"),
                F.substring_index(email, "@", -1),
            ),
        ).otherwise(email).alias("email"),
        F.when(
            phone.isNotNull(),
            F.concat(F.lit("***-***-"), F.substring(phone, -4, 4)),
        ).otherwise(phone).alias("phone"),
        F.col("primaryAddressId").alias("primaryaddressid"),
        F.col("billingAddressId").alias("billingaddressid"),
        F.lit("U").alias("ds_surf_iud"),
    )


def executeTransformer(spark: Any, context: Any) -> None:
    """Run against the Spark cluster selected by the platform PSP."""
    del spark
    customers = context.getInputDataFrame("Original", "CustomerDB", "customers")
    context.writeOutput("customers", maskCustomers(customers))
