import pprint
import sqlalchemy

import ckan.new_authz as new_authz
import ckan.model as model
import ckan.logic.auth as auth
import ckan.lib.dictization.model_dictize as model_dictize

import ckan.plugins as p

import ckan.logic.auth.create as create_auth

from ckan.common import _


import ckan.plugins.toolkit as toolkit


_check_access = toolkit.check_access
_or_ = sqlalchemy.or_


def group_list_authz(context, data_dict):
    '''Return the list of groups that the user is authorized to edit.

    :param available_only: remove the existing groups in the package
      (optional, default: ``False``)
    :type available_only: boolean

    :param am_member: if True return only the groups the logged-in user is a
      member of, otherwise return all groups that the user is authorized to
      edit (for example, sysadmin users are authorized to edit all grouimport ckan.lib.dictization.model_dictize as model_dictizeps)
      (optional, default: False)
    :type am-member: boolean

    :returns: list of dictized groups that the user is authorized to edit
    :rtype: list of dicts

    '''
    model = context['model']
    user = context['user']
    available_only = data_dict.get('available_only', False)
    am_member = data_dict.get('am_member', False)
    
    
    _check_access('group_list_authz',context, data_dict)
    
    sysadmin = new_authz.is_sysadmin(user)
    
    roles = new_authz.get_roles_with_permission('manage_group')
    if not roles:
        return []
    user_id = new_authz.get_user_id_for_username(user, allow_none=True)
    if not user_id:
        return []
    
    if not sysadmin or am_member:
        q = model.Session.query(model.Member) \
            .filter(model.Member.table_name == 'user') \
            .filter(model.Member.capacity.in_(roles)) \
            .filter(model.Member.table_id == user_id)
        group_ids = []
        for row in q.all():
            group_ids.append(row.group_id)

        if not group_ids:
            return []
    
    q = model.Session.query(model.Group) \
        .filter(model.Group.is_organization == False) \
        .filter(model.Group.state == 'active')
    
    if not sysadmin or am_member:
        q = q.filter(_or_(model.Group.id.in_(group_ids), model.Group.is_organization == False))

    groups = q.all()

    if available_only:
        package = context.get('package')
        if package:
            groups = set(groups) - set(package.get_groups())

    group_list = model_dictize.group_list_dictize(groups, context)
    return group_list


def member_create(context, data_dict):
    
    group = p.toolkit.get_action('group_show')(context,
            {
                'id': data_dict.get('id'),
            })
    
    if group.get('is_organization'):
        return create_auth.member_create(context, data_dict)
    else:
        user = context.get('user')
        # Looking for any organizations user, has at least editor rights. If none exists 
        # he cannot edit a thematic group
        organizations = p.toolkit.get_action('organization_list_for_user')(context,
                        {
                            'permission': 'update_dataset'
                        })
        if not organizations:
            return {'success': False,
                    'msg': _('User %s not authorized to edit any thematic group')}
        else:
            return {'success': True}    
        
        
def member_delete(context, data_dict):
    return member_create(context, data_dict)
    
    

    
