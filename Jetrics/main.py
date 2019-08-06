# Built In Modules
import logging

# Local Modules
import Jetrics.downstream as d
import Jetrics.upstream as u

# Global Variables
log = logging.getLogger('Jetrics.main')

def main():
    """
    Main function to start the program

    """
    # Get our JIRA client
    log.info('Getting JIRA client...')
    client = d.get_jira_client()

    # Build our downstream values
    log.info('Generating Jetrics...')
    ret = d.deferred_or_declined(client)
    deferred, declined = ret[0], ret[1]
    ret = d.cycle_time(client)
    bug_cycle_time, story_cycle_time = ret[0], ret[1]
    values = {
        'Current Work In Progress': d.current_work_in_progress(client),
        'Average Code Review Time': d.average_code_review_time(client),
        'Average Code Review to QE': d.average_code_review_to_qe(client),
        'Time to Deploy': d.time_to_deploy(client),
        'Bug Cycle Time': bug_cycle_time,
        'Story Cycle Time': story_cycle_time,
        'QE Gaps': d.qe_gaps(client),
        'Bugs Caught': d.bugs_caught(client),
        'Bug Ratio': d.bug_ratio(client),
        'Work Outside of Quarterly Planning': d.work_outside_of_quarterly_planning(client, 'Y19-Q4'),
        'Passing QE': d.passing_qe(client),
        'Deferred Issues': deferred,
        'Declined Issues': declined,
    }

    # Sync these values upstream
    log.info('Syncing upstream...')
    u.sync_with_upstream(values)


if __name__ == '__main__':
    main()