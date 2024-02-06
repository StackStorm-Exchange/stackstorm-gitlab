#!/usr/bin/env python

from st2common.runners.base_action import Action
import gitlab


class GitlabIssueCreate(Action):

    # Retrieve config information
    def __init__(self, config):
        super(GitlabIssueCreate, self).__init__(config=config)
        self.url = self.config.get('url')
        self.token = self.config.get('token')

    def run(self, project_id, title, description, assignee_ids, labels, epic_id, due_date, weight, token):

        # Use user token if given
        token = token or self.token

        # Initiate GitLab instance
        gl = gitlab.Gitlab(self.url, token)

        # Get the project with id == project_id
        project = gl.projects.get(project_id)

        # Create new issue
        issue = project.issues.create({ 'title': title, 'description': description, 'assignee_ids': assignee_ids,
                                        'labels': labels, 'epic_id': epic_id, 'due_date': due_date, 'weight': weight})

        return (True, issue)
