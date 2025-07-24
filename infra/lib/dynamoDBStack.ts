import * as cdk from 'aws-cdk-lib';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import { Construct } from 'constructs';

export interface DynamoDBStackProps extends cdk.StackProps {
}

export class DynamoDBStack extends cdk.Stack {
  public readonly transactionsTable: dynamodb.Table;
  public readonly categoriesTable: dynamodb.Table;

  constructor(scope: Construct, id: string, props?: DynamoDBStackProps) {
    super(scope, id, props);

    this.transactionsTable = new dynamodb.Table(this, 'TransactionsTable', {
      tableName: 'trakcash-transactions',
      partitionKey: {
        name: 'userId',
        type: dynamodb.AttributeType.STRING,
      },
      sortKey: {
        name: 'transactionDateId',
        type: dynamodb.AttributeType.STRING,
      },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY
    });

    this.transactionsTable.addGlobalSecondaryIndex({
      indexName: 'StatusIndex',
      partitionKey: { name: 'nonTerminalStatus', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'transactionDateId', type: dynamodb.AttributeType.STRING },
    });

    this.transactionsTable.addGlobalSecondaryIndex({
      indexName: 'PendingValidationIndex',
      partitionKey: { name: 'pendingValidation', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'transactionDateId', type: dynamodb.AttributeType.STRING },
    });

    this.categoriesTable = new dynamodb.Table(this, 'CategoriesTable', {
      tableName: 'trakcash-categories',
      partitionKey: { name: 'userId', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY, // For development only
    });

    new cdk.CfnOutput(this, 'TransactionsTableName', {
      value: this.transactionsTable.tableName,
      description: 'The name of the DynamoDB table for transactions',
    });

    new cdk.CfnOutput(this, 'CategoriesTableName', {
      value: this.categoriesTable.tableName,
      description: 'The name of the DynamoDB table for user categories',
    });
  }
}
