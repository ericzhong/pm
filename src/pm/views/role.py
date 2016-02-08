from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from ..models import Role, Project_Group_Role, Project_User_Role, User, Permission
from ..forms import RoleForm


_model = Role
_form = RoleForm


def get_role_user(project_id):
    return [(i.role, i.user) for i in Project_User_Role.objects.filter(project_id=project_id)]


def get_role_group(project_id):
    return [(i.role, i.group) for i in Project_Group_Role.objects.filter(project_id=project_id)]


def get_role_user_of_groups(project_id):
    return list(set([(i[0], n) for i in get_role_group(project_id) for n in i[1].user_set.all()]))


def get_role_users(project_id):
    role_user = list(set(get_role_user(project_id) + get_role_user_of_groups(project_id)))

    import collections
    tmp = collections.defaultdict(list)
    for item in role_user:
        tmp[item[0]].append(item[1])

    return [(key, [u for u in value]) for key, value in tmp.iteritems()]


def check_user_in_groups(project_id, user_id):
    return True if user_id in [i[1].id for i in get_role_user_of_groups(project_id)] else False


def get_group_roles_id(project_id, group_id):
    return list(Project_Group_Role.objects.filter(project_id=project_id, group_id=group_id)
                .values_list('role', flat=True).distinct())


def get_user_roles_id(project_id, user_id):
    return list(Project_User_Role.objects.filter(project_id=project_id, user_id=user_id)
                .values_list('role', flat=True).distinct())


def get_user_groups_roles_id(project_id, user_id):
    user = User.objects.get(pk=user_id)
    return list(Project_Group_Role.objects.filter(project_id=project_id, group__in=list(user.groups.all()))
                .values_list('role', flat=True).distinct())


def get_project_role_of_user(user_id):
    return [(i.project, i.role) for i in Project_User_Role.objects.filter(user_id=user_id)]


def get_project_role_of_group(group_id):
    return [(i.project, i.role) for i in Project_Group_Role.objects.filter(group_id=group_id)]


def get_project_role_of_groups(user):
    return list(set([(i.project, i.role)
                     for i in Project_Group_Role.objects.filter(group__in=list(user.groups.all()))]))


def get_user_permissions(user):
    roles_id = list(Project_User_Role.objects.filter(user_id=user.id).values_list('role', flat=True).distinct())
    return list(set([item.permission for item in Role.permissions.through.objects.filter(role_id__in=roles_id)]))


def get_project_user_permissions(user, project):
    roles_id = list(Project_User_Role.objects.filter(user=user, project=project)
                    .values_list('role', flat=True).distinct())
    return list(set([item.permission for item in Role.permissions.through.objects.filter(role_id__in=roles_id)]))


def get_group_permissions(user):
    roles_id = list(Project_Group_Role.objects.filter(group__in=list(user.groups.all()))
                    .values_list('role', flat=True).distinct())
    return list(set([item.permission for item in Role.permissions.through.objects.filter(role_id__in=roles_id)]))


def get_project_group_permissions(user, project):
    roles_id = list(Project_Group_Role.objects.filter(group__in=list(user.groups.all()), project=project)
                    .values_list('role', flat=True).distinct())
    return list(set([item.permission for item in Role.permissions.through.objects.filter(role_id__in=roles_id)]))


class List(ListView):
    model = _model
    template_name = '_admin/roles.html'
    context_object_name = 'roles'


class Create(CreateView):
    model = _model
    form_class = _form
    template_name = '_admin/create_role.html'

    def get_success_url(self):
        if 'continue' in self.request.POST:
            return reverse_lazy('role_add')
        else:
            return reverse_lazy('role_list')


class Update(UpdateView):
    model = _model
    form_class = _form
    template_name = '_admin/edit_role.html'
    success_url = reverse_lazy('role_list')


class Delete(DeleteView):
    model = _model
    success_url = reverse_lazy('role_list')

    def get(self, request, *args, **kwargs):
        return redirect('role_list')
