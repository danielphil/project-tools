from jira import JIRA
import pystache
from datetime import datetime
import json

options = { 'server': 'http://shaipjira.local.tmvse.com' }
jira = JIRA(options)
project = jira.project('10002')
requirements = jira.search_issues(
    'project = SHAIP AND issuetype = Requirement AND resolution = Unresolved ORDER BY id ASC',
    expand="renderedFields")

template_requirements = []
for requirement in requirements:
    links = []
    for link in requirement.fields.issuelinks:
        if link.type.name != "Defines":
            continue

        link_type = None
        issue = None
        if hasattr(link, 'outwardIssue'):
            link_type = "defines"
            issue = link.outwardIssue
        else:
            link_type = "is defined by"
            issue = link.inwardIssue

        links.append({
            'key': issue.key,
            'summary': issue.fields.summary,
            'icon_type': issue.fields.issuetype.iconUrl,
            'permalink': issue.permalink(),
            'closed': issue.fields.status.name == "Done",
            'link_type': link_type
        })

    template_requirements.append({
        'key': requirement.key,
        'summary': requirement.fields.summary,
        'description': requirement.renderedFields.description,
        'links': links,
        'permalink': requirement.permalink(),
        'labels': requirement.fields.labels
    })

renderer = pystache.Renderer()
context = {
    'project_name': project.name,
    'requirements': template_requirements,
    'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
}

with open('output.html', 'w') as file:
    #print(json.dumps(context, sort_keys=True, indent=4))
    file.write(renderer.render_path("templates/requirements.html.mustache", context))
