# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals
import pandas as pd
from .dbutils import db_sqlalchemy_str, get_table_fields, getDB
from pandas.io.sql import pandasSQL_builder
from sqlalchemy import sql


def get_select_sql(sql):
    sql=sql.strip()
    return ' ' in sql.lower() and sql or (u'select * from %s' % sql)


def get_dataframe_from_table(table_name_or_sql, connection="default"):
    sql=get_select_sql(table_name_or_sql).replace("%", "%%")
    print sql
    return pd.read_sql(sql, db_sqlalchemy_str(connection))


def write_dataframe_to_table(df, **kwargs):
    kwargs['con'] = db_sqlalchemy_str(kwargs['con'])
    return df.to_sql(**kwargs)


def smart_write_dataframe_to_table(df, **kwargs):
    con = db_sqlalchemy_str(kwargs['con'])


def dtype(dt):
    return dt.startswith('int') and 'int' \
           or dt.startswith('float') and 'float' \
           or dt.startswith('datetime') and 'datetime' \
           or 'string'


def ftype(ft):
    return ft == "string" and "varchar(255)" or ft


class AutoGrowTable(object):
    def __init__(self, db_name, table_name, primary_key):
        self.db_name = db_name
        self.table_name = table_name
        self.primary_key = primary_key
        self.fields = {}
        self.connection = getDB(self.db_name)
        self.pd_sql = pandasSQL_builder(db_sqlalchemy_str(self.db_name))
        self.detect_fields()

    def detect_fields(self):
        try:
            self.fields = get_table_fields(getDB(self.db_name), self.table_name)
        except:
            pass

    def get_field_definition(self, fields):
        return ",".join(["%s %s" % (f, ftype(f)) for f in fields])

    def run(self, data_frame):
        df = data_frame
        exists = self.pd_sql.has_table(self.table_name)
        dtypes = dict([(c, dtype(str(dt))) for c, dt in df.dtypes.iteritems()])
        se = self.connection.schema_editor
        new_fields = ["%s %s" % (f, ftype(dt)) for f, dt in dtypes.iteritems() if f not in self.fields]
        print new_fields
        with self.connection.cursor() as cursor:
            if not exists:
                sql = "create table %s(%s)" % (self.table_name, ",".join(new_fields))
                print sql
                cursor.execute(sql)
                cursor.execute("alter table %s add primary key(%s)" % (self.table_name, self.primary_key))
                self.detect_fields()
            else:
                if new_fields:
                    cursor.execute("alter table %s add column %s" % (self.table_name, ", add column ".join(new_fields)))

        from pandas.io.sql import SQLTable
        self.table = SQLTable(self.table_name, self.pd_sql, df).table.tometadata(self.pd_sql.meta)
        self.insert(df)
        return

    def split_insert_and_update(self, df):
        # self.table.select(  df[self.primary_key]
        pass

    def insert(self, df):
        df = df.fillna(0)
        with self.connection.cursor() as cursor:
            sql_template = "select 1 from %s where %%s" % self.table_name
            for r in xrange(len(df)):
                s = df.iloc[r]
                where = "%s='%s'" % (self.primary_key, s[self.primary_key])
                sql = sql_template % where
                cursor.execute(sql)
                if cursor.fetchone():
                    self.table.update().where(where).values(s.to_dict()).execute()
                else:
                    self.table.insert(s.to_dict()).execute()

    def update(self, df):
        for r in xrange(len(df)):
            self.table.update(df.iloc[r].to_dict()).execute()
