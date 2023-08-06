# Bitbucket Cloud Build Status Reporter For Jenkins

## Update the Bitbucket  build statuses for commits from within a Jenkins job.

### Benefits
* Block pull requests from being merged if there is a failed build
* Link to the relevant build logs from within Bitbucket UI
* More flexible than the existing Jenkins plugin - if you clone multiple repos within your jobs

### Environment variables
* This CLI uses [Jenkins Environment Vars](https://wiki.jenkins.io/display/JENKINS/Building+a+software+project#Buildingasoftwareproject-belowJenkinsSetEnvironmentVariables)
* Should be run from the root of the checked out repo
* Requires username and password with `repository` scope permission to access the required [API method](https://developer.atlassian.com/bitbucket/api/2/reference/resource/repositories/%7Busername%7D/%7Brepo_slug%7D/commit/%7Bnode%7D/statuses/build)

### Reference
```
bb-report --help
usage: bb-report [-h] -o ORG -r REPO -s {INPROGRESS,SUCCESSFUL,FAILED} -u
                 USERNAME -p PASSWORD

Bitbucket Cloud Build Status Notifier

optional arguments:
  -h, --help            show this help message and exit
  -o ORG, --org ORG     Bitbucket org
  -r REPO, --repo REPO  Repository name
  -s {INPROGRESS,SUCCESSFUL,FAILED}, --state {INPROGRESS,SUCCESSFUL,FAILED}
                        State of the build
  -u USERNAME, --username USERNAME
                        Username for bitbucket
  -p PASSWORD, --password PASSWORD
                        Password for bitbucket
```
