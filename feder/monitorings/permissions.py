from rest_framework import permissions


class MultiCaseTagManagementPerm(permissions.DjangoModelPermissions):
    permission_name = "monitorings.change_case"

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        monitoring = view.get_object()
        return user.has_perm(self.permission_name, monitoring) if monitoring else False
