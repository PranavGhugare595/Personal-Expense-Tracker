# 💸 Personal Expense Tracker — AI-Powered Full Stack ML Application

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.136-009688?logo=fastapi)
![React](https://img.shields.io/badge/React-18.2-61DAFB?logo=react)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?logo=mongodb)
![ML](https://img.shields.io/badge/ML-Scikit--Learn-F7931E?logo=scikitlearn)
![License](https://img.shields.io/badge/License-MIT-green)

> A **production-ready**, full-stack web application that combines intelligent Machine Learning models with a beautiful, responsive UI to help users track, analyze, and optimize their personal finances.

---

## ✨ Key Features

- 🔐 **JWT Authentication** — Secure login & registration with bcrypt password hashing
- 📊 **Interactive Dashboard** — Real-time expense tracking with summary KPIs and budget gauges
- 🤖 **AI Category Suggestions** — NLP-powered transaction auto-classification (TF-IDF + Naive Bayes)
- 📈 **Monthly Forecasting** — 3-month expense projections using linear time-series extrapolation
- 💰 **Budget Recommendations** — Personalized limits based on 50/30/20 budgeting rule
- 🛡️ **Resilient DB Layer** — MongoDB Atlas with automatic local offline fallback
- 🎨 **Glassmorphic Dark UI** — Premium Ant Design UI with neon glassmorphic styling
- 📱 **Standalone Client** — Open `index.html` in any browser — no server required for demo!

---

## 🏗️ Tech Stack

| Layer | Technology | Purpose |
|:------|:-----------|:--------|
| **Frontend** | React 18 + Vite | UI Framework |
| **UI Library** | Ant Design 5 | Component system |
| **Styling** | Custom CSS (Glassmorphism) | Visual design |
| **Backend** | FastAPI (Python 3.13) | REST API Server |
| **Database** | MongoDB Atlas + PyMongo | Cloud Database |
| **Auth** | JWT (PyJWT) + bcrypt | Authentication |
| **ML - NLP** | Scikit-Learn (TF-IDF + NB) | Category Classification |
| **ML - Forecast** | Pandas + NumPy | Time-Series Projection |
| **ML - Budget** | Custom Optimizer | 50/30/20 Rule Engine |
| **Deploy FE** | Vercel | Frontend Hosting |
| **Deploy BE** | Render | Backend Hosting |

---

## 📁 Project Structure

```
personal-expense-tracker/
├── backend/               # FastAPI Python Server
│   ├── app/
│   │   ├── api/v1/       # Route handlers (auth, expenses, budgets, ml)
│   │   ├── core/         # Config, Security, Database drivers
│   │   ├── ml/           # Category predictor, Forecaster
│   │   └── schemas/      # Pydantic validation models
│   ├── requirements.txt
│   └── run.py
├── frontend/              # Vite + React Client
│   ├── src/
│   │   ├── App.jsx       # Main application component
│   │   └── assets/styles/index.css  # Glassmorphic Design System
│   └── package.json
├── index.html             # ⚡ Standalone client (open in any browser!)
└── README.md
```

---

## 🚀 Quick Start

### ⚡ Instant Demo (No Setup Required!)
Simply **double-click** `index.html` in your browser to explore the full UI with offline sandbox data!

---

### 🐍 Backend Setup

```bash
# 1. Navigate to backend
cd backend

# 2. Create virtual environment
python -m venv .venv

# 3. Activate environment (Windows)
.\.venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure environment
copy .env.example .env
# Edit .env with your MongoDB Atlas connection string

# 6. Launch FastAPI server
python run.py
```

Backend runs at: **`http://localhost:8000`**  
Swagger UI: **`http://localhost:8000/docs`**

---

### ⚛️ Frontend Setup (Vite React)

> **Note**: Requires Node.js v18+ to be installed.

```bash
# 1. Navigate to frontend
cd frontend

# 2. Install packages
npm install

# 3. Configure API URL
copy .env.example .env
# Set VITE_API_URL=http://localhost:8000

# 4. Start dev server
npm run dev
```

Frontend runs at: **`http://localhost:5173`**

---

## 🌐 Environment Variables

### Backend (`backend/.env`)
```env
PROJECT_NAME="Personal Expense Tracker API"
MONGODB_URL="mongodb+srv://<user>:<pass>@cluster0.mongodb.net/expense_db"
JWT_SECRET_KEY="your-super-secret-key-here"
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ENVIRONMENT="production"
```

### Frontend (`frontend/.env`)
```env
VITE_API_URL="https://your-backend.onrender.com"
```

---

## 🧠 ML Architecture

```
User Input Text
    ↓
TF-IDF Vectorizer (bi-gram, stopwords removed)
    ↓
Multinomial Naive Bayes Classifier
    ↓
Category + Confidence Score (e.g., "Food & Dining" @ 94.2%)

Historical Expenses
    ↓
Monthly Aggregation (Pandas resample)
    ↓
Linear Regression Extrapolation
    ↓
3-Month Forecast + Confidence Intervals
```

---

## 🚢 Deployment

| Service | Platform | Configuration |
|:--------|:---------|:-------------|
| **Frontend** | Vercel | Root: `frontend/`, Build: `npm run build`, Output: `dist` |
| **Backend** | Render | Root: `backend/`, Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Database** | MongoDB Atlas | M0 Free Tier, IP whitelist: `0.0.0.0/0` |

---

## 📸 API Endpoints

| Method | Endpoint | Description |
|:-------|:---------|:------------|
| `POST` | `/api/v1/auth/register` | Register new user |
| `POST` | `/api/v1/auth/login` | Login & get JWT |
| `GET` | `/api/v1/expenses` | List all expenses |
| `POST` | `/api/v1/expenses` | Create expense |
| `POST` | `/api/v1/ml/suggest-category` | AI category prediction |
| `GET` | `/api/v1/ml/forecast` | 3-month forecast |
| `GET` | `/api/v1/ml/insights` | Budget recommendations |

---

## 🔒 Security

- Passwords hashed with **bcrypt** (12 rounds)
- Tokens signed with **HS256 JWT** (24-hour expiry)
- CORS configured per deployment environment
- Input validated via **Pydantic v2** schemas
- No raw credentials stored in database

---

## 📅 Development Timeline

| Week | Deliverable |
|:-----|:-----------|
| Week 1 | Environment setup, MongoDB Atlas, DB schema design |
| Week 2 | JWT auth, Expense & Budget CRUD API |
| Week 3 | ML NLP classifier, forecasting, budget optimizer |
| Week 4 | React frontend + Ant Design integration |
| Week 5 | Dashboard, charts, ML insight panels |
| Week 6 | Testing, deployment, production tuning |

---

## 🤝 Contributing

Pull requests are welcome. For major changes, open an issue first to discuss what you'd like to change.

---

## 📄 License

This project is open-source under the [MIT License](LICENSE).

---

*Built with ❤️ as a full-stack ML portfolio project.*
