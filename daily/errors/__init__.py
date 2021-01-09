from flask import Blueprint

bp = Blueprint('errors',__name__)

# Bottom to avoid circular dependencies
from daily.errors import handlers
