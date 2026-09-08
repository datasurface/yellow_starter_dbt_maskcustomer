# Java Spark customer masking

`com.datasurface.examples.MaskCustomers` implements the same masking rules as
`pyspark_transformer.py`, using the DataSurface Java Spark DT context. It supports
full-history reseed and records successful invocation count, batch, and row count
through the standard DT state handoff. It neither connects to a database directly
nor owns credentials; the platform supplies its governed input and output maps.

Build with Java 17 and `DATASURFACE_SPARK_CLASSPATH` containing the approved
DataSurface Spark runtime and Spark 4.0.4 provided API dependencies. Run `build.sh`,
then package `target/customer-mask-spark.jar` under `/app/java/lib` in a PSP-approved
image. Spark and DataSurface dependencies must not be bundled in this thin JAR.

Model with `JavaSparkCodeArtifact("customer-mask-spark.jar",
"com.datasurface.examples.MaskCustomers")`. The input is
`Original / CustomerDB / customers`; output is the IUD dataset `customers`.
