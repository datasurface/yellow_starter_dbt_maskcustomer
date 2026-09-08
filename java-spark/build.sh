#!/usr/bin/env bash
set -euo pipefail
: "${DATASURFACE_SPARK_CLASSPATH:?Set to the DataSurface Spark runtime plus the provided Spark API jars}"
cd "$(dirname "$0")"
mkdir -p target/classes
javac --release 17 -cp "$DATASURFACE_SPARK_CLASSPATH" -d target/classes src/main/java/com/datasurface/examples/MaskCustomers.java
jar --create --file target/customer-mask-spark.jar -C target/classes .
