from flowetl.mixins.fixed_sql_mixin import fixed_sql_operator

UpdateETLTableOperator = fixed_sql_operator(
    class_name="UpdateETLTableOperator",
    sql="""
        INSERT INTO etl.etl_records (cdr_type, cdr_date, state, timestamp) VALUES ('{{ params.cdr_type }}', '{{ ds }}'::DATE, 'ingested', NOW());
        INSERT INTO available_tables (table_name, has_locations, has_subscribers) VALUES ('{{ params.cdr_type }}', true, true)
            ON conflict (table_name)
            DO UPDATE SET has_locations=EXCLUDED.has_locations, has_subscribers=EXCLUDED.has_subscribers;
        """,
)
