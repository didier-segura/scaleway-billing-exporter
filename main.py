import requests
import os
import time
import re
from datetime import datetime, timedelta
from prometheus_client import start_http_server, Gauge

# Define Gauge metrics
consumption_total = Gauge('scaleway_consumption_total', 'Total consumption for the current month')
consumption_category = Gauge('scaleway_consumption_category', 'Consumption for a specific category', ['category', 'project_id', 'project_name'])
consumption_month = Gauge('scaleway_consumption_month', 'Consumption for a specific month', ['month','project_id', 'project_name'])
consumption_project = Gauge('scaleway_consumption_project', 'Consumption for a specific project', ['project_id', 'project_name'])
consumption_total_projects = Gauge('scaleway_consumption_total_projects', 'Total consumption across all projects')

def fetch_project_name(project_id):
    url = f"https://api.scaleway.com/account/v1/projects/{project_id}"
    headers = {"X-Auth-Token": os.environ.get('SCW_SECRET_KEY'), "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    data = response.json()
    project_name = data.get('project', {}).get('name')
    return project_name

# Function to fetch consumption data for a specific category
def fetch_consumption_category(category, project_id=None):
    labels = {'category': category}  # Start with the category label
    
    if project_id:
        # Fetch project name
        project_name = fetch_project_name(project_id)
        if project_name:
            labels['project_id'] = project_id
            labels['project_name'] = project_name

    url = f"https://api.scaleway.com/billing/v2beta1/consumptions?category_name={category}"
    if project_id:
        url += f"&project_id={project_id}"
        
    headers = {"X-Auth-Token": os.environ.get('SCW_SECRET_KEY'), "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    data = response.json()
    total_consumption = sum(float(item['value']['units']) + float(item['value']['nanos']) / 1e9 for item in data.get('consumptions', []))
    
    valid_labels = {k: v for k, v in labels.items() if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', k)}
    consumption_category.labels(**valid_labels).set(total_consumption)  # Set labels using dictionary


def fetch_project_name(project_id):
    url = f"https://api.scaleway.com/account/v2/projects/{project_id}"
    headers = {"X-Auth-Token": os.environ.get('SCW_SECRET_KEY')}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        project_data = response.json()
        return project_data.get('name')
    else:
        print(f"Failed to fetch project name for project ID {project_id}. Status code: {response.status_code}")
        return None


# Function to fetch consumption data for a specific month
def fetch_consumption_month(month):
    url = f"https://api.scaleway.com/billing/v2beta1/consumptions?organization_id={os.environ.get('SCW_ORGANIZATION_ID')}&billing_period={month}"
    headers = {"X-Auth-Token": os.environ.get('SCW_SECRET_KEY'), "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    data = response.json()
    total_consumption = sum(item['value']['units'] + item['value']['nanos'] / 1e9 for item in data.get('consumptions', []))
    consumption_month.labels(month).set(total_consumption)


# Function to fetch consumption data for a specific project
def fetch_consumption_project(project_id, project_name):
    url = f"https://api.scaleway.com/billing/v2beta1/consumptions?project_id={project_id}"
    headers = {"X-Auth-Token": os.environ.get('SCW_SECRET_KEY'), "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    data = response.json()
    total_consumption = sum(float(item['value']['units']) + float(item['value']['nanos']) / 1e9 for item in data.get('consumptions', []))
    consumption_project.labels(project_id, project_name).set(total_consumption)


def fetch_all_projects():
    url = f"https://api.scaleway.com/account/v2/projects?organization_id={os.environ.get('SCW_ORGANIZATION_ID')}&page=1&page_size=10&order_by=created_at_asc"
    headers = {"X-Auth-Token": os.environ.get('SCW_SECRET_KEY')}
    response = requests.get(url, headers=headers)
    data = response.json()
    projects = data.get('projects', [])
    return projects

def fetch_consumption_categories_for_project(project_id):
    categories = ['BareMetal', 'Compute', 'Containers', 'Labs', 'Managed Databases', 'Managed Services', 'Network', 'Object Storage', 'Observability', 'Security and Identity', 'Serverless', 'Storage', 'Subscription']
    for category in categories:
        fetch_consumption_category(category, project_id)


def fetch_consumption_month_by_project(month, project_id, project_name):
    url = f"https://api.scaleway.com/billing/v2beta1/consumptions?project_id={project_id}&billing_period={month}"
    headers = {"X-Auth-Token": os.environ.get('SCW_SECRET_KEY'), "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    data = response.json()
    total_consumption = sum(float(item['value']['units']) + float(item['value']['nanos']) / 1e9 for item in data.get('consumptions', []))
    consumption_month.labels(month=month, project_id=project_id, project_name=project_name).set(total_consumption)

# Function to fetch consumption data for the last 12 months from the current month
def fetch_consumption_last_12_months(project_id, project_name):
    current_month = datetime.utcnow().strftime('%Y-%m')
    for i in range(1, 13):
        month = (datetime.utcnow() - timedelta(days=i*30)).strftime('%Y-%m')
        fetch_consumption_month_by_project(month, project_id, project_name)

# Function to fetch and compute total consumption across all projects
def fetch_total_consumption_across_projects():
    projects = fetch_all_projects()
    total_consumption = 0
    for project in projects:
        project_id = project['id']
        url = f"https://api.scaleway.com/billing/v2beta1/consumptions?project_id={project_id}"
        headers = {"X-Auth-Token": os.environ.get('SCW_SECRET_KEY'), "Content-Type": "application/json"}
        response = requests.get(url, headers=headers)
        data = response.json()
        total_consumption += sum(float(item['value']['units']) + float(item['value']['nanos']) / 1e9 for item in data.get('consumptions', []))
    consumption_total_projects.set(total_consumption)

if __name__ == '__main__':
    # Set up the HTTP server to expose the metrics on port 8000
    start_http_server(8000)

    # Fetch and set metrics every 60 seconds
    while True:
        projects = fetch_all_projects()
        for project in projects:
            project_id = project['id']
            project_name = project['name']
            fetch_consumption_categories_for_project(project_id)
            fetch_consumption_project(project_id, project_name)
            fetch_consumption_last_12_months(project_id, project_name)
            fetch_total_consumption_across_projects()
        time.sleep(180)