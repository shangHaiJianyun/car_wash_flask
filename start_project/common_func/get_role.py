from start_project import Role


def get_user_role(name):
    user_role = Role.query.filter_by(name=name).first()
    return user_role
