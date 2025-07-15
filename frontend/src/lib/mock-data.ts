export interface ExpenseCategory {
  id: string;
  name: string;
  amount: number;
  percentage: number;
  color: string;
}

export const expenseCategories: ExpenseCategory[] = [
  {
    id: "housing",
    name: "Housing",
    amount: 1200,
    percentage: 30,
    color: "#4f46e5" // Indigo
  },
  {
    id: "food",
    name: "Food & Dining",
    amount: 800,
    percentage: 20,
    color: "#0ea5e9" // Sky blue
  },
  {
    id: "transportation",
    name: "Transportation",
    amount: 600,
    percentage: 15,
    color: "#10b981" // Emerald
  },
  {
    id: "entertainment",
    name: "Entertainment",
    amount: 400,
    percentage: 10,
    color: "#f59e0b" // Amber
  },
  {
    id: "utilities",
    name: "Utilities",
    amount: 300,
    percentage: 7.5,
    color: "#ef4444" // Red
  },
  {
    id: "other",
    name: "Other/Miscellaneous",
    amount: 700,
    percentage: 17.5,
    color: "#8b5cf6" // Violet
  }
];

export const totalMonthlyExpenses = expenseCategories.reduce(
  (total, category) => total + category.amount,
  0
);
