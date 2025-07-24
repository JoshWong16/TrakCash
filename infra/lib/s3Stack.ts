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

    // Create SQS queue for S3 notifications
    this.transactionQueue = new sqs.Queue(this, 'TransactionQueue', {
      queueName: 'trakcash-transaction-queue',
      visibilityTimeout: cdk.Duration.seconds(300), // 5 minutes, matching Lambda timeout
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
  }
}
