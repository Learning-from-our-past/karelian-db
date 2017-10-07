from flask import url_for, request, redirect, flash
from flask_admin import AdminIndexView, expose
from flask_security import current_user


class KairaToolsAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            flash('Please log in first', 'error')
            next_url = request.url
            login_url = '%s?next=%s' % (url_for('security.login'), next_url)
            return redirect(login_url)

        if current_user.has_role('superuser'):
            return super(KairaToolsAdminIndexView, self).index()
        else:
            return redirect(url_for("index"))
