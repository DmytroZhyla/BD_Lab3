#!/usr/bin/env python3

# import psycopg2
# import psycopg2.sql
# import psycopg2.extensions
import Lab.utils
import peewee


from . import DynamicSearch
from .AutoSchema import *


database_proxy = peewee.DatabaseProxy()


class Library_table(peewee.Model):
	class Meta(object):
		database = database_proxy
		schema = f"Library_loan"


class Author(Library_table):
	Full_name = peewee.CharField(max_length=255, null=False)
	Pseudonym = peewee.CharField(max_length=255, null=False)
	experience = peewee.BigIntegerField(null=False)


class Reader(Library_table):
	Full_Name = peewee.CharField(max_length=255, null=False)
	Age = peewee.BigIntegerField(null=False)


class Books(Library_table):
	date_of_printing = peewee.DateTimeField(null=False)
	Name = peewee.CharField(max_length=255, null=False)
	Author = peewee.ForeignKeyField(Author, backref="books")
	Reader_id = peewee.ForeignKeyField(Reader, backref="readed")


class Library(Library_table):
	year_of_foundation = peewee.DateTimeField(null=False)
	address = peewee.CharField(max_length=255, null=False)
	capacity = peewee.BigIntegerField(null=False)
	Reader_id = peewee.ForeignKeyField(Reader, backref="libraries")


class LibraryBooks(Library_table):
	Library_id = peewee.ForeignKeyField(Library, backref="books")
	Book_id = peewee.ForeignKeyField(Books, backref="libraries")


class AuthorTable(SchemaTableORM):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.ORM = Author


class ReaderTable(SchemaTableORM):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.ORM = Reader


class BooksTable(SchemaTableORM):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.ORM = Books


class LibraryTable(SchemaTableORM):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.ORM = Library


class LibraryBooksTable(SchemaTableORM):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.ORM = LibraryBooks


class Library_loan(Schema):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._dynamicsearch = {a.name: a for a in [DynamicSearch.BooksDynamicSearch(self), DynamicSearch.ReaderLoanDynamicSearch(self), DynamicSearch.ReaderDynamicSearch(self), ]}
		database_proxy.initialize(self.dbconn)
		# self.reoverride()

	def reoverride(self):
		# print(f"reoverride")
		# Table override
		self.tables.Author = AuthorTable(self, f"author")
		self.tables.Reader = ReaderTable(self, f"reader")
		self.tables.Books = BooksTable(self, f"books")
		self.tables.Library = LibraryTable(self, f"library")
		self.tables.LibraryBooks = LibraryBooksTable(self, f"librarybooks")


	def reinit(self):
		# sql = f"""
		# 	SELECT table_name FROM information_schema.tables
		# 	WHERE table_schema = '{self}';
		# """
		with self.dbconn.cursor() as dbcursor:
			# dbcursor.execute(sql)
			for a in self.refresh_tables():  # tuple(dbcursor.fetchall()):
				q = f"""DROP TABLE IF EXISTS {a} CASCADE;"""
				# print(q)
				dbcursor.execute(q)
		# self.dbconn.commit()
		self.dbconn.create_tables([Author, Reader, Books, Library, LibraryBooks, ])
		self.dbconn.commit()
		tables = self.refresh_tables()
		# print(tables)
		self.reoverride()

	def randomFill(self):
		self.tables.Author.randomFill(1_000)
		self.tables.Reader.randomFill(1_000)
		self.tables.Books.randomFill(1_000)
		self.tables.Library.randomFill(1_000)
		self.tables.LibraryBooks.randomFill(1_000)


def _test():
	pass


if __name__ == "__main__":
	_test()
