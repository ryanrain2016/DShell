from channels.routing import route,include
from . import consumers

routing = [
    include('shell.routings.routing'),
]
