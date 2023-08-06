#!/bin/bash
# vim:ts=4
#
# Handle static data required by Bootini Star, namely EVE Online
# item groups and item types.

dbname="$1"
action="$2"
dialect="${3:-postgresql}"

TABLES='groups types'
case "$action" in
	dump)
		opt='--clean --column-inserts'
		for table in $TABLES; do
			pg_dump $opt --table=$table $dbname | bzip2 >$t.sql.bz2
		done
		;;
	load)
		for table in $TABLES; do
			case "$dialect" in
				mysql)
					echo "bzcat $table.sql.bz2 | mysql -u bs -psecret -h xenon $dbname"
					;;
				postgresql)
					echo "bzcat $table.sql.bz2 | psql -U postgres -q $dbname"
					;;
				*)
					echo "Unknow dialect '$dialect'" >&2
					exit 1
			esac
		done
		;;
	*)
		echo "Usage   : $(basename $0) {dbname} {dump | load} [mysql | postgresql]" >&2
		echo "Example : $(basename $0) bs load mysql" >&2
		exit 1
esac
