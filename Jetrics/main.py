
# Local Modules
import Jetrics.downstream as d

def main():
    """
    Main function to start the program

    """
    client = d.get_jira_client()

    print(d.average_code_review_time(client))

if __name__ == '__main__':
    main()