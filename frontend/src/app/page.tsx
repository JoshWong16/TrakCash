import React from 'react';
import { expenseCategories, totalMonthlyExpenses } from '@/lib/mock-data';
import { ExpenseCategoryCard } from '@/components/expense-category-card';

export default function Home() {
  return (
    <div className="py-6">
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">
          Monthly Expenses
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Total: ${totalMonthlyExpenses.toLocaleString()} • July 2025
        </p>
      </div>

      {/* Expense Categories Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {expenseCategories.map((category) => (
          <ExpenseCategoryCard 
            key={category.id} 
            category={category} 
          />
        ))}
      </div>

      {/* Summary Section */}
      <div className="mt-10 bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
          Spending Summary
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Your highest spending category is <span className="font-medium text-gray-900 dark:text-gray-100">Housing</span> at ${expenseCategories[0].amount.toLocaleString()}, 
          which represents {expenseCategories[0].percentage}% of your total monthly expenses.
        </p>
      </div>
    </div>
  );
}
