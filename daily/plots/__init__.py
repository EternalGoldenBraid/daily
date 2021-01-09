from flask import Blueprint

#bp = Blueprint('plots', __name__, template_folder='templates')
bp = Blueprint('plots', __name__)

# Bottom to avoid circular dependencies
from daily.plots import views

