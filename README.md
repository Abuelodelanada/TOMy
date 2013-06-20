TOMy: Another MySQL and PostgreSQL console client
=================================================

[![Build Status](https://travis-ci.org/Abuelodelanada/TOMy.png?branch=master)](https://travis-ci.org/Abuelodelanada/TOMy)

My own MySQL (and now PostgreSQL too) client, which I hope to have more features than the original ;-)

Now, I have implemented the following features:

 - Save data connections to .connections file
 - Support multiple connections
 - Configurable color results in .config file
 - Configurable prompt in .config file
 - Autocomplete sentences with databases, tables and fields names.
 - Save (recover and remove) executed queries to saved_queries.txt file.


![TOMy running](https://raw.github.com/Abuelodelanada/tomy/master/img/example.png "TOMy running")

.connections files
------------------

This file should have the following format

::

    [mysql1]
    host: localhost
    user: root
    pass: xx
    database: gca_31
    port: 3306
    engine: mysql
    autocommit: ON

    [mysql2]
    host: localhost
    user: root
    database: gca_30
    port: 3306
    engine: mysql
    autocommit: OFF



Wishlist
--------

 - SQL syntax coloring.
 - Pretty print for multi-line querys.
