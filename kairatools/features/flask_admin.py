from flask import url_for
from flask_admin import Admin
from kairatools.views.base_view import KairaToolsBaseModelView
from kairatools.views.admin_view import KairaToolsAdminIndexView
from flask_admin import helpers as admin_helpers
from kairatools.models.kairatools_models import User, Role

def setup_admin(app, security):
    # Setup admin panel
    admin = Admin(app,
                  name='kaira-tools',
                  base_template='my_master.html',
                  template_mode='bootstrap3',
                  index_view=KairaToolsAdminIndexView())

    # Add admin views
    admin.add_view(KairaToolsBaseModelView(Role))
    admin.add_view(KairaToolsBaseModelView(User))

    # define a context processor for merging flask-admin's template context into the
    # flask-security views.
    def security_context_processor():
        return dict(
            admin_base_template=admin.base_template,
            admin_view=admin.index_view,
            h=admin_helpers,
            get_url=url_for
        )

    security.context_processor(security_context_processor)

    return admin