export const currencies = [
  { code: 'INR', symbol: '\u20B9', name: 'Indian Rupee' },
  { code: 'USD', symbol: '$', name: 'US Dollar' },
  { code: 'EUR', symbol: '\u20AC', name: 'Euro' },
  { code: 'GBP', symbol: '\u00A3', name: 'British Pound' },
  { code: 'JPY', symbol: '\u00A5', name: 'Japanese Yen' },
  { code: 'AUD', symbol: 'A$', name: 'Australian Dollar' },
  { code: 'CAD', symbol: 'C$', name: 'Canadian Dollar' },
  { code: 'CHF', symbol: 'Fr', name: 'Swiss Franc' },
  { code: 'CNY', symbol: '\u00A5', name: 'Chinese Yuan' },
  { code: 'SGD', symbol: 'S$', name: 'Singapore Dollar' },
  { code: 'AED', symbol: '\u062F.\u0625', name: 'UAE Dirham' },
  { code: 'BRL', symbol: 'R$', name: 'Brazilian Real' },
  { code: 'KRW', symbol: '\u20A9', name: 'South Korean Won' },
  { code: 'MXN', symbol: 'Mex$', name: 'Mexican Peso' },
  { code: 'ZAR', symbol: 'R', name: 'South African Rand' },
];

export const getCurrencySymbol = (code) => {
  const currency = currencies.find((c) => c.code === code);
  return currency ? currency.symbol : code;
};

export const formatCurrency = (amount, currencyCode = 'INR') => {
  const symbol = getCurrencySymbol(currencyCode);
  const absAmount = Math.abs(amount);
  const formatted = absAmount.toLocaleString('en-IN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
  return amount < 0 ? `-${symbol}${formatted}` : `${symbol}${formatted}`;
};

export const expenseCategories = [
  'Food & Dining',
  'Transport',
  'Utilities',
  'Entertainment',
  'Shopping',
  'Healthcare',
  'Education',
  'Rent & Housing',
  'Insurance',
  'Groceries',
  'Travel',
  'Subscriptions',
  'Personal Care',
  'Gifts & Donations',
  'Other',
];

export const paymentRoutes = [
  'Cash',
  'Credit Card',
  'Debit Card',
  'UPI',
  'Net Banking',
  'Digital Wallet',
  'Cheque',
  'Other',
];

// Simple keyword-based category suggestion
export const suggestCategory = (memo) => {
  const lower = memo.toLowerCase();
  const rules = [
    { keywords: ['food', 'restaurant', 'dinner', 'lunch', 'breakfast', 'cafe', 'coffee', 'latte', 'pizza', 'burger', 'starbucks', 'zomato', 'swiggy', 'mcdonalds', 'kfc', 'bakery', 'snack'], category: 'Food & Dining' },
    { keywords: ['uber', 'ola', 'cab', 'taxi', 'metro', 'bus', 'train', 'fuel', 'petrol', 'diesel', 'parking', 'toll', 'flight', 'auto'], category: 'Transport' },
    { keywords: ['electric', 'electricity', 'water', 'gas', 'internet', 'wifi', 'phone', 'mobile', 'recharge', 'bill'], category: 'Utilities' },
    { keywords: ['movie', 'netflix', 'spotify', 'game', 'concert', 'theatre', 'entertainment', 'youtube', 'disney', 'amazon prime'], category: 'Entertainment' },
    { keywords: ['amazon', 'flipkart', 'shopping', 'clothes', 'shoes', 'electronics', 'gadget', 'mall'], category: 'Shopping' },
    { keywords: ['doctor', 'hospital', 'medicine', 'pharmacy', 'medical', 'health', 'clinic', 'dental', 'eye'], category: 'Healthcare' },
    { keywords: ['school', 'college', 'course', 'book', 'tuition', 'class', 'exam', 'study', 'udemy', 'coursera'], category: 'Education' },
    { keywords: ['rent', 'housing', 'apartment', 'flat', 'maintenance', 'society'], category: 'Rent & Housing' },
    { keywords: ['insurance', 'lic', 'policy', 'premium'], category: 'Insurance' },
    { keywords: ['grocery', 'groceries', 'supermarket', 'whole foods', 'vegetables', 'fruits', 'milk', 'dmart', 'bigbasket'], category: 'Groceries' },
    { keywords: ['travel', 'hotel', 'booking', 'trip', 'vacation', 'holiday', 'airbnb'], category: 'Travel' },
    { keywords: ['subscription', 'membership', 'plan', 'annual', 'monthly'], category: 'Subscriptions' },
    { keywords: ['salon', 'haircut', 'spa', 'beauty', 'cosmetics', 'grooming'], category: 'Personal Care' },
    { keywords: ['gift', 'donation', 'charity', 'present', 'birthday'], category: 'Gifts & Donations' },
  ];

  for (const rule of rules) {
    if (rule.keywords.some((kw) => lower.includes(kw))) {
      return rule.category;
    }
  }
  return null;
};
