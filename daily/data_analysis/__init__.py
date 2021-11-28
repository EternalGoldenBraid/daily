from flask import Blueprint

bp = Blueprint('data_analysis', __name__)

# Bottom to avoid circular dependencies
from daily.data_analysis import views
