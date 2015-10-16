#!/usr/bin/python

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean
from sqlalchemy.types import Text, BigInteger
from sqlalchemy.schema import ForeignKey
from sqlalchemy.sql import delete
from sqlalchemy.orm import sessionmaker, mapper, relation

from pylons import config

from geoalchemy import Geometry

# Declare data model
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

    def __init__(self):
        self.engine = None
        self.metadata = None
        self.session = None

        self._initialize_session()
        self._initialize_model()

    def _initialize_session(self):
        engine = config.get('ckanext.publicamundi.mapclient_db')
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
                             Column('the_geom', Geometry(4326)),
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
                print 'couldn\' map tables to classes'
                print ex

    def get_all_records(self, Table):
        db_entries = self.session.query(Table).all()
        records = []
        for db_entry in db_entries:
           records.append(self._as_dict(db_entry))
        return records

    def get_record_by_id(self, Table, id):
        db_entry = self.session.query(Table).get(id)
        return self._as_dict(db_entry)

    def insert_records(self, records, Table):
        try:
            for rec in records:
                db_entry = Table()
                db_entry = self._update_object_with_dict(db_entry, rec)
                self.session.add(db_entry)
            self.session.commit()
        except Exception as ex:
            print 'exception'
            print ex
            self.session.rollback()

        return records

    def update_records(self, records, Table):
        try:
            for rec in records:
                db_entry = self.session.query(Table).get(rec.get("id"))
                db_entry = self._update_object_with_dict(db_entry, rec)

            self.session.commit()
        except Exception as ex:
            print 'exception'
            print ex
            self.session.rollback()

        return records

    def upsert_records(self, records, Table):
        try:
            for rec in records:
                db_entry = self.session.query(Table).get(rec.get("id"))
                if db_entry:
                    db_entry = self._update_object_with_dict(db_entry, rec)
                else:
                    db_entry = Table()
                    db_entry = self._update_object_with_dict(db_entry, rec)
                    self.session.add(db_entry)
            self.session.commit()
        except Exception as ex:
            print 'exception'
            print ex
            self.session.rollback()

        return records

    def delete_records(self, records, Table):
        try:
            for rec in records:
                db_entry = self.session.query(Table).get(rec.get("id"))
                if db_entry:
                    self.session.delete(db_entry)
            self.session.commit()
        except Exception as ex:
            print 'exception'
            print ex
            self.session.rollback()

    def delete_all_records(self, Table):
        try:
            db_entries = self.session.query(Table).all()
            for db_entry in db_entries:
                self.session.delete(db_entry)
            self.session.commit()
        except Exception as ex:
            print 'exception'
            print ex
            self.session.rollback()

    def get_resources(self):
        res = self.session.query(Resource).all()
        return self._list_objects_to_dict(res)

    def get_resources_with_packages_organizations(self):
        res = self.session.query(Resource, Package, Organization).filter(Resource.package == Package.id).filter(Package.organization == Organization.id).order_by(Organization.title_el.asc()).order_by(Package.title_el.asc()).all()
        return self._pkg_org_tuples_to_dict(res)

    def get_resource_by_id(self, id):
        return self.get_record_by_id(Resource, id)

    def insert_resources(self, resources):
        return self.insert_records(resources, Resource)

    def update_resources(self, resources):
        return self.update_records(resources, Resource)

    def upsert_resources(self, resources):
        return self.upsert_records(resources, Resource)

    def get_resource_queryable(self, resource_id):
        res = self.session.query(Queryable).filter(Queryable.resource == resource_id).all()
        queryable = self._list_objects_to_dict(res)
        for q in queryable:
            q.update({'fields':\
                    sorted(self._list_objects_to_dict(q.get('fields')), \
                    key=lambda k: k['id'])\
                    })
        if queryable:
            return queryable[0]
        else:
            return None

    def update_resource_fields(self, fields):
        return self.update_records(fields, Field)

    def upsert_resource_fields(self, fields):
        return self.upsert_records(fields, Field)

    def update_resource_queryable(self, queryable):
        return self.update_records(queryable, Queryable)

    def upsert_resource_queryable(self, queryable):
        return self.upsert_records(queryable, Queryable)

    def get_tree_nodes(self):
        return self.get_all_records(TreeNode)

    def delete_tree_nodes(self, tree_nodes):
        return self.delete_records(tree_nodes, TreeNode)

    def delete_all_tree_nodes(self):
        return self.delete_all_records(TreeNode)

    def insert_tree_nodes(self, tree_nodes):
        return self.insert_records(tree_nodes, TreeNode)

    def update_tree_nodes(self, tree_nodes):
        return self.update_records(tree_nodes, TreeNode)

    def upsert_tree_nodes(self, tree_nodes):
        return self.upsert_records(tree_nodes, TreeNode)

    # Helpers
    def _cleanup(self):
        try:
            if self.session:
                self.session.close()
        except:
            pass
   
    def _as_dict(self, row):
        return self._filter_dict(row.__dict__)
    
    def _update_object_with_dict(self, obj, dct):
        for key, value in dct.iteritems():
            setattr(obj, key, value)
        return obj

    def _filter_dict(self, dict):
        d = {}
        for k, v in dict.iteritems():
            if not k == '_sa_instance_state':
            #if type(v) is 'object':
                #print 'del'
                #del dict[k]
                d[k] = v
        return d
         
    def _list_objects_to_dict(self, obj_list):
        res_list = []
        for obj in obj_list:
            res_list.append(self._as_dict(obj))
        return res_list

    def _pkg_org_tuples_to_dict(self, obj_list):
        res_list = []
        for obj in obj_list:
            res = obj[0]
            pkg = obj[1]
            org = obj[2]

            out_dict = self._as_dict(res)
            out_dict.update({"package_name": pkg.name,
                        "organization_name": org.name,
                        "package_title_el": pkg.title_el,
                        "package_title_en": pkg.title_en,
                        "organization_title_el": org.title_el,
                        "organization_title_en": org.title_en,
                        })
            res_list.append(out_dict)
        return res_list
