import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';

export class LambdaStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const categorizeLambda = new cdk.aws_lambda.Function(this, 'CategorizeLambda', {
      functionName: 'CategorizeLambda',
      runtime: cdk.aws_lambda.Runtime.PYTHON_3_12,
      code: cdk.aws_lambda.Code.fromAsset('./../categorizeLambda'),
      handler: 'categorizeLambdaHandler.handler',
      environment: {
        MY_ENV_VAR: 'Hello, World!',
      },
    });
  }
}
