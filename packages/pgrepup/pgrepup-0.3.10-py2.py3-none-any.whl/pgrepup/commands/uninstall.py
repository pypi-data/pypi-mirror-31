# Copyright (C) 2016-2018 Denis Gasparin <denis@gasparin.net>
#
# This file is part of Pgrepup.
#
# Pgrepup is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pgrepup is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pgrepup. If not, see <http://www.gnu.org/licenses/>.
from clint.textui import indent
from ..helpers.replication import *
from ..helpers.docopt_dispatch import dispatch
from ..helpers.ui import *
from .stop import stop


@dispatch.on('uninstall')
def uninstall():
    stop()

    output_cli_message("Uninstall operations", color='cyan')
    puts("")
    with indent(4, quote=' >'):
        output_cli_message("Remove nodes from Destination cluster")
        print
        with indent(4, quote=' '):
            for db in get_cluster_databases(connect('Destination')):
                output_cli_message(db)
                drop_node(db)
                print(output_cli_result(True, 4))
        output_cli_message("Drop pgl_ddl_deploy extension in all databases")
        print
        with indent(4, quote=' '):
            for t in ['Source', 'Destination']:
                output_cli_message(t)
                print
                with indent(4, quote=' '):
                    for db in get_cluster_databases(connect(t)):
                        output_cli_message(db)
                        if not clean_pgl_ddl_deploy(t, db):
                            print(output_cli_result(False, compensation=8))
                            continue
                        print(output_cli_result(True, compensation=8))

        output_cli_message("Drop pg_logical extension in all databases")
        print
        with indent(4, quote=' '):
            for t in ['Source', 'Destination']:
                output_cli_message(t)
                print
                with indent(4, quote=' '):
                    for db in get_cluster_databases(connect(t)):
                        output_cli_message(db)
                        if not clean_pglogical_setup(t, db):
                            print(output_cli_result(False, compensation=8))
                            continue
                        print(output_cli_result(True, compensation=8))

        output_cli_message("Drop user for replication")
        print(output_cli_result(drop_user(connect('Source'), get_pgrepup_replication_user())))

        output_cli_message("Drop unique fields added by fix command")
        print
        with indent(8, quote=' '):
            src_db_conn = connect('Source')
            for db in get_cluster_databases(src_db_conn):
                output_cli_message(db)
                print
                src_d_db_conn = connect('Source', db_name=db)
                dest_d_db_conn = connect('Destination', db_name=db)
                with indent(4, quote=' '):
                    for table in get_database_tables(src_d_db_conn):
                        output_cli_message("%s.%s" % (table['schema'], table['table']))
                        s = drop_table_field(
                            src_d_db_conn, table['schema'], table['table'], get_unique_field_name()
                        )
                        d = drop_table_field(
                            dest_d_db_conn, table['schema'], table['table'], get_unique_field_name()
                        )
                        print(output_cli_result(s and d, compensation=12))


