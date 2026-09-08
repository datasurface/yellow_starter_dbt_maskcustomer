package com.datasurface.examples;

import com.datasurface.spark.SparkDataTransformer;
import com.datasurface.spark.SparkDataTransformerContext;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import static org.apache.spark.sql.functions.*;

/** The same masking rules as pyspark_transformer.py, with state for retry qualification. */
public final class MaskCustomers implements SparkDataTransformer {
    public static Dataset<Row> maskCustomers(Dataset<Row> input) {
        return input.select(
            col("id"),
            concat(substring(col("firstName"), 1, 1), lit("***")).alias("firstname"),
            concat(substring(col("lastName"), 1, 1), lit("***")).alias("lastname"),
            col("dob"),
            when(col("email").isNotNull().and(instr(col("email"), "@").gt(0)),
                 concat(substring(col("email"), 1, 2), lit("***@"), substring_index(col("email"), "@", -1)))
                 .otherwise(col("email")).alias("email"),
            when(col("phone").isNotNull(), concat(lit("***-***-"), substring(col("phone"), -4, 4)))
                 .otherwise(col("phone")).alias("phone"),
            col("primaryAddressId").alias("primaryaddressid"),
            col("billingAddressId").alias("billingaddressid"),
            lit("U").alias("ds_surf_iud"));
    }

    @Override public void transform(SparkDataTransformerContext context) throws Exception {
        boolean reseed = context.isReseedRequested();
        Dataset<Row> input = reseed
            ? context.getInputFullDataFrame("Original", "CustomerDB", "customers")
            : context.getInputDataFrame("Original", "CustomerDB", "customers");
        Dataset<Row> output = maskCustomers(input);
        context.writeOutput("customers", output);
        if (reseed) context.declareReseed();
        long completed = ((Number) context.getPreviousState().getOrDefault("completed_runs", 0)).longValue();
        context.setNextStateValue("completed_runs", completed + 1);
        context.setNextStateValue("last_batch", context.getBatchId());
        context.setNextStateValue("last_row_count", output.count());
        System.out.println("DATASURFACE_KERBEROS_MASK_COMPLETED batch=" + context.getBatchId());
    }
}
