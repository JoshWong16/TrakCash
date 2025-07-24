#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { LambdaStack } from './lambdaStack';
import { DynamoDBStack } from './dynamoDBStack';
import { S3Stack } from './s3Stack';

const app = new cdk.App();

// Create stacks
const s3Stack = new S3Stack(app, 'S3Stack', {});
const dynamoDBStack = new DynamoDBStack(app, 'DynamoDBStack', {});
const lambdaStack = new LambdaStack(app, 'LambdaStack', {
  transactionBucket: s3Stack.transactionBucket,
  transactionQueue: s3Stack.transactionQueue,
  transactionsTable: dynamoDBStack.transactionsTable,
  categoriesTable: dynamoDBStack.categoriesTable,
});
