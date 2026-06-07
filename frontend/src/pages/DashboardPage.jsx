import { useState, useEffect, useCallback } from 'react';
import { Target, Check, Trash2 } from 'lucide-react';
import api from '../utils/api';
import { formatCurrency, getCurrencySymbol } from '../utils/currencies';
import './DashboardPage.css';

const getCategoryClass = (category) => {
  const map = {
    'Food & Dining': 'food',
    Transport: 'transport',
    Utilities: 'utilities',
    Entertainment: 'entertainment',
    Shopping: 'shopping',
    Healthcare: 'healthcare',
    Education: 'education',
    'Rent & Housing': 'rent',
    Groceries: 'groceries',
    Travel: 'travel',
    Subscriptions: 'subscriptions',
  };
  return map[category] || 'other';
};

export default function DashboardPage() {
  const [stats, setStats] = useState({
    gross_expenditure: 0,
    monthly_income: 0,
    savings_target_pct: 20,
    savings_target_amount: 0,
    budget_used_pct: 0,
    category_distribution: {},
  });
  const [expenses, setExpenses] = useState([]);
  const [income, setIncome] = useState(0);
  const [savingsPct, setSavingsPct] = useState(20);
  const [currency, setCurrency] = useState('INR');
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    try {
      const [statsRes, expensesRes, profileRes] = await Promise.all([
        api.get('/api/v1/dashboard/stats'),
        api.get('/api/v1/expenses?limit=10'),
        api.get('/api/v1/profile'),
      ]);
      setStats(statsRes.data);
      setExpenses(expensesRes.data.expenses || []);
      setIncome(profileRes.data.monthly_income || 0);
      setSavingsPct(profileRes.data.savings_target || 20);
      setCurrency(profileRes.data.currency || 'INR');
    } catch (err) {
      console.error('Failed to load dashboard:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchData();
  }, [fetchData]);

  const handleIncomeUpdate = async () => {
    try {
      await api.put('/api/v1/profile', {
        monthly_income: income,
        savings_target: savingsPct,
      });
      fetchData();
    } catch (err) {
      console.error('Failed to update:', err);
    }
  };

  const handleDeleteExpense = async (id) => {
    try {
      await api.delete(`/api/v1/expenses/${id}`);
      fetchData();
    } catch (err) {
      console.error('Failed to delete:', err);
    }
  };

  const sym = getCurrencySymbol(currency);
  const savingsAmount = (income * savingsPct) / 100;
  const remaining = income - savingsAmount;
  const needsAmount = (remaining * 5) / 8;
  const wantsAmount = (remaining * 3) / 8;

  const sliderLabels = [10, 20, 30, 40, 50];

  if (loading) {
    return (
      <div className="no-data" style={{ marginTop: '3rem' }}>
        Loading dashboard...
      </div>
    );
  }

  return (
    <>
      {/* Stat Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-card-label">Gross Expenditure</div>
          <div className="stat-card-value negative">
            -{formatCurrency(Math.abs(stats.gross_expenditure), currency)}
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-card-label">Monthly Income</div>
          <div className="stat-card-value">
            {sym} {income.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-card-label">Safety Savings Target</div>
          <div className="stat-card-value">
            {sym} {savingsAmount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </div>
        </div>
        <div className="stat-card budget-card">
          <div className="budget-header">
            <div>
              <div className="stat-card-label">Budget Allocation Limit</div>
              <div className="stat-card-value" style={{ fontSize: '1.1rem' }}>
                {stats.budget_used_pct.toFixed(1)}% Used
              </div>
            </div>
            <div className="budget-percentage">{stats.budget_used_pct.toFixed(0)}%</div>
          </div>
          <div className="budget-bar">
            <div
              className="budget-bar-fill"
              style={{ width: `${Math.min(stats.budget_used_pct, 100)}%` }}
            />
          </div>
        </div>
      </div>

      {/* Financial Planner */}
      <div className="planner-section">
        <div className="planner-header">
          <div className="icon-circle">
            <Target size={15} color="#ec4899" />
          </div>
          <h2>Financial Planning & Safety Allocation Configurator</h2>
        </div>
        <p className="planner-subtitle">
          Personalize your monthly targets. The system automatically adjusts category thresholds and
          optimizes savings to match your safety margins.
        </p>

        <div className="planner-controls">
          <div>
            <div className="planner-income-label">Monthly Income ({sym})</div>
            <input
              type="number"
              className="planner-income-input"
              value={income}
              onChange={(e) => setIncome(Number(e.target.value))}
              onBlur={handleIncomeUpdate}
              placeholder={`${sym} 0`}
            />
          </div>

          <div className="slider-section">
            <div className="slider-header">
              <div className="slider-title">Safety Savings Allocation (%)</div>
              <div className="slider-value">{savingsPct}% Selected</div>
            </div>
            <input
              type="range"
              className="savings-slider"
              min="10"
              max="50"
              step="5"
              value={savingsPct}
              onChange={(e) => setSavingsPct(Number(e.target.value))}
              onMouseUp={handleIncomeUpdate}
              onTouchEnd={handleIncomeUpdate}
            />
            <div className="slider-labels">
              {sliderLabels.map((val) => (
                <span
                  key={val}
                  className={val === savingsPct ? 'active-label' : ''}
                >
                  {val}%{val === 20 ? ' (Standard)' : ''}
                </span>
              ))}
            </div>
          </div>
        </div>

        <div className="safety-info">
          <div className="check-icon">
            <Check />
          </div>
          <div className="safety-info-content">
            <h4>
              Current Safety Target: {sym}
              {savingsAmount.toLocaleString('en-IN', { minimumFractionDigits: 2 })} / Month
            </h4>
            <p>
              This allocates <strong>{savingsPct}%</strong> of your income to secure reserves. The
              remaining <strong>{100 - savingsPct}%</strong> is dynamically budgeted into Needs (
              {sym}
              {needsAmount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}) and Wants ({sym}
              {wantsAmount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}) using a 5:3
              optimized priority model.
            </p>
          </div>
        </div>
      </div>

      {/* Bottom Grid */}
      <div className="bottom-grid">
        {/* Recent Expenses */}
        <div className="expenses-section">
          <h3>Recent Expense Stream</h3>
          {expenses.length === 0 ? (
            <div className="no-data">No expenses logged yet. Start tracking!</div>
          ) : (
            <table className="expenses-table">
              <thead>
                <tr>
                  <th>Description</th>
                  <th>Category</th>
                  <th>Amount</th>
                  <th>Date</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {expenses.map((exp) => (
                  <tr key={exp.id}>
                    <td>{exp.description}</td>
                    <td>
                      <span className={`category-badge ${getCategoryClass(exp.category)}`}>
                        {exp.category}
                      </span>
                    </td>
                    <td className="amount-negative">
                      -{formatCurrency(exp.amount, currency)}
                    </td>
                    <td>{new Date(exp.date).toLocaleDateString()}</td>
                    <td>
                      <button
                        className="delete-btn"
                        onClick={() => handleDeleteExpense(exp.id)}
                        title="Delete expense"
                      >
                        <Trash2 />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Category Distribution */}
        <div className="category-section">
          <h3>Core Category Distribution</h3>
          {Object.keys(stats.category_distribution || {}).length === 0 ? (
            <div className="no-data">No category data yet.</div>
          ) : (
            <div className="category-list">
              {Object.entries(stats.category_distribution).map(([cat, amount]) => (
                <div className="category-item" key={cat}>
                  <span className="category-item-name">{cat}</span>
                  <span className={`category-item-amount ${getCategoryClass(cat)}`}>
                    {formatCurrency(amount, currency)}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
