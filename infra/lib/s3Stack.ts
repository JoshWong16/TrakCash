import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as s3n from 'aws-cdk-lib/aws-s3-notifications';
import { Construct } from 'constructs';

export interface S3StackProps extends cdk.StackProps {
}

export class S3Stack extends cdk.Stack {
  public readonly transactionBucket: s3.Bucket;
  public readonly transactionQueue: sqs.Queue;
  public readonly transactionDLQ: sqs.Queue;


  constructor(scope: Construct, id: string, props: S3StackProps) {
    super(scope, id, props);

    this.transactionBucket = new s3.Bucket(this, 'TransactionBucket', {
      bucketName: 'trakcash-transaction-uploads',
      removalPolicy: cdk.RemovalPolicy.DESTROY, // For development only
      autoDeleteObjects: true, // For development only
    });

    new cdk.CfnOutput(this, 'TransactionBucketName', {
      value: this.transactionBucket.bucketName,
      description: 'The name of the S3 bucket for transaction uploads',
    });

    // Create Dead Letter Queue first
    this.transactionDLQ = new sqs.Queue(this, 'TransactionDLQ', {
      queueName: 'trakcash-transaction-dlq',
      retentionPeriod: cdk.Duration.days(14), // Keep failed messages for 14 days
    });

    // Create SQS queue for S3 notifications with DLQ configuration
    this.transactionQueue = new sqs.Queue(this, 'TransactionQueue', {
      queueName: 'trakcash-transaction-queue',
      visibilityTimeout: cdk.Duration.seconds(300), // 5 minutes, matching Lambda timeout
      deadLetterQueue: {
        queue: this.transactionDLQ,
        maxReceiveCount: 1,
      },
    });

    this.transactionBucket.addEventNotification(
      s3.EventType.OBJECT_CREATED_PUT, new s3n.SqsDestination(this.transactionQueue)
    );


    new cdk.CfnOutput(this, 'TransactionQueueUrl', {
      value: this.transactionQueue.queueUrl,
      description: 'The URL of the SQS queue for transaction notifications',
    });

    new cdk.CfnOutput(this, 'TransactionQueueArn', {
      value: this.transactionQueue.queueArn,
      description: 'The ARN of the SQS queue for transaction notifications',
    });

    new cdk.CfnOutput(this, 'TransactionDLQUrl', {
      value: this.transactionDLQ.queueUrl,
      description: 'The URL of the Dead Letter Queue for failed transaction messages',
    });

    new cdk.CfnOutput(this, 'TransactionDLQArn', {
      value: this.transactionDLQ.queueArn,
      description: 'The ARN of the Dead Letter Queue for failed transaction messages',
    });
  }
}
