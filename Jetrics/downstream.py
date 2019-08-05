# Built In Modules
import os
from datetime import datetime, timedelta
import logging

# 3rd Party Modules
import jira

# Global Variables
create_date = "createdDate > '2019/06/1'"
projects_in = "Project in ('FACTORY')"
standard_jql = f"{create_date} AND {projects_in}"
log = logging.getLogger(__name__)

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
    jql = f"{standard_jql} AND type in (Bug, Story)"
    issues = client.search_issues(jql, expand='changelog')
    if len(issues) < 1:
        log.warning(f'No issues could be found for JQL: {jql}')
        return
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
            if start_time < end_time and end_time > start_time:
                differences.append(end_time - start_time)

    if len(differences) < 1:
        log.warning(f'No issues have transitioned in/out of Code Review')
        return -1

    sum = timedelta(days=0)
    for difference in differences:
        sum += difference
    average_days = (sum.total_seconds()/60/60/24)/len(differences)
    return average_days


def average_code_review_to_qe(client):
    """
    Function to get the average time tickets spend from code review -> Merged (or Testing)


    :param jira.client.JIRA client: JIRA Client
    :return: Average number of days spent in code review
    :rtype: Int
    """
    jql = f"{standard_jql} AND type in (Bug, Story)"
    issues = client.search_issues(jql, expand='changelog')
    if len(issues) < 1:
        log.warning(f'No issues could be found for JQL: {jql}')
        return
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
                    elif item.toString == 'Testing' or item.toString == 'Merged' and start_time:
                        end_time = datetime.strptime(history.created[:-5], '%Y-%m-%dT%H:%M:%S.%f')
        if start_time and end_time:
            if start_time < end_time and end_time > start_time:
                differences.append(end_time - start_time)

    if len(differences) < 1:
        log.warning(f'No issues have transitioned from Code Review -> Merged/Testing')
        return -1
    sum = timedelta(days=0)
    for difference in differences:
        sum += difference
    average_days = (sum.total_seconds()/60/60/24)/len(differences)
    return average_days


def time_to_deploy(client):
    """
    Function to get the average number of days between release-pending and closed

    :param jira.client.JIRA client: JIRA Client
    :return: Average number of days spent in code review
    :rtype: Int
    """
    jql = f"{standard_jql} AND type in (Bug, Story)"
    issues = client.search_issues(jql, expand='changelog')
    if len(issues) < 1:
        log.warning(f'No issues could be found for JQL: {jql}')
        return
    start_time = None
    end_time = None
    differences = []
    for issue in issues:
        changelog = issue.changelog
        for history in changelog.histories:
            for item in history.items:
                if item.field == 'status':
                    if (item.toString == 'Release Pending' or item.toString == 'Release_Pending') and not end_time:
                        start_time = datetime.strptime(history.created[:-5], '%Y-%m-%dT%H:%M:%S.%f')
                    elif item.toString == 'Closed' and start_time:
                        end_time = datetime.strptime(history.created[:-5], '%Y-%m-%dT%H:%M:%S.%f')
        if start_time and end_time:
            if start_time < end_time and end_time > start_time:
                differences.append(end_time - start_time)

    if len(differences) < 1:
        log.warning(f'No issues have transitioned from Release Pending -> Closed')
        return -1
    sum = timedelta(days=0)
    for difference in differences:
        sum += difference
    average_days = (sum.total_seconds()/60/60/24)/len(differences)
    return average_days


def cycle_time(client):
    """
    Function to get the average time from In Progress -> Closed/Resolved


    :param jira.client.JIRA client: JIRA Client
    :return: Average number of days spent in code review for (Bugs, Stories)
    :rtype: Tuple
    """
    # Lets start with Bugs
    jql = f"{standard_jql} AND type in (Bug)"
    issues = client.search_issues(jql, expand='changelog')
    if len(issues) < 1:
        log.warning(f'No Bugs could be found for JQL: {jql}')
    start_time = None
    end_time = None
    differences = []
    for issue in issues:
        changelog = issue.changelog
        for history in changelog.histories:
            for item in history.items:
                if item.field == 'status':
                    if item.toString == 'In Progress' and not end_time:
                        start_time = datetime.strptime(history.created[:-5], '%Y-%m-%dT%H:%M:%S.%f')
                    elif issue.fields.project.key in ['FACTORY', 'BST', 'COMPOSE', 'NOS']:
                        if item.toString == 'Resolved' and start_time:
                            end_time = datetime.strptime(history.created[:-5], '%Y-%m-%dT%H:%M:%S.%f')
                    else:
                        if item.toString == 'Closed' and start_time:
                            end_time = datetime.strptime(history.created[:-5], '%Y-%m-%dT%H:%M:%S.%f')
        if start_time and end_time:
            if start_time < end_time and end_time > start_time:
                differences.append(end_time - start_time)

    if len(differences) < 1:
        log.warning(f'No Bugs have transitioned from In-Progress -> Closed/Resolved')
        bug_average_days = -1
    else:
        sum = timedelta(days=0)
        for difference in differences:
            sum += difference
        bug_average_days = (sum.total_seconds() / 60 / 60 / 24) / len(differences)

    # No lets do the same thing for Stories
    jql = f"{standard_jql} AND type in (Story)"
    issues = client.search_issues(jql, expand='changelog')
    if len(issues) < 1:
        log.warning(f'No issues could be found for JQL: {jql}')
    start_time = None
    end_time = None
    differences = []
    for issue in issues:
        changelog = issue.changelog
        for history in changelog.histories:
            for item in history.items:
                if item.field == 'status':
                    if item.toString == 'In Progress' and not end_time:
                        start_time = datetime.strptime(history.created[:-5], '%Y-%m-%dT%H:%M:%S.%f')
                    elif issue.fields.project.key in ['FACTORY', 'BST', 'COMPOSE', 'NOS']:
                        if item.toString == 'Resolved' and start_time:
                            end_time = datetime.strptime(history.created[:-5], '%Y-%m-%dT%H:%M:%S.%f')
                    else:
                        if item.toString == 'Closed' and start_time:
                            end_time = datetime.strptime(history.created[:-5], '%Y-%m-%dT%H:%M:%S.%f')
        if start_time and end_time:
            if start_time < end_time and end_time > start_time:
                differences.append(end_time - start_time)

    if len(differences) < 1:
        log.warning(f'No Stories have transitioned from In-Progress -> Closed/Resolved')
        story_average_days = -1
    else:
        sum = timedelta(days=0)
        for difference in differences:
            sum += difference
        story_average_days = (sum.total_seconds() / 60 / 60 / 24) / len(differences)

    return bug_average_days, story_average_days


def re_testing_qe_gaps(client):
    """
    Function to calculate QE Gaps.


    :param jira.client.JIRA client: JIRA Client
    :return: Number of issues that fall under 'QE Gaps'
    :rtype: Int
    """
    jql = f"{standard_jql} AND category = 'Product Pipeline' and status changed from Verified to Testing"
    return len(client.search_issues(jql))


def bugs_caught(client):
    """
    Function to count the number of issues that have transitions from Testing -> In Progress


    :param jira.client.JIRA client: JIRA Client
    :return: Number of issues
    :rtype: Int
    """
    jql = f"{standard_jql} AND status changed from Testing to 'In Progress'"
    return len(client.search_issues(jql))


def bug_ratio(client):
    """
    Function to capture the ratio of Bugs:Everything Else


    :param jira.client.JIRA client: JIRA Client
    :return: Ratio of Bugs:Everything Else
    :rtype: Int
    """
    jql = f"{standard_jql} AND type = Bug and resolution is not EMPTY"
    number_of_bugs = len(client.search_issues(jql))
    jql = f"{standard_jql} AND type != Bug and resolution is not EMPTY"
    number_of_issues = len(client.search_issues(jql))
    if number_of_issues == 0:
        log.warning(f'No issues could be found for jql: {jql}')
        return -1
    return number_of_bugs/number_of_issues


def work_outside_of_quarterly_planning(client, quarter_label):
    """
    Function to track how many unplanned issues came up during the year

    :param jira.client.JIRA client: JIRA Client
    :param String quarter_label: Quarter Label we should search for
    :return: Number of issues that fit this criteria
    :rtype: Int
    """
    jql = f"{standard_jql} AND type not in (Bug, Ticket) and " \
        f"(issueFunction in linkedIssuesOf('type = epic and " \
        f"labels = {quarter_label}', 'is epic of''))"
    return len(client.search_issues(jql))


def passing_qe(client):
    """
    Function to get average time between
    * Merged -> Verified/In Progress (QE)
    * Testing -> In Progress/Release Pending (None QE)

    :param jira.client.JIRA client: JIRA Client
    :return: Average number of days a issue stays in said critera
    :rtype: Int
    """
    jql = f"{standard_jql} AND type in (Bug, Story)"
    issues = client.search_issues(jql, expand='changelog')
    if len(issues) < 1:
        log.warning(f'No issues could be found for JQL: {jql}')
        return
    start_time = None
    end_time = None
    differences = []
    for issue in issues:
        changelog = issue.changelog
        for history in changelog.histories:
            for item in history.items:
                if item.field == 'status':
                    if issue.fields.project.key in ['FACTORY', 'BST', 'COMPOSE', 'NOS']: #TODO: THIS IS WITHOUT QE
                        # If this is QE
                        if item.toString == 'Merged' and not end_time:
                            start_time = datetime.strptime(history.created[:-5], '%Y-%m-%dT%H:%M:%S.%f')
                        elif (item.toString == 'Verified' or item.toString == 'In Progress') and start_time:
                            end_time = datetime.strptime(history.created[:-5], '%Y-%m-%dT%H:%M:%S.%f')
                    else:
                        # If this is not QE
                        if item.toString == 'Testing' and not end_time:
                            start_time = datetime.strptime(history.created[:-5], '%Y-%m-%dT%H:%M:%S.%f')
                        elif (item.toString == 'In Progress' or item.toString == 'Release Pending') and start_time:
                            end_time = datetime.strptime(history.created[:-5], '%Y-%m-%dT%H:%M:%S.%f')
                if start_time and end_time:
                    # Always check this as this can happen multiple times in an issue
                    if start_time < end_time and end_time > start_time:
                        differences.append(end_time - start_time)
                        start_time = None
                        end_time = None

    if len(differences) < 1:
        log.warning(f'No issues could be found for function passing_qe')
        return -1
    else:
        sum = timedelta(days=0)
        for difference in differences:
            sum += difference
        return (sum.total_seconds() / 60 / 60 / 24) / len(differences)


def deferred_or_declined(client):
    """
    Function to get the number of deferred/declined issues

    :param jira.client.JIRA client: JIRA Client
    :return: Number of deferred issues, Number of declined issues
    :rtype: Tuple
    """
    jql = f"{standard_jql} AND resolution = Deferred"
    deferred_issues = len(client.search_issues(jql))
    if deferred_issues == 0:
        log.warning(f'No deferred issues could be found for JQL: {jql}')
    jql = f"{standard_jql} AND resolution = 'Won’t Fix'"
    declined_issues = len(client.search_issues(jql))
    if declined_issues == 0:
        log.warning(f'No declined issues could be found for JQL: {jql}')
    return deferred_issues, declined_issues
