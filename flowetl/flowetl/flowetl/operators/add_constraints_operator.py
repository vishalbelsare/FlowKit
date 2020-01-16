from flowetl.mixins.fixed_sql_mixin import fixed_sql_operator

AddConstraintsOperator = fixed_sql_operator(
    class_name="AddConstraintsOperator",
    sql="""
        ALTER TABLE {{ extract_table }}
        ALTER COLUMN msisdn SET NOT NULL,
        ALTER COLUMN datetime SET NOT NULL;
    
        ALTER TABLE {{ extract_table }} DROP CONSTRAINT IF EXISTS {{ table_name }}_date_constraint;
        ALTER TABLE {{ extract_table }} ADD CONSTRAINT {{ table_name }}_date_constraint CHECK (
                    datetime >= '{{ ds }}'::TIMESTAMPTZ AND
                    datetime < '{{ tomorrow_ds }}'::TIMESTAMPTZ
                  );
        """,
)
