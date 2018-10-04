#!/usr/bin/env python

from lib.gitlab import GitlabIssuesAPI

class GitlabIssue(GitlabIssuesAPI):

    def run(self, url, project, issue_iid, token, verify_ssl):
        self.url = url or self.url
        self.verify_ssl = verify_ssl or self.verify_ssl
        self.token = token or self.token

        return True, self.get(self.url, project, issue_iid)
