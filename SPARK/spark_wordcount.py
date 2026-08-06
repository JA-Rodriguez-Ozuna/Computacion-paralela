"""
spark_wordcount.py
Word Count con Apache Spark: RDD vs DataFrame
Mide tiempos y calcula speedup

Instalar PySpark:
    pip install pyspark

Ejecutar:
    python spark_wordcount.py
"""

import time
import re
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, split, lower, regexp_replace, col, desc

# ── Generar dataset de texto si no existe ────────────────────
def generar_dataset(nombre="dataset.txt", mb=10):
    """Genera un archivo de texto de aproximadamente mb MB."""
    if os.path.exists(nombre):
        print(f"[Dataset] '{nombre}' ya existe ({os.path.getsize(nombre)//1024} KB)")
        return

    frases = [
        "Apache Spark is a unified analytics engine for large scale data processing",
        "Spark provides high level APIs in Java Scala Python and R",
        "Resilient Distributed Datasets RDD are the fundamental data structure of Spark",
        "DataFrames provide a higher level abstraction over RDDs with schema information",
        "The Catalyst optimizer automatically optimizes DataFrame query plans",
        "MapReduce processes data sequentially while Spark processes data in memory",
        "Big Data frameworks allow distributed processing across clusters of machines",
        "Word count is the hello world of distributed computing frameworks",
        "PySpark allows Python developers to use Apache Spark capabilities",
        "Spark streaming enables real time data processing with micro batch architecture",
        "Machine learning pipelines can be built using MLlib in Apache Spark",
        "Graph processing is supported through GraphX in the Spark ecosystem",
        "HDFS Hadoop Distributed File System stores data across multiple nodes",
        "Fault tolerance in Spark is achieved through RDD lineage information",
        "Lazy evaluation in Spark means transformations are not executed immediately",
    ]

    target = mb * 1024 * 1024
    with open(nombre, "w", encoding="utf-8") as f:
        written = 0
        while written < target:
            for frase in frases:
                f.write(frase + "\n")
                written += len(frase) + 1
                if written >= target:
                    break

    size_mb = os.path.getsize(nombre) / (1024 * 1024)
    print(f"[Dataset] Generado '{nombre}' — {size_mb:.2f} MB")


# ════════════════════════════════════════════════════════════
# WORD COUNT CON RDD
# ════════════════════════════════════════════════════════════
def wordcount_rdd(sc, archivo):
    """
    Pipeline RDD:
    textFile -> flatMap (tokenizar) -> map (par clave-valor)
             -> reduceByKey (sumar) -> sortBy (ordenar desc)
    """
    rdd = (sc.textFile(archivo)
             .flatMap(lambda linea: re.findall(r'[a-zA-Z]+', linea.lower()))
             .map(lambda palabra: (palabra, 1))
             .reduceByKey(lambda a, b: a + b)
             .sortBy(lambda x: x[1], ascending=False))
    return rdd.collect()


# ════════════════════════════════════════════════════════════
# WORD COUNT CON DATAFRAME
# ════════════════════════════════════════════════════════════
def wordcount_dataframe(spark, archivo):
    """
    Pipeline DataFrame:
    read.text -> select (explode + split) -> groupBy -> count -> orderBy
    """
    df = (spark.read.text(archivo)
               .select(explode(
                   split(regexp_replace(lower(col("value")),
                                        r'[^a-zA-Z\s]', ''), ' ')
               ).alias("palabra"))
               .filter(col("palabra") != "")
               .groupBy("palabra")
               .count()
               .orderBy(desc("count")))
    return df.collect()


# ════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════
def main():
    ARCHIVO = "dataset.txt"
    DATASET_MB = 10   # tamano del dataset en MB

    # Generar dataset
    generar_dataset(ARCHIVO, DATASET_MB)

    # Crear SparkSession
    spark = (SparkSession.builder
             .appName("WordCount_RDD_vs_DataFrame")
             .master("local[*]")
             .config("spark.ui.showConsoleProgress", "false")
             .config("spark.driver.memory", "2g")
             .getOrCreate())

    spark.sparkContext.setLogLevel("ERROR")
    sc = spark.sparkContext

    print("\n" + "="*55)
    print(" SPARK WORD COUNT: RDD vs DataFrame")
    print(f" Dataset: {ARCHIVO} ({DATASET_MB} MB)")
    print(f" Nucleos: {sc.defaultParallelism}")
    print("="*55)

    # ── RDD ───────────────────────────────────────────────────
    print("\n[RDD] Iniciando Word Count con RDD...")
    t_rdd_ini = time.time()
    resultados_rdd = wordcount_rdd(sc, ARCHIVO)
    t_rdd_fin = time.time()
    t_rdd = t_rdd_fin - t_rdd_ini

    print(f"[RDD] Completado en {t_rdd:.4f} s")
    print(f"[RDD] Palabras unicas: {len(resultados_rdd)}")
    print(f"[RDD] Top 10 palabras:")
    for palabra, conteo in resultados_rdd[:10]:
        print(f"       {palabra:<25} {conteo}")

    # Guardar resultados RDD
    with open("output_rdd.txt", "w") as f:
        for palabra, conteo in resultados_rdd:
            f.write(f"{palabra}\t{conteo}\n")
    print(f"[RDD] Resultados guardados en 'output_rdd.txt'")

    # ── DataFrame ─────────────────────────────────────────────
    print("\n[DataFrame] Iniciando Word Count con DataFrame...")
    t_df_ini = time.time()
    resultados_df = wordcount_dataframe(spark, ARCHIVO)
    t_df_fin = time.time()
    t_df = t_df_fin - t_df_ini

    print(f"[DataFrame] Completado en {t_df:.4f} s")
    print(f"[DataFrame] Palabras unicas: {len(resultados_df)}")
    print(f"[DataFrame] Top 10 palabras:")
    for row in resultados_df[:10]:
        print(f"       {row['palabra']:<25} {row['count']}")

    # Guardar resultados DataFrame
    with open("output_dataframe.csv", "w") as f:
        f.write("palabra,conteo\n")
        for row in resultados_df:
            f.write(f"{row['palabra']},{row['count']}\n")
    print(f"[DataFrame] Resultados guardados en 'output_dataframe.csv'")

    # ── Comparacion ───────────────────────────────────────────
    speedup = t_rdd / t_df if t_df > 0 else 0

    print("\n" + "="*55)
    print(" COMPARACION DE RENDIMIENTO")
    print("="*55)
    print(f"  Tiempo RDD       : {t_rdd:.4f} s")
    print(f"  Tiempo DataFrame : {t_df:.4f} s")
    print(f"  Speedup (RDD/DF) : {speedup:.2f}x  "
          f"({'DataFrame mas rapido' if speedup > 1 else 'RDD mas rapido'})")
    print(f"  Palabras unicas  : {len(resultados_rdd)}")
    print("="*55)

    spark.stop()
    print("\n[Spark] Sesion finalizada.")


if __name__ == "__main__":
    main()