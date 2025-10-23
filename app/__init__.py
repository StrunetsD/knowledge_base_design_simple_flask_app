from flask import Flask

from routers.organizations_routers import organizations_bp
from routers.teachers_routers import teachers_bp
from routers.courses_routers import courses_bp
from routers.training_requests_routers import training_requests_bp

def create_app():
    app = Flask(__name__)
 
    app.register_blueprint(organizations_bp, url_prefix='/api/organizations')
    app.register_blueprint(courses_bp, url_prefix='/api/courses')
    app.register_blueprint(teachers_bp, url_prefix='/api/teachers')
    app.register_blueprint(training_requests_bp, url_prefix='/api/training-requests')

    return app