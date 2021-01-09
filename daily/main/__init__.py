from flask import Blueprint

bp = Blueprint('main', __name__)

# Bottom to avoid circular dependencies
from daily.main import views
