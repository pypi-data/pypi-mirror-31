import requests
from urllib.parse import urlparse
from requests.adapters import HTTPAdapter
from veracodestats.api_hmac import generate_veracode_hmac_header, VeracodeHMACError


class VeracodeAPIError(Exception):
    """Raised when something goes wrong with talking to the Veracode API"""
    pass


class VeracodeAPI:
    def __init__(self, proxies=None):
        self.baseurl = "https://analysiscenter.veracode.com/api"
        self.proxies = proxies

    def _get_request(self, url, params=None):
        try:
            session = requests.Session()
            session.mount(self.baseurl, HTTPAdapter(max_retries=3))
            request = requests.Request("GET", url, params=params)
            prepared_request = request.prepare()
            try:
                prepared_request.headers["Authorization"] = generate_veracode_hmac_header(urlparse(url).hostname,
                                                                                          prepared_request.path_url, "GET")
            except VeracodeHMACError:
                raise VeracodeAPIError("Could not generate API HMAC header")
            r = session.send(prepared_request, proxies=self.proxies)
            if 200 >= r.status_code <= 299:
                if r.content is None:
                    raise VeracodeAPIError("HTTP response body is empty")
                else:
                    return r.content
            else:
                raise VeracodeAPIError("HTTP error {}".format(r.status_code))
        except requests.exceptions.RequestException as e:
            raise VeracodeAPIError(e)

    def get_app_list(self):
        """Returns all application profiles."""
        return self._get_request(self.baseurl + "/5.0/getapplist.do")

    def get_app_builds(self, report_changed_since):
        """Returns all builds."""
        return self._get_request(self.baseurl + "/4.0/getappbuilds.do", params={"only_latest": False,
                                                                                "include_in_progress": True,
                                                                                "report_changed_since": report_changed_since})

    def get_app_info(self, app_id):
        """Returns application profile info for a given app ID."""
        return self._get_request(self.baseurl + "/5.0/getappinfo.do", params={"app_id": app_id})

    def get_sandbox_list(self, app_id):
        """Returns a list of sandboxes for a given app ID"""
        return self._get_request(self.baseurl + "/5.0/getsandboxlist.do", params={"app_id": app_id})

    def get_build_list(self, app_id, sandbox_id=None):
        """Returns all builds for a given app ID."""
        params = {"app_id": app_id}
        if sandbox_id:
            params["sandbox_id"] = sandbox_id
        return self._get_request(self.baseurl + "/5.0/getbuildlist.do", params=params)
    
    def get_build_info(self, app_id, build_id, sandbox_id=None):
        """Returns build info for a given build ID."""
        params = {"app_id": app_id, "build_id": build_id}
        if sandbox_id:
            params["sandbox_id"] = sandbox_id
        return self._get_request(self.baseurl + "/5.0/getbuildinfo.do", params=params)

    def get_detailed_report(self, build_id):
        """Returns a detailed report for a given build ID."""
        return self._get_request(self.baseurl + "/5.0/detailedreport.do", params={"build_id": build_id})

    def get_policy_list(self):
        """Returns all policies."""
        return self._get_request(self.baseurl + "/5.0/getpolicylist.do")

    def get_user_list(self):
        """Returns all user accounts."""
        return self._get_request(self.baseurl + "/5.0/getuserlist.do")

    def get_user_info(self, username):
        """Returns user info for a given username."""
        return self._get_request(self.baseurl + "/5.0/getuserinfo.do", params={"username": username})
