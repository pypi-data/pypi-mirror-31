#!/usr/bin/env python3
# pylint: disable=too-many-arguments,duplicate-code

import copy
import datetime
import singer
import time

import singer.metrics as metrics
from singer import utils

LOGGER = singer.get_logger()

def escape(string):
    if '`' in string:
        raise Exception("Can't escape identifier {} because it contains a backtick"
                        .format(string))
    return '`' + string + '`'


def get_stream_version(tap_stream_id, state):
    stream_version = singer.get_bookmark(state, tap_stream_id, 'version')

    if stream_version is None:
        stream_version = int(time.time() * 1000)

    return stream_version


def generate_column_list(catalog_entry):
    return list(catalog_entry.schema.properties.keys())


def generate_select_sql(catalog_entry, columns):
    escaped_db = escape(catalog_entry.database)
    escaped_table = escape(catalog_entry.table)
    escaped_columns = [escape(c) for c in columns]

    select_sql = 'SELECT {} FROM {}.{}'.format(
        ','.join(escaped_columns),
        escaped_db,
        escaped_table)

    return select_sql


def row_to_singer_record(catalog_entry, version, row, columns, time_extracted):
    row_to_persist = ()
    for idx, elem in enumerate(row):
        property_type = catalog_entry.schema.properties[columns[idx]].type
        if isinstance(elem, datetime.datetime):
            row_to_persist += (elem.isoformat() + '+00:00',)

        elif isinstance(elem, datetime.date):
            row_to_persist += (elem.isoformat() + 'T00:00:00+00:00',)

        elif isinstance(elem, datetime.timedelta):
            epoch = datetime.datetime.utcfromtimestamp(0)
            timedelta_from_epoch = epoch + elem
            row_to_persist += (timedelta_from_epoch.isoformat() + '+00:00',)

        elif isinstance(elem, bytes):
            # for BIT value, treat 0 as False and anything else as True
            boolean_representation = elem != b'\x00'
            row_to_persist += (boolean_representation,)

        elif 'boolean' in property_type or property_type == 'boolean':
            if elem is None:
                boolean_representation = None
            elif elem == 0:
                boolean_representation = False
            else:
                boolean_representation = True
            row_to_persist += (boolean_representation,)

        else:
            row_to_persist += (elem,)
    rec = dict(zip(columns, row_to_persist))

    return singer.RecordMessage(
        stream=catalog_entry.stream,
        record=rec,
        version=version,
        time_extracted=time_extracted)


def sync_query(cursor, catalog_entry, state, select_sql, columns, stream_version, params):
    replication_key = singer.get_bookmark(state,
                                          catalog_entry.tap_stream_id,
                                          'replication_key')

    query_string = cursor.mogrify(select_sql, params)

    time_extracted = utils.now()

    LOGGER.info('Running %s', query_string)
    cursor.execute(select_sql, params)

    row = cursor.fetchone()
    rows_saved = 0

    with metrics.record_counter(None) as counter:
        counter.tags['database'] = catalog_entry.database
        counter.tags['table'] = catalog_entry.table

        while row:
            counter.increment()
            rows_saved += 1
            record_message = row_to_singer_record(catalog_entry,
                                                  stream_version,
                                                  row,
                                                  columns,
                                                  time_extracted)
            yield record_message

            if replication_key is not None:
                state = singer.write_bookmark(state,
                                              catalog_entry.tap_stream_id,
                                              'replication_key_value',
                                              record_message.record[replication_key])
            if rows_saved % 1000 == 0:
                yield singer.StateMessage(value=copy.deepcopy(state))

            row = cursor.fetchone()

    yield singer.StateMessage(value=copy.deepcopy(state))
