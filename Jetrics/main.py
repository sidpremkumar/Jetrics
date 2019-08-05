# Built In Modules
import logging

# Local Modules
import Jetrics.downstream as d

# Global Variables
log = logging.getLogger('Jetrics.main')

def main():
    """
    Main function to start the program

    """
    client = d.get_jira_client()

    print(d.passing_qe(client))

if __name__ == '__main__':
    main()