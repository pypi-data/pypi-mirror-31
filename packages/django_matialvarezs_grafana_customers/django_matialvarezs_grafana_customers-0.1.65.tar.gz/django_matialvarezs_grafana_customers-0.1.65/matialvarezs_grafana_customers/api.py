from . import settings
from matialvarezs_request_handler import utils as matialvarezs_request_handler_utils
from . import models
import json


def create_organisation(business_id, name):
    data = {
        "name": name
    }
    res = matialvarezs_request_handler_utils.send_post_and_get_response(settings.GRAFANA_API_BASE_URL + 'orgs',
                                                                        data=data, headers=settings.GRAFANA_API_HEADERS,
                                                                        convert_data_to_json=True)
    # res = requests.post(settings.GRAFANA_API_BASE_URL + 'orgs',data=data, headers=settings.GRAFANA_API_HEADERS)
    # res.
    print("res antes de guardar organisation en grafana", res.content)
    if res:
        print("res al guardar organisation en grafana", res.content)
        res_data = json.loads(res.content.decode('utf-8'))
        organisation_id = res_data['orgId']
        customer_org_grafana = models.OrganisationGrafana(object_project=business_id, organisation_id=organisation_id)
        customer_org_grafana.save()


def update_organisation(business_id, name):
    pass


def create_user():
    pass


def create_dashboard(json_dashboard):
    # data = {
    #     "dashboard": {
    #         "id": None,
    #         "uid": None,
    #         "title": "Production Overview",
    #         "tags": [json_dashboard],
    #         "timezone": "browser",
    #         "schemaVersion": 16,
    #         "version": 0
    #     },
    #     "folderId": 0,
    #     "overwrite": False
    # }
    data = {
        "dashboard": json_dashboard,
        "folderId": 0,
        "overwrite": False
    }

    res = matialvarezs_request_handler_utils.send_post_and_get_response(settings.GRAFANA_API_BASE_URL + 'dashboards/db',
                                                                        data=data, headers=settings.GRAFANA_API_HEADERS,
                                                                        convert_data_to_json=True)
    if res:
        res_data = json.loads(res.content.decode('utf-8'))
        id_dashboard = res_data['uid']
        print("RES AL GUARDAR DASHBOARD", json.loads(res.content.decode('utf-8')))
    print("ERROR AL GUARDAR DASHBOARD", json.loads(res.content.decode('utf-8')))
