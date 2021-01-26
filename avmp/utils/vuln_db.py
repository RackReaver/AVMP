"""Class functions for managing a sqlite database for Tenable vulnerabilities.
"""
__copyright__ = "Copyright (C) 2020  Matt Ferreira"
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
            print('[INFO] - DB Not Found...')
            self._build_db()

        self.con = sqlite3.connect(filepath)
        self.ignore_statuses = ignore_statuses

    def _build_db(self):
        print('[INFO] - Building DB now...')

        con = sqlite3.connect(self.db_name)

        with con:
            con.execute("""
                    CREATE TABLE "tickets" (
                    "ticket_id"	TEXT NOT NULL,
                    "plugin_id"	TEXT NOT NULL,
                    "status"	INTEGER,
                    "create_date"	TEXT NOT NULL,
                    "modified_date"	TEXT NOT NULL,
                    PRIMARY KEY("ticket_id"))
                    """)
            con.execute("""
                    CREATE TABLE "ip_addresses" (
                    "id"	INTEGER NOT NULL UNIQUE,
                    "ip_address"	TEXT NOT NULL,
                    "ticket_id"	TEXT NOT NULL,
                    PRIMARY KEY("id" AUTOINCREMENT))
                    """)

    def add_ticket(self, ticket_number, plugin_id, status, ip_addresses, date=datetime.datetime.now().strftime('%Y-%m-%d')):
        """Add a created ticket to database.

        args:
            ticket_number (str): Identification value for ticketing system.
            plugin_id (str): Plugin ID provided by Tenable.
            status (str): Status of new ticket in ticketing system.
            ip_addresses (list): List of ip's associated with ticket.
        kwargs:
            date (str): [default: current date YYYY-MM-DD] Date ticket was created.

        Return (bool): Confirmation of completion.
        """
        isinstance(ticket_number, str)
        isinstance(plugin_id, str)
        isinstance(status, str)
        isinstance(ip_addresses, list)
        isinstance(date, str)

        try:
            assert self.check_by_ticket_number(
                ticket_number) == False, 'Ticket already exists in DB'
        except AssertionError:
            logging.exception(
                f'"{ticket_number}" is already in "{self.db_name}"')
            return False

        sql = 'INSERT INTO tickets (ticket_id, plugin_id, status, create_date, modified_date) '
        sql += 'values ("{}","{}","{}","{}","{}")'.format(ticket_number,
                                                          plugin_id,
                                                          status,
                                                          date,
                                                          date
                                                          )
        with self.con:
            self.con.execute(sql)

        for ip in ip_addresses:
            sql = 'INSERT INTO ip_addresses (ticket_id, ip_address) '
            sql += 'values ("{}","{}")'.format(ticket_number, ip)

            with self.con:
                self.con.execute(sql)

        return True

    def check_by_ticket_number(self, ticket_number):
        """Given a ticket number check if it exists in the database.

        args:
            ticket_number (str): Identification value for ticketing system to check.

        Return (bool): Confirmation of existance.
        """
        isinstance(ticket_number, str)
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

        status_check = ''
        for item in self.ignore_statuses:
            status_check += f'AND status != "{item}" '

        sql = f'UPDATE tickets SET status="{status}", modified_date="{date}" WHERE ticket_id="{ticket_number}" {status_check}'

        with self.con:
            data = self.con.execute(sql).fetchone()

        if data == None:
            logging.info(
                f'"{ticket_number}" is either already in a completed state or does not exist in "{self.db_name}"')
            return False
        else:
            logging.info(f'Successfully updated status for "{ticket_number}"')
            return True
