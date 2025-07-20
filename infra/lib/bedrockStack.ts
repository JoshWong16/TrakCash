import * as cdk from 'aws-cdk-lib';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Construct } from 'constructs';

export interface BedrockStackProps extends cdk.StackProps {
}

export class BedrockStack extends cdk.Stack {
  public readonly bedrockRole: iam.Role;

  constructor(scope: Construct, id: string, props?: BedrockStackProps) {
    super(scope, id, props);

    // Create IAM role for Bedrock access
    this.bedrockRole = new iam.Role(this, 'BedrockAccessRole', {
      roleName: 'trakcash-bedrock-access-role',
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
    });

    // Add policy to allow Bedrock model invocation
    this.bedrockRole.addToPolicy(
      new iam.PolicyStatement({
        actions: ['bedrock:InvokeModel'],
        resources: ['*'], // In production, scope this down to specific models
      })
    );

    // Output the role ARN
    new cdk.CfnOutput(this, 'BedrockRoleArn', {
      value: this.bedrockRole.roleArn,
      description: 'The ARN of the IAM role for Bedrock access',
    });
  }
}
