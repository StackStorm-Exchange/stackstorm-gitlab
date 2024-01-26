#!/usr/bin/env python

from st2common.runners.base_action import Action
import gitlab


class GitlabEpicCreate(Action):

    # Retrieve config information
    def __init__(self, config):
        super(GitlabEpicCreate, self).__init__(config=config)
        self.url = self.config.get('url')
        self.token = self.config.get('token')

    def run(self, group_id, title, labels, description, start_date, due_date, token):

        # Use user token if given
        token = token or self.token

        # Initiate GitLab instance
        gl = gitlab.Gitlab(self.url, token)

        # Get the group with id == group_id
        group = gl.groups.get(group_id)

        # If start/due date is given, tell gitlab it is fixed
        due_date_is_fixed = True if due_date else False
        start_date_is_fixed = True if start_date else False

        # Create new epic
        epic = group.epics.create({'title': title, 'description': description, 'labels': labels, 'start_date_fixed': start_date, 'start_date_is_fixed': start_date_is_fixed, 'due_date_fixed': due_date, 'due_date_is_fixed': due_date_is_fixed})
        return (True, epic)
