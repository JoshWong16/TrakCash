import * as cdk from 'aws-cdk-lib';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as s3n from 'aws-cdk-lib/aws-s3-notifications';
import { Construct } from 'constructs';

export interface SQSStackProps extends cdk.StackProps {
  transactionBucket: s3.Bucket;
}

export class SQSStack extends cdk.Stack {
  public readonly transactionQueue: sqs.Queue;

  constructor(scope: Construct, id: string, props: SQSStackProps) {
    super(scope, id, props);

    // Create SQS queue for S3 notifications
    this.transactionQueue = new sqs.Queue(this, 'TransactionQueue', {
      queueName: 'trakcash-transaction-queue',
      visibilityTimeout: cdk.Duration.seconds(300), // 5 minutes, matching Lambda timeout
    });

    // Configure S3 to send notifications to SQS
    props.transactionBucket.addEventNotification(
      s3.EventType.OBJECT_CREATED,
      new s3n.SqsDestination(this.transactionQueue)
    );

    // Output the queue URL and ARN
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
