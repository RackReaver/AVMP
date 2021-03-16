"""Class functions for managing a sqlite database for Tenable vulnerabilities.
"""
__copyright__ = "Copyright (C) 2020-2021  Matt Ferreira"
__license__ = "Apache License"

import os
import sqlite3
import datetime
import logging


class TenableSqliteVulnDB:
    def __init__(self, filepath, ignore_statuses=['Done', 'Closed', 'Platform Complete']):
        isinstance(filepath, str)
        isinstance(ignore_statuses, list)

        self.filepath = filepath
        self.db_name = os.path.basename(filepath)

        if not os.path.exists(filepath):
            logging.info('DB Not Found...')
            self._build_db()

        self.con = sqlite3.connect(filepath)
        self.ignore_statuses = ignore_statuses

    def _build_db(self):
        logging.info('Building DB now...')

        con = sqlite3.connect(self.db_name)

        con.execute("""
                CREATE TABLE "tickets" (
                "ticket_id"	TEXT NOT NULL,
                "plugin_id"	TEXT NOT NULL,
                "status"	INTEGER,
                "created_date"	TEXT NOT NULL,
                "modified_date"	TEXT NOT NULL,
                PRIMARY KEY("ticket_id"))
                """)
        con.execute("""
                CREATE TABLE "hosts" (
	            "id"	INTEGER NOT NULL UNIQUE,
	            "host"	TEXT NOT NULL,
                PRIMARY KEY("id" AUTOINCREMENT))
                """)
        con.execute("""
                CREATE TABLE "hosts_tickets" (
	            "id"	INTEGER NOT NULL UNIQUE,
	            "host_id"	INTEGER NOT NULL,
                "ticket_id"	INTEGER NOT NULL,
                FOREIGN KEY("host_id") REFERENCES "hosts"("id"),
                FOREIGN KEY("ticket_id") REFERENCES "hosts"("ticket_id"),
                PRIMARY KEY("id" AUTOINCREMENT))
                """)
        con.close()

    def add_ticket(self, ticket_number, plugin_id, status, hosts, date=datetime.datetime.now().strftime('%Y-%m-%d')):
        """Add a created ticket to database.

        args:
            ticket_number (str): Identification value for ticketing system.
            plugin_id (str): Plugin ID provided by Tenable.
            status (str): Status of new ticket in ticketing system.
            hosts (list): List of ip's associated with ticket.
        kwargs:
            date (str): [default: current date YYYY-MM-DD] Date ticket was created.

        Return (bool): Confirmation of completion.
        """
        isinstance(ticket_number, str)
        isinstance(plugin_id, str)
        isinstance(status, str)
        isinstance(hosts, list)
        isinstance(date, str)

        try:
            assert self.check_by_ticket_number(
                ticket_number) == False, 'Ticket already exists in DB'
        except AssertionError:
            logging.exception('"{}" is already in {}'.format(
                ticket_number, self.db_name))
            return False

        sql = 'INSERT INTO tickets (ticket_id, plugin_id, status, created_date, modified_date) '
        sql += 'values ("{}","{}","{}","{}","{}")'.format(ticket_number,
                                                          plugin_id,
                                                          status,
                                                          date,
                                                          date
                                                          )
        with self.con:
            self.con.execute(sql)

        for ip in hosts:
            if not self.check_by_host(ip):
                sql = 'INSERT INTO hosts (host)'
                sql += 'values ("{}")'.format(ip)

                with self.con:
                    self.con.execute(sql)

            host_id = self.get_host_id(ip)

            sql = 'INSERT INTO hosts_tickets (host_id, ticket_id)'
            sql += 'values ("{}","{}")'.format(host_id, ticket_number)

            with self.con:
                self.con.execute(sql)

        return True

    def check_by_host(self, host):
        """Given a host check if it exists in the database.

        args:
            host (str): IP/Hostname to check database for

        return (bool): Confirmation of existance.
        """
        assert isinstance(host, str)
        sql = f'SELECT * FROM hosts WHERE host="{host}"'
        with self.con:
            data = self.con.execute(sql).fetchone()
        if data == None:
            logging.info(f'"{host}" does not exist.')
            return False
        else:
            logging.info(f'"{host}" exists.')
            return True

    def get_host_id(self, host):
        """Given a host get it's id in the database.

        args:
            host (str): IP/Hostname to check database for

        return (int): Database id for given host.
        """
        assert isinstance(host, str)
        sql = f'SELECT * FROM hosts WHERE host="{host}"'
        with self.con:
            data = self.con.execute(sql).fetchone()

        return data[0]

    def check_by_ticket_number(self, ticket_number):
        """Given a ticket number check if it exists in the database.

        args:
            ticket_number (str): Identification value for ticketing system to check.

        return (bool): Confirmation of existance.
        """
        assert isinstance(ticket_number, str)
        sql = f'SELECT * FROM tickets WHERE ticket_id="{ticket_number}"'
        with self.con:
            data = self.con.execute(sql).fetchone()
        if data == None:
            logging.info(f'"{ticket_number}" does not exist.')
            return False
        else:
            logging.info(f'"{ticket_number}" exists.')
            return True

    def update_status_by_ticket_number(self, ticket_number, status, date=datetime.datetime.now().strftime('%Y-%m-%d')):
        """Update status on database row of given ticket_number.

        args:
            ticket_number (str): Identification value for ticketing system to update.
            status (str): New status to be added to database row.
        kwargs:
            date (str): [default: current date YYYY-MM-DD] Date ticket was created.

        Return (bool): Confirmation of update.
        """
        isinstance(ticket_number, str)
        isinstance(status, str)
        isinstance(date, str)

        sql = f'UPDATE tickets SET status="{status}", modified_date="{date}" WHERE ticket_id="{ticket_number}"'

        try:
            with self.con:
                data = self.con.execute(sql)
                logging.info(
                    f'Successfully updated status for "{ticket_number}"')
                return True
        except:
            logging.info(
                f'"{ticket_number}" is either already in a completed state or does not exist in "{self.db_name}"')
            return False

    def check_by_plugin_id(self, plugin_id):
        """Given a plugin id check if it exists in the database

        args:
            plugin_id (str): Plugin id for a given vulnerability.

        return (bool): Confirmation of exisitance.
        """
        assert isinstance(plugin_id, str)
        sql = f'SELECT * FROM tickets WHERE plugin_id="{plugin_id}"'
        with self.con:
            data = self.con.execute(sql).fetchall()
        if data == None:
            logging.info(f'"{plugin_id}" does not exist.')
            return False
        else:
            logging.info(f'"{plugin_id}" exists.')
            return True

    def get_by_plugin_id(self, plugin_id):
        """Given a plugin id return ticket_id and status

        args:
            plugin_id (str): Plugin id for a given vulnerability.

        return (list): List of each ticket_id and status
        """
        assert isinstance(plugin_id, str)
        sql = f'SELECT * FROM tickets WHERE plugin_id="{plugin_id}"'
        with self.con:
            data = self.con.execute(sql).fetchall()
        if data == None:
            logging.info((f'No data found for "{plugin_id}"'))
            return None
        else:
            logging.info(f'""')

        # TODO: This is still incomplete and is a work in progress

    def get_all_tickets_by_plugin_id(self, plugin_id):
        """Given a plugin id get all tickets with working statuses.
            i.e. Ticket status can not be in self.ignore_statuses

        args:
            plugin_id (str): Plugin if for a given vulnerability

        return (list): List of all tickets.
        """
        assert isinstance(plugin_id, str)
        ignore_statuses = ['status != "{}"'.format(
            x) for x in self.ignore_statuses]
        where = ' AND '.join(ignore_statuses)
        sql = f'SELECT * FROM tickets WHERE plugin_id="{plugin_id}" AND {where}'

        with self.con:
            data = self.con.execute(sql).fetchall()

        return data

    def get_all_tickets(self):
        if len(self.ignore_statuses) != 0:
            ignore_statuses = ['status != "{}"'.format(
                x) for x in self.ignore_statuses]
            where = ' AND '.join(ignore_statuses)
            sql = f'SELECT ticket_id FROM tickets WHERE {where}'
        else:
            sql = 'SELECT ticket_id FROM tickets'

        with self.con:
            data = self.con.execute(sql).fetchall()

        return data


if __name__ == '__main__':
    db = TenableSqliteVulnDB('tickets.db')
    print(db.get_all_tickets_by_plugin_id('5192'))
