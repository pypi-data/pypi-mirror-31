# ZenPy
A rewrite of GlintPy.

ZenPy is created to fill in the missing pieces of AWS CloudFormation services.

ZenPy automates:
* AWS Lambda function(Python or NodeJS) packaging and deployment
* MySQL to Dynamo DB data mapping
* ElasticSearch indexing(under development)
* RDS instance creation(under development)

To install ZenPy: **pip install zen-py**




To run ZenPy, type **zen** in your command line interface, and it will ask for the path to ***package.json*** file to load the configurations.

**zen --file ~/path.../package.json**

# Sample template for package.json

```
{
    "version": "0.0.1",
    "author": "Chen Cheng",
    "email": "nick@carpal.com",
    "description": "An AWS service automation toolbox",
    "region": "your aws account region",
    "pythonVirtualenv": "your python virtualenv path",
    "accessKey": "your aws access key",
    "secretKey": "your aws secret key",
    "elasticIP": false,
    "awsClientID": "",
    "lambdas": [{
        "skip": true,
        "name": "lambda function name",
        "handler": "lambda function handler name",
        "alias": "lambda function alias",
        "runtime": "python version",
        "stages": ["stage A", "stage B", ...],
        "environmentVariables": {},
        "iamRole": "iam role to execute the lambda function",
        "timeout": 3,
        "path": "lambda function directory",
        "packages": ["dependancy package 1", "dependancy package 2"],
        "files": ["dependancy file 1", "dependancy file 2"],
	"vendor": [{"rootDirectory": "...",
		    "modules": ["moduel_folder_name"]}],
        "events": [{
            "type": "CloudWatchEvent",
            "name": "test_event",
            "schedule": "rate(1 minute)",
            "state": "ENABLED",
            "iamRole": "IAM_ROLE_ARN"
        },{
            "type": "SNS",
            "name": "test_sns_trigger",
            "state": "ENABLED",
            "stage": "dev",
            "topicARN": "Topic ARN",
            "iamRole": "IAM_ROLE_ARN"
        },{
            "type": "SNS",
            "name": "test_sns_trigger",
            "state": "ENABLED",
            "stage": "staging",
            "topicARN": "Topic ARN",
            "iamRole": "IAM_ROLE_ARN"
        }]
    }],
    "vpcs":[{
        "skip": true,
        "defaultVpc": true,
        "cidrBlock": "default CIDR block",
        "instanceTenancy": "default",
        "subnets":[{"cidr":"subnet 1", "availabilityZone":"region name", "nat": false}],
        "securityGroups": [{"name": "security group name", "description": "description", "ingressRules":[{"IpProtocol": "tcp",
                                                                                                            "FromPort": 3306,
                                                                                                            "ToPort": 3306,
                                                                                                            "IpRanges": [{"CidrIp": "0.0.0.0/0"}]}]}]}],
    "customPolicies":[{"name": "custome policy name",
                       "document": "document in JSON format"}],
    "iamRoles":[{"roleName": "IAM role name", 
                 "assumedRole": "assumed role in JSON format",
                 "inlinePolicy":"inline policy in JSON format",
                 "policies": ["AWS predefined policy 1", "AWS predefined policy 2", "..."]}
                ],
    "rds":[{
        "skip": false,
        "username": "DB username",
        "password": "DB password",
        "engine": "mysql",
        "engineVersion": "RDS instance engine version",
        "identifier": "RDS instance identifier",
        "name": "RDS instance name",
        "allocatedStorage": 5,
        "storageType": "gp2",
        "availabilityZone": "RDS instance region",
        "multipleAZ": true,
        "publiclyAccessible": true,
        "autoMinorVersionUpgrade": true,
        "backupWindow": "17:38-18:08",
        "instanceClass": "RDS instance type",
        "securityGroups": ["RDS instance security group name"],
        "storageEncrypted": false,
        "subnetGroup": "subnet group name",
        "subnetGroupSubnets": ["subnet group subnet 1", "subnet group subnet 2"],
        "port": 3306,
        "characterSetName": "utf8mb4",
        "backupRetentionPeriod": 7,
        "licenseModel": "general-public-license",
        "endpoint": "",
        "requireReplication": true,
        "databases": [{
            "name": "DB name",
            "tablePath": "sql files for table schemas",
            "dataPath": "sql files for data dumps"
        }]
    }],
    "cloudWatch":{
        "alarms": [{
            "skip": true,
            "name": "alarm name",
            "description": "",
            "enabled": true,
            "okAction": "",
            "alarmAction": ["alarm action name"],
            "insufficientDataAction": "",
            "dimensions":[{"name": "", "value": ""}],
            "metricName": "mertic name",
            "namespace": "namespace",
            "statistic": "Average",
            "period": 60,
            "unit": "Count",
            "evaluationPeriods": 1,
            "threshold": 1,
            "comparisonOperator": "GreaterThanOrEqualToThreshold"
        }]
    },
    "sns":[{"name": "SNS topic name", "skip": false}],
    "dynamoDBs":[{"name": "Dynamo DB type",
				  "skip": false,
                  "attributeDefinitions": [{"name": "attribute name", "type":"S"}],
			  	  "keySchema": [{"name": "key name", "type":"HASH"}],
			  	  "provisionedThroughput": {"readCapacityUnits": 5, "writeCapacityUnits": 5}}],
    "sqs":[{"name":"queue name",
           "attributes":{"delaySeconds": 0}}],
    "elasticSearch":[{"domainName": "elastic domain name",
                      "skip":false,
                      "createIndices": true,
                      "dbServer": "source database connection string",
                      "dbUser": "source database username",
                      "dbPassword": "source database password",
                      "db": "source database name",
                      "view": "assets_view",
                      "config": {"instanceType": "elasticsearch instance type",
                                 "instanceCount": 1,
                                 "dedicatedMasterEnabled": false,
                                 "zoneAwarenessEnabled": false},
                      "version": "5.3",
                      "ebsOptions":{"enabled": true,
                                    "volumeType": "standard",
                                    "volumeSize": 10,
                                    "iops": 2},
                      "accessPolicies": "access policy in JSON format",
                      "automatedSnapshotStartHour": 0}]
}
```
