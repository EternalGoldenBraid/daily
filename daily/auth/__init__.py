from flask import Blueprint

bp = Blueprint('auth', __name__)

# Bottom to avoid circular dependencies
from daily.auth import views
