#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { LambdaStack } from './lambdaStack';
import { DynamoDBStack } from './dynamoDBStack';
import { SQSStack } from './sqsStack';
import { S3Stack } from './s3Stack';
import { BedrockStack } from './bedrockStack';

const app = new cdk.App();

// Create stacks
const s3Stack = new S3Stack(app, 'S3Stack', {});
const sqsStack = new SQSStack(app, 'SQSStack', {
  transactionBucket: s3Stack.transactionBucket,
});
const dynamoDBStack = new DynamoDBStack(app, 'DynamoDBStack', {});
const bedrockStack = new BedrockStack(app, 'BedrockStack', {});
const lambdaStack = new LambdaStack(app, 'LambdaStack', {
  transactionBucket: s3Stack.transactionBucket,
  transactionQueue: sqsStack.transactionQueue,
  transactionsTable: dynamoDBStack.transactionsTable,
  categoriesTable: dynamoDBStack.categoriesTable,
  bedrockRole: bedrockStack.bedrockRole,
});
