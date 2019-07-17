from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declared_attr, has_inherited_table
from datetime import datetime

# from sqlalchemy.exc import SQLAlchemyError

from flask import current_app

app = current_app
db = SQLAlchemy()

# __all__ = ('QueryMixin',)


def row2dict(row):
    if row is None:
        return ""
    d = {}
    for column in row.__table__.columns:
        if isinstance(getattr(row, column.name), str):
            d[column.name] = getattr(row, column.name)
        elif isinstance(getattr(row, column.name), datetime):
            d[column.name] = str(getattr(row, column.name))
        else:
            # d[column.name] = str(getattr(row, column.name))
            d[column.name] = getattr(row, column.name)
    return d


class QueryMixin(object):
    """
        Mixin class for database queries.
        Usage:
            # create & save objects
            user = User(name=u'John Doe', age=32, email=u'johndoe@example.org', city=u'Los Angeles', state=u'CA')
            user.save()

            users = User.find(state='CA')
            users.update(dict(country='US'))

            # Find some users
            users_who_are_32 = User.find(age=32)
            users_in_los_angeles = User.find(city=u'Los Angeles')
            users_in_ca = User.find(state=u'CA')
            los_angelinos_who_are_32 = User.find(city=u'Los Angeles', age=32)
            users_in_30s = User.find_in(age=range(30,40))
            users_not_in_ca_or_wa = User.find_not_in(state=(u'CA',u'WA'))
            users_in_southeast = User.find_in(state=(u'GA', u'TN', u'AL', u'MS', u'NC', u'SC'))

    """

    # CRUD methods
    def save(self):
        """Save instance to database."""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Delete instance."""
        db.session.delete(self)
        db.session.commit()

    # def update(self, **kargs):
    #     """
    #         Update instance
    #     """
    #     db.session.update(**kargs)
    #     db.session.commit()

    # Query helpers
    @classmethod
    def exists(cls, **kwargs):
        """Checks if record matching kwargs exists in the database.

        Returns True/False.
        """
        return db.session.query(cls._and_query(kwargs).exists()).all()[0][0]

    @classmethod
    def find(cls, **kwargs):
        """Return filtered AND query results for passed in kwargs.

        Example:

            # find all instances of MyModel for first name 'John' AND last name 'Doe'
            MyModel.find(first_name='John', last_name='Doe')

        Returns result list or None.
        """
        return cls._and_query(kwargs)

    @classmethod
    def find_or(cls, **kwargs):
        """Return filtered OR query results for passed in kwargs.

        Example:

            # find all instances of MyModel for first name 'John' OR last name 'Doe'
            MyModel.find_or(first_name='John', last_name='Doe')

        Returns result list or None.
        """
        return cls._or_query(kwargs)

    @classmethod
    def find_in(cls, _or=False, **kwargs):
        """Return filtered query results for passed in attrs that match a list.

        Query defaults to an AND query. If you want an OR query, pass _or=True.
        """
        if _or:
            return cls._or_in_query(kwargs)
        else:
            return cls._and_in_query(kwargs)

    @classmethod
    def find_not_in(cls, _or=False, **kwargs):
        """Return filtered query results for passed in attrs that do not match
        a list.

        Query defaults to an AND query. If you want an OR query, pass _or=True.
        """
        if _or:
            return cls._or_not_in_query(kwargs)
        else:
            return cls._and_not_in_query(kwargs)

    @classmethod
    def find_not_null(cls, *args):
        """Return filtered query results for passed in attrs that are not None.

        Example:

            # find all instances of MyModel where email and phone != null
            MyModel.find_not_null('email', 'phone')

        NOTE: Filtering for JSON types that are not NULL does not work. JSON
        must be cast to at least text to check for a NULL value. You can verify
        this yourself in the `psql` client like so:

            # you will see null results show up
            select * from form where custom_fields is not null;

            # you will not see null results
            select * from form where custom_fields::text != 'null';

        Returns result list or None.
        """
        filters = [getattr(cls, attr) != None for attr in args]
        return cls.query.filter(*filters)

    @classmethod
    def first(cls, **kwargs):
        """Return first result for query.

        Returns instance or None.
        """
        return cls._and_query(kwargs).first()

    @classmethod
    def first_or_404(cls, **kwargs):
        """Get first item that matches kwargs or raise 404 error."""
        item = cls._and_query(kwargs).first()
        if item is None:
            return
        else:
            return item

    @classmethod
    def get(cls, id):
        """Get item by primary key.

        Returns instance or `None`.
        """
        return cls.query.get(id)

    @classmethod
    def get_active_or_404(cls, id):
        """Get item by primary key or 404 only if it is active."""
        item = cls.query.get_or_404(id)
        if item.active:
            return item
        else:
            return

    @classmethod
    def get_or_404(cls, id):
        """Get item by primary key or 404."""
        return cls.query.get_or_404(id)

    ########################################
    # Internal methods; Do not use directly
    ########################################
    @classmethod
    def _filters(cls, filters):
        """Return filter list from kwargs."""
        return [getattr(cls, attr) == filters[attr] for attr in filters]

    @classmethod
    def _filters_in(cls, filters):
        """Return IN filter list from kwargs."""
        return [getattr(cls, attr).in_(filters[attr]) for attr in filters]

    @classmethod
    def _filters_not_in(cls, filters):
        """Return NOT IN filter list from kwargs."""
        return [getattr(cls, attr).notin_(filters[attr]) for attr in filters]

    @classmethod
    def _and_query(cls, filters):
        """Execute AND query.

        Returns BaseQuery.
        """
        return cls.query.filter(db.and_(*cls._filters(filters)))

    @classmethod
    def _and_in_query(cls, filters):
        """Execute AND query.

        Returns BaseQuery.
        """
        return cls.query.filter(db.and_(*cls._filters_in(filters)))

    @classmethod
    def _and_not_in_query(cls, filters):
        """Execute AND NOT IN query.

        Returns BaseQuery.
        """
        return cls.query.filter(db.and_(*cls._filters_not_in(filters)))

    @classmethod
    def _or_query(cls, filters):
        """Execute OR query.

        Returns BaseQuery.
        """
        return cls.query.filter(db.or_(*cls._filters(filters)))

    @classmethod
    def _or_in_query(cls, filters):
        """Execute OR IN query.

        Returns BaseQuery.
        """
        return cls.query.filter(db.or_(*cls._filters_in(filters)))

    @classmethod
    def _or_not_in_query(cls, filters):
        """Execute OR NOT IN query.

        Returns BaseQuery.
        """
        return cls.query.filter(db.or_(*cls._filters_not_in(filters)))
