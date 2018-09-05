from jira import JIRA
import pystache
from datetime import datetime

options = { 'server': 'http://shaipjira.local.tmvse.com' }
jira = JIRA(options)
project = jira.project('10002')
epics = jira.search_issues(
    'project = SHAIP AND issuetype = Epic AND resolution = Unresolved ORDER BY id ASC',
    expand="renderedFields")

template_epics = []
for epic in epics:
    epic_children = jira.search_issues('"Epic Link" = {}'.format(epic.key))

    children = []
    for child in epic_children:
        children.append({
            'key': child.key,
            'summary': child.fields.summary,
            'icon_type': child.fields.issuetype.iconUrl,
            'permalink': child.permalink(),
            'closed': child.fields.resolution is not None
        })

    template_epics.append({
        'key': epic.key,
        'summary': epic.fields.summary,
        'description': epic.renderedFields.description,
        'children': children,
        'permalink': epic.permalink()
    })

renderer = pystache.Renderer()
context = {
    'project_name': project.name,
    'epics': template_epics,
    'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
}

with open('output.html', 'w') as file:
    file.write(renderer.render_path("templates/requirements.html.mustache", context))
