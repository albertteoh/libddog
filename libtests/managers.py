import re
import subprocess
from datetime import datetime
from pathlib import Path

from libddog.command_line.dashboards import DashboardManagerCli
from libddog.crud import DashboardManager
from libddog.dashboards import Dashboard


class GitHelper:
    def get_current_branch(self) -> str:
        code, output = subprocess.getstatusoutput("git branch --show-current")
        if code == 0:
            return output

        raise RuntimeError(
            "Failed to get git branch name with code: %r and output: %r"
            % (code, output)
        )


class QADashboardManager:
    # detect occurrences of:  %(variable)s
    rx_string_template = re.compile("%\\([a-zA-Z0-9_]+\\)s")

    def __init__(self) -> None:
        proj_root = Path(__file__).parent.parent
        testdata_dir = proj_root.joinpath("testdata").absolute()
        self.cli = DashboardManagerCli(proj_path=str(testdata_dir))

        self.mgr = DashboardManager()
        self.mgr.load_credentials_from_environment()

        self.git = GitHelper()

    def load_definition_by_title(self, title: str) -> Dashboard:
        dashboards = self.cli.load_definitions()
        for dashboard in dashboards:
            if dashboard.title == title:
                return dashboard

        raise RuntimeError("Failed to get dashboard with title: %s" % title)

    def assign_id_to_dashboard(self, dashboard: Dashboard) -> str:
        all_dashboards = self.mgr.list()

        existing_id: str = ""
        for dash in all_dashboards:
            if dash["title"] == dashboard.title:
                existing_id = dash["id"]
                return existing_id

        # TODO: else create a new dash so we can use that id
        raise NotImplementedError

    def stamp_dashboard(self, dashboard: Dashboard) -> None:
        dt = datetime.now()
        branch = self.git.get_current_branch()

        dashboard.desc = dashboard.desc % {
            "branch": branch,
            "test_run_time": dt.ctime(),
        }

    def update_live_dashboard(self, dashboard: Dashboard, id: str) -> None:
        if self.rx_string_template.search(dashboard.desc):
            raise RuntimeError(
                "Dashboard desc contains unpopulated template: %s" % dashboard.desc
            )

        self.mgr.update(dashboard, id)
