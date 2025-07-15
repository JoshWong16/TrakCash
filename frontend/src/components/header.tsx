import React from 'react';
import Link from 'next/link';
import { cn } from '@/lib/utils';

export function Header() {
  return (
    <header className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800">
      <div className="container mx-auto px-4 py-4 flex justify-between items-center">
        <div className="flex items-center">
          <Link href="/" className="text-2xl font-bold text-blue-600 dark:text-blue-400">
            TrakCash
          </Link>
        </div>
        <nav className="hidden md:flex space-x-6">
          {/* Placeholder for menu items */}
          <Link href="/" className="text-gray-600 hover:text-blue-600 dark:text-gray-300 dark:hover:text-blue-400">
            Dashboard
          </Link>
          <Link href="#" className="text-gray-600 hover:text-blue-600 dark:text-gray-300 dark:hover:text-blue-400">
            Expenses
          </Link>
          <Link href="#" className="text-gray-600 hover:text-blue-600 dark:text-gray-300 dark:hover:text-blue-400">
            Categories
          </Link>
          <Link href="#" className="text-gray-600 hover:text-blue-600 dark:text-gray-300 dark:hover:text-blue-400">
            Settings
          </Link>
        </nav>
        <div className="md:hidden">
          {/* Mobile menu button placeholder */}
          <button className="text-gray-600 hover:text-blue-600 dark:text-gray-300 dark:hover:text-blue-400">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
      </div>
    </header>
  );
}
