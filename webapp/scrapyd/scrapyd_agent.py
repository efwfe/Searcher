import json
import logging
from scrapyd.model import DaemonStatus, AddVersionResultSet, ScheduleResultSet, CancelResultSet, ProjectList, \
    VersionList, SpiderList, JobList, DeleteProjectVersionResultSet, DeleteProjectResultSet
from utils import http_utils
from html.parser import HTMLParser

logging = logging.getLogger(__name__)


class ScrapyLogsPageHTMLParser(HTMLParser):
    result = []

    def handle_data(self, data):
        if self.lasttage == "a":
            self.result.append(data)

    def clean_enter_sign(self):
        for x in self.result:
            if x.startswith("\n"):
                self.result.remove(x)


class ScrapyCommandSet(dict):
    def __init__(self, scrapyd_url, *args, **kw):
        super(ScrapyCommandSet, self).__init__(*args, **kw)
        self.itemlist = list(super(ScrapyCommandSet, self).keys())
        self.init_command_set(scrapyd_url)

    def __setitem__(self, key, value):
        self.itemlist.append(key)
        super(ScrapyCommandSet, self).__setitem__(key, value)

    def __iter__(self):
        return self.itemlist

    def keys(self):
        return self.itemlist

    def values(self):
        return [self[key] for key in self]

    def itervalues(self):
        return (self[key] for key in self)

    def init_command_set(self, scrapyd_url):
        """
        Init command set by scrapyd_url, each element is a list such
        as ["command", 'supervisored http staff' ]
        """
        if scrapyd_url[-1:] != '/':
            scrapyd_url = scrapyd_url + "/"
        self["daemonstatus"] = [scrapyd_url +
                                'daemonstatus.json', http_utils.METHOD_GET]
        self["addversion"] = [scrapyd_url +
                              "addverison.json", http_utils.METHOD_POST]
        self["schedule"] = [scrapyd_url +
                            "schedule.json", http_utils.METHOD_POST]
        self["cancel"] = [scrapyd_url + 'cancel.json', http_utils.METHOD_POST]
        self["listprojects"] = [scrapyd_url +
                                'listprojects.json', http_utils.METHOD_GET]
        self["listversions"] = [scrapyd_url +
                                'listversions.json', http_utils.METHOD_GET]
        self["listspiders"] = [scrapyd_url +
                               'listspiders.json', http_utils.METHOD_GET]
        self["listjobs"] = [scrapyd_url + 'listjobs.json', http_utils.METHOD_GET]
        self["delversion"] = [scrapyd_url +
                              'delversion.json', http_utils.METHOD_POST]
        self["delproject"] = [scrapyd_url +
                              'delproject.json', http_utils.METHOD_POST]
        self["logs"] =[scrapyd_url + "logs/", http_utils.METHOD_GET]

class ScrapydAgent:
    def __init__(self, scrapyd_url):
        self.command_set = ScrapyCommandSet(scrapyd_url)

    def get_load_status(self):
        """
        To check the load status of a service
        return : a dictionary that include json data
                example:{"status":"ok", "runnning":"0", "pendding":"0", "finished":"0", "node_name":"node_name"}
        """

        url, method = self.command_set["daemonstatus"]
        response = http_utils.request(
            url, method_type=method, return_type=http_utils.RETURN_JSON)
        return response

    def add_version(self, project_name, version, egg):
        """
        Add a version to a project, creating the project if it doesn't exist
        """
        url, method = self.command_set["addversion"]
        data = {}
        data["project"] = project_name
        data["version"] = version
        data["egg"] = egg
        response = http_utils.request(
            url, method_type=method, data=data, return_type=http_utils.RETURN_JSON)
        return response

    def schedule(self, project_name, spider_name, setting=None, job_id=None, version=None, args={}):
        """
        Schedule a spider run , return job id
        """
        url, method = self.command_set["schedule"]
        data = {}
        data["project"] = project_name
        data["spider"] = spider_name
        if setting is not None:
            data["setting"] = setting
        if job_id is not None:
            data["jobid"] = job_id
        if version is not None:
            data["_version"] = version
        for k, v in args.items():
            data[k] = v
        response = http_utils.request(
            url, method_type=method, data=data, return_type=http_utils.RETURN_JSON)
        return response

    def cancel(self, project_name, job_id):
        """
        Cancel a spider run,if the job is pending it will be removed,
        if the job is running ,it will be terminated
        """
        url, method = self.command_set["cancel"]
        data = {}
        data["project"] = project_name
        data["job"] = job_id
        response = http_utils.request(
            url, method_type=method, data=data, return_type=http_utils.RETURN_JSON)
        return json.loads(response)

    def get_project_list(self):
        """
        Get the list of projects uploaded to this scrapy server
        """
        url, method = self.command_set["listprojects"]
        response = http_utils.request(
            url, method_type=method, return_type=http_utils.RETURN_JSON)
        return response

    def get_version_list(self, project_name):
        """
        Get the list of versions avaliabel for some project
        """
        url, method = self.command_set["listversions"]
        data = {"project": project_name}
        response = http_utils.request(
            url, method_type=method, data=data, return_type=http_utils.RETURN_JSON)
        return response

    def get_spider_list(self, project_name, version=None):
        """
        Get the list of spiders avalabel in the last version of some project
        """
        url, method = self.command_set["listspdiers"]
        data = {}
        data["project"] = project_name
        if version is not None:
            data["_version"] = version
        response = http_utils.request(
            url, method_type=method, data=data, return_type=http_utils.RETURN_JSON)
        return response

    def get_job_list(self, project_name):
        """
        Get the list of pending, running and finished jobs of some project.
        """
        url, method = self.command_set["listjobs"]
        data = {"project": project_name}
        response = http_utils.request(
            url, method_type=method, data=data, return_type=http_utils.RETURN_JSON)
        return response

    def delete_project_version(self, project_name, version):
        """
        Delete a project version
        if there are no more versions avaliabel for a given project.
        the project will be delted too.
        """
        url, method = self.command_set["delversion"]
        data = {"project": project_name, "version": version}
        response = http_utils.request(
            url, method_type=method, data=data, return_type=http_utils.RETURN_JSON)
        return response

    def delete_project(self, project_name):
        """
        Delete a project and all its uploaded versions
        """
        url, method = self.command_set["delproject"]
        data = {"project": project_name}
        response = http_utils.request(
            url, method_type=method, data=data, return_type=http_utils.RETURN_JSON)
        return response


    def get_logs_urls(self, project_name, spider_name):
        """
        Get urls that scrapd logs file by project name and spider name
        """
        url, method = self.command_set["logs"]
        url = url + "/" +spider.name + "/"
        response = http_utils.request(url, method_type = method)
        html_parser = ScrapyLogsPageHTMLParser()
        html_parser.feed(response)~
        html_parser.clean_enter_sign()
        return [url + x for x in html_parser.result]
