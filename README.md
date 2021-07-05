# IDN2Syslog

Send audit logs from SailPoint IdentityNow to Syslog.

The script stores the file locally or can store timestamp in AWS Systems Manager Parameter Store.

This script is based on https://github.com/Flo451/IDN2QRadar and has been adapted to:

- Use v3 search API instead of Beta
- Propose to store the timestamp locally using Shelves
- Use environment variables for configuration instead of INI file

> WARNING: At this moment, the script must be scheduled to be executed periodically.

## Configuration

The configuration is done by environment variables.
Configuration can also be done through a `.env` file.

| Env variable name  | Description                                                                                    |
| ------------------ | ---------------------------------------------------------------------------------------------- |
| SYSLOG_HOST        | Hostname of the Syslog server                                                                  |
| SYSLOG_SOCKET_TYPE | Connection type. Can be `UDP` or `TCP`. `UDP` by default                                       |
| CACHE_PROVIDER     | Either `ShelveStore` for local cache (default) or `AWS` for AWS System Manager Parameter store |
| CACHE_PATH         | Path for local cache                                                                           |
| IDN_CLIENT_ID      | Client ID to connect to IdentityNow                                                            |
| IDN_CLIENT_SECRET  | Client Secret to connect to IdentityNow                                                        |
| IDN_TENANT         | Tenant name of IdentityNow                                                                     |
| AWS_ACCESS_KEY     | AWS access key for System Manager Parameter store                                              |
| AWS_SECRET_KEY     | AWS secret key for System Manager Parameter store                                              |
| AWS_REGION         | AWS region for System Manager Parameter store                                                  |

## High Level workflow

- Periodically query the IDN Search API to retrieve the latest event logs
- Forward the events to Syslog messages\*
- Store last timestamp

## Testing

Testing has been performed using syslog-ng.
A Docker compose file is present in the repository to run a syslog-ng.

## Considerations

- The search API allows querying events with filters e.g. `created:>2021-02-28` but log events in the IDN API can become available with a slight delay. We have to build a mechanism that queries the latest events allowing for them to be delayed: `created:>{query_checkpoint_time} AND created:<{current_time - query_search_delay}`
- As seen above we need to record a checkpoint time that contains the last event that was retrieved from the API so we have a starting point for the next execution run. We store this value in AWS System Manager Parameter store or locally to keep state between executions.
- The event messages are encoded in JSON and transported via Syslog.
- UDP syslog messages should not exceed 1,024 bytes but SailPoint Logs are often >1,024 bytes. TCP message can be used instead

## Hosting

### AWS

Overview of the AWS services use in this solution

- [Amazon Elastic Container Service (ECS)](https://aws.amazon.com/ecs), a highly scalable, high performance container management service that supports Docker containers
- [AWS Fargate](https://aws.amazon.com/fargate) is a serverless compute engine for containers that works with ECS. Fargate removes the need to provision and manage servers, lets you specify resources per application, and improves security through application isolation by design.
- [AWS Systems Manager Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html) provides secure, hierarchical storage for configuration data management and secrets management as well as the ability to store values as plain text or encrypted data.
- Amazon Elastic Compute Cloud (Amazon EC2) is a web service that provides secure, resizable compute capacity in the cloud.

### Azure

TBD
