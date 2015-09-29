#!/usr/bin/python

import sys
import os
import json
import geojson
import csv
import argparse
import urlparse
import requests
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean
from sqlalchemy.types import Text, BigInteger
from sqlalchemy.schema import ForeignKey
from sqlalchemy.sql import delete
from sqlalchemy.orm import sessionmaker, mapper, relation
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.ext.declarative import declarative_base

from pylons import config

from ckanext.publicamundi.model import Base

from geoalchemy import GeometryColumn, Geometry, WKTSpatialElement
from shapely.geometry import shape

class Organization(object):
    pass
class Group(object):
    pass
class Package(object):
    pass
class PackageGroup(object):
    pass
class Resource(object):
    pass
class TreeNode(object):
    pass
class Queryable(object):
    pass
class Field(object):
    pass

class MapsRecords(object):
    # Declare data model
        
    def __init__(self):
        self.engine = None
        self.metadata = None
        self.session = None
        #self._cleanup()

        self._initialize_session()
        self._initialize_model()

    def _initialize_session(self):
        engine = config.get('ckanext.publicamundi.maps_db')
        self.engine = create_engine(engine)
        session_factory = sessionmaker(bind=self.engine)

        self.session = session_factory()
        self.metadata = MetaData()

    def _initialize_model(self):
        if self.session:
            self.organizations = Table('organization',
                                  self.metadata,  
                                  autoload=True,
                                  autoload_with=self.engine)


            self.groups = Table('group',
                           self.metadata,  
                           autoload=True,
                           autoload_with=self.engine)


            self.packages = Table('package',
                             self.metadata,
                             #Column('the_geom', Geometry(4326)),
                             Column('organization', Text, ForeignKey('organization.id')),
                             autoload=True,
                             autoload_with=self.engine)

            self.package_groups = Table('package_group',
                                   self.metadata,
                                   Column('package_id', Text, ForeignKey('package.id')),
                                   Column('group_id', Text, ForeignKey('group.id')),
                                   autoload=True, 
                                   autoload_with=self.engine)
            
            self.tree_nodes = Table('resource_tree_node',
                               self.metadata,
                               Column('parent', BigInteger, ForeignKey('resource_tree_node.id')),
                               autoload = True,
                               autoload_with = self.engine)
                        
            self.resources = Table('resource',
                               self.metadata,
                               Column('package', Text, ForeignKey('package.id')),
                               Column('tree_node_id', Text, ForeignKey('resource_tree_node.id')),
                               autoload=True,
                               autoload_with=self.engine)
            
            
            self.queryables = Table('resource_queryable',
                               self.metadata,
                               Column('resource', Text, ForeignKey('resource.id')),
                               autoload=True,
                               autoload_with=self.engine)
                               
            self.fields = Table('resource_field',
                           self.metadata,
                           Column('queryable', Text, ForeignKey('resource_queryable.id')),
                           autoload=True,
                           autoload_with=self.engine)
            
            # Do the mappings only once
            # Why does it map class with two classes? (causes exception)
            try:
                mapper(Organization, self.organizations)
                mapper(Group, self.groups)
                mapper(PackageGroup, self.package_groups, properties={
                    # M:1 relations. No lazy loading is used.
                    'packageRef':relation(Package, lazy=False),
                    'groupRef':relation(Group, lazy=False)
                    })

                mapper(Package, self.packages, properties = {
                    # M:1 relation
                    'organizationRef': relation(Organization, uselist=False, remote_side=[self.organizations.c.id], lazy=False),
                    # M:N relation. No lazy loading is used.
                    'groups': relation(PackageGroup, lazy=False),
                    })

                mapper(TreeNode, self.tree_nodes, properties={
                    # Add a reference to the parent group. It is important to set remote_side parameter since the relation is a many-to-one
                    # relation. Moreover, since this is a self-referencing relation, join_depth parameter must be also set in order to avoid
                    # querying the database for the parent of each group.
                    'parentRef': relation(TreeNode, uselist=False, remote_side=[self.tree_nodes.c.id], lazy=False, join_depth=1)
                    })
                
                mapper(Resource, self.resources, properties = {
                    # M:1 relation
                    'packageRef': relation(Package, uselist=False, remote_side=[self.packages.c.id], lazy=False),
                    # M:1 relation
                    'treeNodeRef': relation(TreeNode, uselist=False, remote_side=[self.tree_nodes.c.id], lazy=False),
                    # 1:1 relation. No lazy loading is used. Allow cascading deletes
                    'queryableRef': relation(Queryable, lazy=False, backref='resourceRef', cascade="all, delete, delete-orphan")
                    })

                mapper(Field, self.fields)
                mapper(Queryable, self.queryables, properties = {
                    # 1:M relation. No lazy loading is used. Allow cascading deletes
                    'fields': relation(Field, lazy=False, backref='queryableRef', cascade="all, delete, delete-orphan")
                    })
            except Exception as ex:
                print 'TRYING TO MAP AGAIN'
                print ex

    def get_resources(self, sorting=None, filters=None):
        res = self._get_all_records(Resource)
        resources = []
        for it in res:
            resources.append(self._as_dict(it))

        return resources

    def get_resource_fields(self, resource_id):
        #res = self._get_all_records(Resource)
        #res = self.session.query(Resource).filter(Resource.id == resource_id).join(Resource.queryable).first()
        res = self.session.query(Field).join(Queryable).filter(Queryable.resource == resource_id).all()
        if not res:
            return {}
        else:
            fields = []
            
            for it in res:
                print it
                fields.append(self._as_dict(it))

            return fields

    
    def _as_dict(self, row):
        return self._filter_dict(row.__dict__)

    def _filter_dict(self, dict):
        d = {}
        for k, v in dict.iteritems():
            if not k == '_sa_instance_state':
            #if type(v) is 'object':
                #print 'del'
                #del dict[k]
                d[k] = v
        return d

    def _commit(self):
        try:
            print 'committing'
            self.session.commit()
        except Exception as ex:
            print 'exception'
            print ex
            self.session.rollback()

    def _get_all_records(self, Table):
        return self.session.query(Table).all()

    def _update_object_with_dict(self, db_entry, rec):
        for reck, recv in rec.iteritems():
            setattr(db_entry, reck, recv)
        return db_entry

    def update_resources(self, resources):
        # have to handle 
        # 1. if in resources and not in db -> INSERT
        # 2. if in db and not in resources -> UPDATE (visible: False)
        # 3. if in db and in resources -> UPDATE (all values in dict)

        db_entries = self._get_all_records(Resource)

        # start by making all Resource objects invisible
        for db_entry in db_entries:
            db_entry.visible = False

        for res in resources:
            found = False
            for db_entry in db_entries:
                if db_entry.id == res.get("id"):
                    # found, so update (#3)
                    found = True
                    db_entry = self._update_object_with_dict(db_entry, res)
            if not found:
                # not found, so insert (#1)
                db_entry = Resource()
                db_entry = self._update_object_with_dict(db_entry, res)
                self.session.add(db_entry)

        self._commit()

    def update_tree_nodes(self, tree_nodes):
        # have to handle 
        # 1. if in tree_nodes and not in db -> INSERT
        # 2. if in db and not in tree_nodes -> DELETE
        print 'UPDATING TREENODES'
        print tree_nodes
    
        db_entries = self._get_all_records(TreeNode)

        # start by removing all TreeNodes (#2)
        # TODO: can i avoid this commit?
        print 'deleting previous tnodes'
        for db_entry in db_entries:
            print db_entry.id
            self.session.delete(db_entry)
        self._commit()

        print 'adding new tnodes'
        for node in tree_nodes:
            print node
            # not found, so insert (#1)
            db_entry = TreeNode()
            db_entry = self._update_object_with_dict(db_entry, node)
            self.session.add(db_entry)

        self._commit()

    def update_resource_fields(self, fields):
        # have to handle 
        # 1. just update field with new values (if not in db return)
        print 'UPDATING FIELDS'

        for field in fields:
            db_entry = self.session.query(Field).get(field.get("id"))
            db_entry = self._update_object_with_dict(db_entry, field)

        self._commit()

    def _cleanup(self):
        try:
            if self.session:
                self.session.close()
        except:
            pass

