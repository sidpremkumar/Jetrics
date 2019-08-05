# Built In Modules
import os
from datetime import datetime, timedelta

# 3rd Party Modules
import jira

# Global Variables
create_date = "createdDate > '2019/08/1'"
projects_in = "Project in ('FACTORY')"
standard_jql = f"{create_date} AND {projects_in}"

def get_jira_client(verify=True):
    """
    Function to create JIRA client.

    :param Bool verify: Bool to indicate if we should enable verification (Default = True)
    :returns: JIRA client
    :rtype: jira.client.JIRA
    """
    jira_info = {
        'options': {
            'server': os.environ['JIRA_URL'],
            'verify': verify
        },
        'basic_auth': (os.environ['JIRA_USER'], os.environ['JIRA_PW'])
    }

    client = jira.client.JIRA(**jira_info)
    return client


def current_work_in_progress(client):
    """
    Function to get Current Work in Progress.


    :param jira.client.JIRA client: JIRA Client
    :return: Number of issues in progress
    :rtype: Int
    """
    jql = f"{standard_jql} AND status = 'In Progress'"
    return len(client.search_issues(jql))


def average_code_review_time(client):
    """
    Function to get the average time tickets spend under code review


    :param jira.client.JIRA client: JIRA Client
    :return: Average number of days spent in code review
    :rtype: Int
    """
    # expand = 'changelog'
    jql = f"{standard_jql} AND type in (Bug, Story)"
    issues = client.search_issues(jql, expand='changelog')
    start_time = None
    end_time = None
    differences = []
    for issue in issues:
        changelog = issue.changelog
        for history in changelog.histories:
            for item in history.items:
                if item.field == 'status':
                    if item.toString == 'Code Review' and not end_time:
                        start_time = datetime.strptime(history.created[:-5], '%Y-%m-%dT%H:%M:%S.%f')
                    elif item.fromString == 'Code Review' and start_time:
                        end_time = datetime.strptime(history.created[:-5], '%Y-%m-%dT%H:%M:%S.%f')
        if start_time and end_time:
            differences.append(end_time - start_time)

    sum = timedelta(days=0)
    for difference in differences:
        sum += difference
    average_days = (sum.total_seconds()/60/60/24)/len(difference)
    return average_days
