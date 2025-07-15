import React from 'react';
import { ExpenseCategory } from '@/lib/mock-data';
import { cn } from '@/lib/utils';

interface ExpenseCategoryCardProps {
  category: ExpenseCategory;
  className?: string;
}

export function ExpenseCategoryCard({ category, className }: ExpenseCategoryCardProps) {
  return (
    <div 
      className={cn(
        "bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 border-l-4",
        className
      )}
      style={{ borderLeftColor: category.color }}
    >
      <div className="flex justify-between items-center mb-2">
        <h3 className="font-medium text-gray-900 dark:text-gray-100">{category.name}</h3>
        <span 
          className="inline-block w-3 h-3 rounded-full" 
          style={{ backgroundColor: category.color }}
        ></span>
      </div>
      <div className="flex justify-between items-baseline">
        <span className="text-2xl font-bold text-gray-900 dark:text-gray-100">
          ${category.amount.toLocaleString()}
        </span>
        <span className="text-sm text-gray-500 dark:text-gray-400">
          {category.percentage}%
        </span>
      </div>
      <div className="mt-2 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
        <div 
          className="h-2 rounded-full" 
          style={{ 
            width: `${category.percentage}%`,
            backgroundColor: category.color 
          }}
        ></div>
      </div>
    </div>
  );
}
