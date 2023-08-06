""" Tiny wrapper for gitlab REST API """

import json
import urllib.parse

import requests
import ui

import tsrc

GITLAB_API_VERSION = "v4"


class GitLabError(tsrc.Error):
    pass


class GitLabAPIError(GitLabError):
    def __init__(self, url, status_code, message):
        super().__init__(message)
        self.url = url
        self.status_code = status_code
        self.message = message

    def __str__(self):
        if self.message:
            return "%s - %s" % (self.status_code, self.message)
        else:
            return "Bad status code: %s" % self.status_code


class TooManyUsers(GitLabError):
    pass


def handle_errors(response, stream=False):
    if stream:
        _handle_stream_errors(response)
    else:
        _handle_json_errors(response)


def _handle_json_errors(response):
    # Make sure we always have a dict containing some
    # kind of error:
    json_details = dict()
    try:
        json_details = response.json()
    except ValueError:
        json_details["error"] = ("Expecting json result, got %s" % response.text)

    status_code = response.status_code
    url = response.url
    if 400 <= status_code < 500:
        for key in ["error", "message"]:
            if key in json_details:
                raise GitLabAPIError(url, status_code, json_details[key])
        raise GitLabAPIError(url, status_code, json.dumps(json_details, indent=2))
    if status_code >= 500:
        raise GitLabAPIError(url, status_code, response.text)


def _handle_stream_errors(response):
    if response.status_code >= 400:
        raise GitLabAPIError(response.url, response.status_code, "")


def extract_next_page_number(response):
    header = response.headers['x-next-page']
    if header:
        return int(header)
    else:
        return None


class GitLabHelper():
    def __init__(self, gitlab_url, token):
        self.gitlab_api_url = gitlab_url + "/api/" + GITLAB_API_VERSION
        self.token = token

    def make_request(self, verb, url, *, data=None, params=None, stream=False):
        response = self.get_response(verb, url, data=data, params=params, stream=stream)
        handle_errors(response, stream=stream)
        if stream:
            return response
        else:
            return response.json()

    def make_paginated_get_request(self, url, *, params=None):
        results = list()
        params = params.copy()
        next_page = 1
        while next_page:
            params["page"] = next_page
            response = self.get_response("GET", url, params=params)
            handle_errors(response)
            results.extend(response.json())
            next_page = extract_next_page_number(response)
        return results

    def get_response(self, verb, url, *, data=None, params=None, stream=False):
        full_url = self.gitlab_api_url + url
        response = requests.request(verb, full_url,
                                    headers={"PRIVATE-TOKEN": self.token},
                                    data=data, params=params, stream=stream)
        return response

    def get_project_id(self, project_name):
        encoded_project_name = urllib.parse.quote(project_name, safe="")
        url = "/projects/%s" % encoded_project_name
        try:
            res = self.make_request("GET", url)
            return res["id"]
        except GitLabAPIError as e:
            if e.status_code == 404:
                raise GitLabAPIError(url, 404, "Project not found: %s" % project_name) from None
            else:
                raise

    def get_default_branch(self, project_id):
        url = "projects/%s" % project_id
        project_desc = self.make_request("GET", url)
        return project_desc["default_branch"]

    def find_opened_merge_request(self, project_id, source_branch):
        url = "/projects/%s/merge_requests" % project_id
        params = {
            "state": "opened",
            "per_page": "100"  # Maximum number of items allowed in pagination
        }
        previous_mrs = self.make_paginated_get_request(url, params=params)
        for mr in previous_mrs:
            if mr["source_branch"] == source_branch:
                return mr
        return None

    def create_merge_request(self, project_id, source_branch, *, title,
                             target_branch="master"):
        ui.info_2("Creating merge request", ui.ellipsis, end="")
        url = "/projects/%i/merge_requests" % project_id
        data = {
            "source_branch": source_branch,
            "target_branch": target_branch,
            "title": title,
            "project_id": project_id,
        }
        result = self.make_request("POST", url, data=data)
        ui.info("done", ui.check)
        return result

    def update_merge_request(self, merge_request, **kwargs):
        project_id = merge_request["target_project_id"]
        merge_request_iid = merge_request["iid"]
        url = "/projects/%s/merge_requests/%s" % (project_id, merge_request_iid)
        return self.make_request("PUT", url, data=kwargs)

    def accept_merge_request(self, merge_request):
        project_id = merge_request["project_id"]
        merge_request_iid = merge_request["iid"]
        ui.info_2("Merging when build succeeds", ui.ellipsis, end="")
        url = "/projects/%s/merge_requests/%s/merge" % (project_id, merge_request_iid)
        data = {
            "merge_when_pipeline_succeeds": True,
        }
        self.make_request("PUT", url, data=data)
        ui.info("done", ui.check)

    def get_active_users(self):
        response = self.get_response("GET", "/users", params={"active": "true", "per_page": 100})
        total = int(response.headers["X-TOTAL"])
        if total > 100:
            raise TooManyUsers()
        else:
            return response.json()

    def get_group_members(self, group, query=None):
        return self.make_request("GET", "/groups/%s/members" % group,
                                 params={"query": query})

    def get_project_members(self, project_id, query=None):
        return self.make_request("GET", "/projects/%s/members" % project_id,
                                 params={"query": query})
