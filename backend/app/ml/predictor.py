import os
import joblib
from typing import Tuple, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

class CategoryPredictor:
    def __init__(self):
        self.models_dir = os.path.join(os.path.dirname(__file__), "models")
        self.vectorizer_path = os.path.join(self.models_dir, "vectorizer.pkl")
        self.model_path = os.path.join(self.models_dir, "category_classifier.pkl")
        self.vectorizer = None
        self.model = None
        self.load_models()

    def load_models(self):
        """Loads serialized models or triggers default bootstrapping if missing."""
        if os.path.exists(self.model_path) and os.path.exists(self.vectorizer_path):
            try:
                self.vectorizer = joblib.load(self.vectorizer_path)
                self.model = joblib.load(self.model_path)
                print("[INFO] Successfully loaded category classifier weights.")
            except Exception as e:
                print(f"[WARNING] Model loading failed: {e}. Retraining...")
                self.bootstrap_default_model()
        else:
            self.bootstrap_default_model()

    def bootstrap_default_model(self):
        """Builds and serializes a standard TF-IDF + Naive Bayes classifier on baseline transactions"""
        sample_descriptions = [
            "starbucks latte coffee morning", "mcdonalds burger fries meal", "grocery supermarket items food organic",
            "uber ride city airport cab", "shell gas station fuel fill tank", "subway metro transit train card ticket",
            "netflix monthly hd plan subscription", "cinema movie tickets popcorn", "steam games digital console play",
            "electricity utility bill monthly heating", "water utility clean supply bill", "high speed home wifi router broad",
            "monthly rent payment apartment lease", "ikea table drawer desk chair", "family doctor consultation general fee",
            "prescription generic pills pharmacy drug", "target department retail store malls", "amazon delivery clothes shoes checkout online"
        ]
        sample_labels = [
            "Food & Dining", "Food & Dining", "Food & Dining",
            "Transport", "Transport", "Transport",
            "Entertainment", "Entertainment", "Entertainment",
            "Utilities", "Utilities", "Utilities",
            "Housing", "Housing", "Health & Wellness",
            "Health & Wellness", "Shopping", "Shopping"
        ]

        self.vectorizer = TfidfVectorizer(stop_words='english', min_df=1, ngram_range=(1, 2))
        X = self.vectorizer.fit_transform(sample_descriptions)
        self.model = MultinomialNB(alpha=1.0)
        self.model.fit(X, sample_labels)

        # Ensure directory structure exists and write serialized binaries
        os.makedirs(self.models_dir, exist_ok=True)
        joblib.dump(self.vectorizer, self.vectorizer_path)
        joblib.dump(self.model, self.model_path)
        print("[INFO] Default category classifier model bootstrapped successfully.")

    def retrain_model(self, descriptions: List[str], categories: List[str]):
        """Dynamically retrains the model using updated user-provided history to increase personalized accuracy."""
        if not descriptions or len(descriptions) < 5:
            # Not enough data points to successfully train yet
            return False
        
        try:
            self.vectorizer = TfidfVectorizer(stop_words='english', min_df=1, ngram_range=(1, 2))
            X = self.vectorizer.fit_transform(descriptions)
            self.model = MultinomialNB(alpha=0.5)
            self.model.fit(X, categories)

            # Persist weights
            joblib.dump(self.vectorizer, self.vectorizer_path)
            joblib.dump(self.model, self.model_path)
            print("[INFO] Model retrained successfully on custom user data.")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to retrain category model: {e}")
            return False

    def predict(self, description: str) -> Tuple[str, float]:
        """Classifies a transaction description, returning (suggested_category, confidence)"""
        if not description or not self.model or not self.vectorizer:
            return "Others", 1.0

        try:
            features = self.vectorizer.transform([description.lower()])
            probs = self.model.predict_proba(features)[0]
            max_idx = probs.argmax()
            predicted_class = self.model.classes_[max_idx]
            confidence = float(probs[max_idx])
            return predicted_class, confidence
        except Exception as e:
            print(f"[WARNING] ML inference error: {e}. Defaulting to 'Others'")
            return "Others", 1.0

# Singleton instance
predictor = CategoryPredictor()
