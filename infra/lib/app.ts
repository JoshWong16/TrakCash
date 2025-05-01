#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { LambdaStack } from './lambdaStack';

const app = new cdk.App();
new LambdaStack(app, 'LambdaStack', {});