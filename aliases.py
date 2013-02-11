#! /usr/bin/env python
# -*- coding: utf-8 -*-

postgresql_aliases = {'_li': ("List all databases",
                              """SELECT
                              d.datname as "Name",
                              pg_catalog.pg_get_userbyid(d.datdba) as "Owner",
                              pg_catalog.pg_encoding_to_char(d.encoding) as
                              "Encoding",
                              d.datcollate as "Collate",
                              d.datctype as "Ctype",
                              pg_catalog.array_to_string(d.datacl, E' | ') AS
                              "Access privileges"
                              FROM pg_catalog.pg_database d
                              ORDER BY 1"""),
                      '_d': ("List tables, views, and sequences",
                             """SELECT
                             n.nspname as "Schema",
                             c.relname as "Name",
                             CASE c.relkind WHEN 'r'
                             THEN 'table' WHEN 'v'
                             THEN 'view' WHEN 'i'
                             THEN 'index' WHEN 'S'
                             THEN 'sequence' WHEN 's'
                             THEN 'special' WHEN 'f'
                             THEN 'foreign table' END as "Type",
                             pg_catalog.pg_get_userbyid(c.relowner) as "Owner"
                             FROM pg_catalog.pg_class c
                             LEFT JOIN pg_catalog.pg_namespace n ON
                             n.oid = c.relnamespace
                             WHERE
                             c.relkind IN ('r','v','S','f','') AND
                             n.nspname <> 'pg_catalog' AND
                             n.nspname <> 'information_schema' AND
                             n.nspname !~ '^pg_toast' AND
                             pg_catalog.pg_table_is_visible(c.oid)
                             ORDER BY 1,2"""),
                      '_db': ("List tablespaces",
                              """SELECT
                              spcname AS "Name",
                              pg_catalog.pg_get_userbyid(spcowner) AS "Owner",
                              spclocation AS "Location"
                              FROM pg_catalog.pg_tablespace
                              ORDER BY 1"""),
}
mysql_aliases = {'_sd': ("Show Databases",
                         "SHOW DATABASES")}
