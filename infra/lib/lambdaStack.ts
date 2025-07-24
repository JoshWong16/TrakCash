import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as lambdaEventSources from 'aws-cdk-lib/aws-lambda-event-sources';
import { Construct } from 'constructs';

export interface LambdaStackProps extends cdk.StackProps {
  transactionBucket: s3.Bucket;
  transactionQueue: sqs.Queue;
  transactionsTable: dynamodb.Table;
  categoriesTable: dynamodb.Table;
}

export class LambdaStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: LambdaStackProps) {
    super(scope, id, props);

    const lambdaExecutionRole = new iam.Role(this, 'LambdaExecutionRole', {
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      managedPolicies: [
          iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole'),
      ],
      inlinePolicies: {
        BedrockPolicy: new iam.PolicyDocument({
          statements: [
            new iam.PolicyStatement({
              actions: ['bedrock:InvokeModel'],
              resources: ['*'],
            }),
          ],
        })
      },
    });

    // Create Lambda function to process and categorize transactions
    const categorizeLambda = new lambda.Function(this, 'CategorizeLambda', {
      functionName: 'CategorizeLambda',
      runtime: lambda.Runtime.PYTHON_3_12,
      code: lambda.Code.fromAsset('./../categorizeLambda'),
      handler: 'categorizeLambdaHandler.handler',
      timeout: cdk.Duration.seconds(300),
      memorySize: 1024,
      environment: {
        TRANSACTIONS_TABLE: props.transactionsTable.tableName,
        CATEGORIES_TABLE: props.categoriesTable.tableName,
        TRANSACTION_BUCKET: props.transactionBucket.bucketName,
        BEDROCK_MODEL_ID: 'anthropic.claude-3-sonnet-20240229-v1:0',
      },
      role: lambdaExecutionRole,
    });

    props.transactionBucket.grantRead(categorizeLambda);
    props.transactionsTable.grantReadWriteData(categorizeLambda);
    props.categoriesTable.grantReadData(categorizeLambda);

    categorizeLambda.addEventSource(new lambdaEventSources.SqsEventSource(props.transactionQueue, {
      batchSize: 10, // Process up to 10 messages at once
    }));

    new cdk.CfnOutput(this, 'CategorizeLambdaName', {
      value: categorizeLambda.functionName,
      description: 'The name of the Lambda function for categorizing transactions',
    });

    new cdk.CfnOutput(this, 'CategorizeLambdaArn', {
      value: categorizeLambda.functionArn,
      description: 'The ARN of the Lambda function for categorizing transactions',
    });
  }
}
