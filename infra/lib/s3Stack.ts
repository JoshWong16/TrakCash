import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { Construct } from 'constructs';

export interface S3StackProps extends cdk.StackProps {
}

export class S3Stack extends cdk.Stack {
  public readonly transactionBucket: s3.Bucket;

  constructor(scope: Construct, id: string, props?: S3StackProps) {
    super(scope, id, props);

    // Create S3 bucket for transaction CSV uploads
    this.transactionBucket = new s3.Bucket(this, 'TransactionBucket', {
      bucketName: 'trakcash-transaction-uploads',
      removalPolicy: cdk.RemovalPolicy.DESTROY, // For development only
      autoDeleteObjects: true, // For development only
    });

    // Output the bucket name
    new cdk.CfnOutput(this, 'TransactionBucketName', {
      value: this.transactionBucket.bucketName,
      description: 'The name of the S3 bucket for transaction uploads',
    });
  }
}
