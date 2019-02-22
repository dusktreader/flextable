import flask_buzz
import collections
import functools
import sqlalchemy
import sqlalchemy.ext
import sqlalchemy.ext.declarative
import sqlalchemy.ext.hybrid
import sqlalchemy.ext.mutable
import sqlalchemy.dialects.postgresql
import textwrap
import re


class FlexError(flask_buzz.FlaskBuzz):
    pass


def dedent(text):
    """
    Dedents a block of indented text and removes any leading or tailing
    whitespace for the block
    """
    return textwrap.dedent(text).strip()


class SetTableMixin(sqlalchemy.ext.declarative.AbstractConcreteBase):

    db = None

    @classmethod
    def bind_db(cls, db):
        cls.db = db

    @classmethod
    @functools.lru_cache()
    def col_attr_keys(cls):
        """
        Gets a named tuple of attribute keys for the model where the attribute
        behaves like a column. The following types are included::
          * columns:       Actual columns on the underyling table
          * relationships: SQLAlchemy relationship attributes for the model
          * hybrids:       SQLAlchemy hybrid attributes of the model
          * primaries:     Includes just hybrids and columns
          * all:           All column-like attributes
        """
        AttrKeys = collections.namedtuple(
            "AttrKeys", ["all", "columns", "hybrids", "primaries", "relationships"]
        )
        inspection = sqlalchemy.inspection.inspect(cls)
        hybrids = [
            k
            for (k, v) in inspection.all_orm_descriptors.items()
            if v.extension_type is sqlalchemy.ext.hybrid.HYBRID_PROPERTY
        ]
        base_attrs = [a for a in inspection.attrs if not a.key.startswith("_sa_")]
        columns = [
            a.key
            for a in base_attrs
            if type(a) is not sqlalchemy.orm.properties.RelationshipProperty
        ]
        relationships = [
            a.key
            for a in base_attrs
            if type(a) is sqlalchemy.orm.properties.RelationshipProperty
        ]
        primaries = columns + hybrids
        all = relationships + primaries
        return AttrKeys(
            all=all,
            columns=columns,
            hybrids=hybrids,
            primaries=primaries,
            relationships=relationships,
        )

    def __repr__(self):
        pk_names = [
            k.name for k in sqlalchemy.inspection.inspect(self.__class__).primary_key
        ]
        pk_values = [str(getattr(self, n)) for n in pk_names]
        pk_string = ",".join(pk_values)

        try:
            name_string = f"{self.name}:"
        except AttributeError:
            name_string = ""

        return f"{self.__class__.__name__} ({name_string}{pk_string})"

    def __str__(self):
        attr_dict = self.to_dict()
        sorted_attrs = [(k, attr_dict[k]) for k in sorted(attr_dict.keys())]
        return "\n    ".join(
            [f"{repr(self)}:"] + [f"{k}: {repr(v)}" for (k, v) in sorted_attrs]
        )

    def to_dict(self):
        return {k: getattr(self, k) for k in self.col_attr_keys().all}

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def update(self, **attrs):
        self.check_db()
        with FlexError.handle_errors(
            f"Couldn't update instance {repr(self)} with attrs {attrs}"
        ):
            for (key, value) in attrs.items():
                self[key] = value
            with self.db.session.begin_nested():
                self.db.session.merge(self)
        return self

    def delete(self):
        self.check_db()
        with FlexError.handle_errors(f"Couldn't delete instance {repr(self)}"):
            with self.db.session.begin_nested():
                self.db.session.delete(self)

    @classmethod
    def check_db(cls):
        FlexError.require_condition(
            cls.db is not None,
            f"db is not bound. you must call {cls.__name__}.bind_db() first",
        )

    @classmethod
    def create(cls, **attrs):
        cls.check_db()
        with FlexError.handle_errors(
            f"Couldn't create instance of {cls.__name__} with attrs {attrs}"
        ):
            self = cls()
            for (key, value) in attrs.items():
                self[key] = value
            with self.db.session.begin_nested():
                self.db.session.add(self)
        return self


class FlexTableMixin(SetTableMixin):

    flex_data = sqlalchemy.Column(
        sqlalchemy.ext.mutable.MutableDict.as_mutable(
            sqlalchemy.dialects.postgresql.JSONB
        ),
        default={},
        server_default="{}",
        nullable=False,
    )

    @classmethod
    @functools.lru_cache()
    def base_keys(cls):
        return {k for k in cls.col_attr_keys().all if k != "flex_data"}

    def flex_keys(self):
        # the flex_data attribute may be none if the instance is not
        # yet 'added'. Defaults are set at mapping time
        current_flex_data = self.flex_data or {}
        return current_flex_data.keys()

    def to_dict(self):
        base_dict = super().to_dict()
        flex_dict = base_dict.pop("flex_data", {})
        overlaps = set(base_dict.keys()).intersection(set(flex_dict.keys()))
        FlexError.require_condition(
            len(overlaps) == 0,
            dedent(
                f"""
                For {repr(self)}, there were conflicts between base and flex
                attributes on keys {overlaps}. Issue must be fixed by logging
                directly into the database and resolving the conflict manually
            """
            ),
        )
        return {**{k: getattr(self, k) for k in self.base_keys()}, **self.flex_data}

    def __getitem__(self, key):
        """
        Notes: * haven't figured out how to retrieve flex_data via __getattr__.
                 instead, flex attributes must be retrieved with this method
               * remember that None values are not stored in the flex_data,
                 so return None if the key is not in the flex_data
        """
        if key in self.base_keys() or key == "flex_data":
            return getattr(self, key)
        else:
            return self.flex_data.get(key)

    def __setitem__(self, key, value):
        """
        Allows setting of first and second order elements.

        .. note:: This method simply sets the attribute on an instance. The
                  the instance is not 'merged' afterward. Use instance.update()
                  to automatically merge new values on instance
        """
        if key in self.base_keys() or key == "flex_data":
            setattr(self, key, value)
        else:
            valid_key_chars = re.compile(r"^[A-Za-z_]\w*$")
            FlexError.require_condition(
                valid_key_chars.match(key),
                dedent(
                    """
                    flex_data attribute keys must contain only letters,
                    numbers, and '_', and cannot start with a number.
                """
                ),
            )
            if value is not None:
                # the flex_data attribute may be none if the instance is not
                # yet 'added'. Defaults are set at mapping time
                current_flex_data = self.flex_data or {}
                self.flex_data = {**current_flex_data, key: value}
