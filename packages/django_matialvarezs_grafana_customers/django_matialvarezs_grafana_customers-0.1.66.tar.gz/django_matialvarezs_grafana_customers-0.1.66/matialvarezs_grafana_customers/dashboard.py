import json
from . import base_dashboard,api
def create_dashboard(title_dashboard,panels):
    dashboard = base_dashboard.get_dashboard()
    dashboard['title'] = title_dashboard
    dashboard['panels'] = panels
    #base['panels'] = panels
    # for panel in panels:
    #     dashboard['panels'].append(panel)
    print("DASHBOARD COMPLETO:   ",dashboard)
    api.create_dashboard(dashboard)
    #return base

def update_dashboard():
    pass