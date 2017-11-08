from app import db
from sqlalchemy.dialects.postgresql import JSON
import sqlalchemy_utils
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey


class Entity(db.Model):

    __tablename__ = 'entities'

    # If you change this, be sure to update migration afdf112384be
    ownership = [
        ('c', 'company'),
        ('i', 'individual'),
        ('m', 'media'),
        ('o', 'other')
    ]

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    website = db.Column(db.String())
    wiki = db.Column(db.String())
    wiki_page_id = db.Column(db.Integer, default=-1)
    category = db.Column(sqlalchemy_utils.ChoiceType(ownership))
    long_name = db.Column(db.String())
    other_groups = db.Column(db.String())

    def __init__(self, name, website=None, wiki=None, category=None, long_name=None, other_groups=None):
        self.name = name
        self.website = website
        self.wiki = wiki
        self.category = category
        self.long_name = long_name
        self.other_groups = other_groups

    def __repr__(self):
        return '<Entity: id {} Name {}>'.format(self.id, self.name)

    def get_parents(self):
        return [x.parent for x in self.lower_edges]

    def get_children(self):
        return [x.child for x in self.higher_edges]


class Edge(db.Model):
    __tablename__ = 'edges'

    child_id = db.Column(
        db.Integer,
        ForeignKey('entities.id'),
        primary_key=True)

    parent_id = db.Column(
        db.Integer,
        ForeignKey('entities.id'),
        primary_key=True)

    child = relationship(
        Entity,
        primaryjoin=child_id == Entity.id,
        backref='children')

    parent = relationship(
        Entity,
        primaryjoin=parent_id == Entity.id,
        backref='parents')

    value = db.Column(db.Integer)

    special = db.Column(db.String())

    def __init__(self, parent, child, value=None, special=None):
        self.child = child
        self.parent = parent
        self.value = value
        self.special = special

    def __repr__(self):
        return '<Edge:{} {} -> {}>'.format(self.value, self.parent.name, self.child.name)


class DBMetaData(db.Model):
    __tablename__ = 'db_version'

    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.Integer)
    description = db.Column(db.String())

    def __repr__(self):
        return '<DBMetaData version:{}>'.format(self.version)
