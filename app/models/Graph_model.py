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
    wiki = relationship("WikiData", uselist=False, backref="entity")
    wiki_link = db.Column(db.String())
    category = db.Column(sqlalchemy_utils.ChoiceType(ownership))
    long_name = db.Column(db.String())
    other_groups = db.Column(db.String())

    def __init__(self, name=None, website=None, wiki=None, wiki_page_id=None, category=None, long_name=None, other_groups=None):
        self.name = name
        self.website = website
        self.wiki = wiki
        self.wiki_page_id = wiki_page_id
        self.category = category
        self.long_name = long_name
        self.other_groups = other_groups

    def __repr__(self):
        return '<Entity: id {} Name {}>'.format(self.id, self.name)

    def get_parents(self):
        return [x.parent for x in self.lower_edges]

    def get_children(self):
        return [x.child for x in self.higher_edges]


class WikiData(db.Model):
    __tablename__ = 'wikidatas'

    id = db.Column(db.Integer, primary_key=True)
    entity_id = db.Column(db.Integer, ForeignKey('entities.id'))
    # entity = relationship(Entity, primaryjoin= entity_id == Entity.id, backref='entities')
    title = db.Column(db.String())
    lang = db.Column(db.String())

    def __repr__(self):
        return '<WD: id {} title {}>'.format(self.id, self.title)

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
        backref='parents')

    parent = relationship(
        Entity,
        primaryjoin=parent_id == Entity.id,
        backref='children')

    value = db.Column(db.Integer)

    special = db.Column(db.String())

    def __init__(self, parent, child, value=None, special=None):
        self.child = child
        self.parent = parent
        self.value = value
        self.special = special

    def __repr__(self):
        return '<Edge: {} -> {}>'.format(self.value, self.parent.name, self.child.name)


class DBMetaData(db.Model):
    __tablename__ = 'db_meta_data'

    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String())
    version_string = db.Column(db.String())
    description = db.Column(db.String())

    def __repr__(self):
        return '<DBMetaData version:{}>'.format(self.version)
