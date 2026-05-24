from rest_framework import permissions


class IsOwnerAndDraftOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):

        # GET boleh untuk semua user login
        if request.method in permissions.SAFE_METHODS:
            return True

        # PUT dan DELETE hanya untuk owner
        # dan status harus DRAFT
        return obj.reporter == request.user and obj.status == 'DRAFT'