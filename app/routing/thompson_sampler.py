"""
Thompson Sampling Module
Implements Thompson Sampling for multi-armed bandit optimization.
Uses Beta distribution priors to model model performance.
"""

import numpy as np
from typing import List, Dict, Any, Tuple


class BetaBandit:
    """
    Thompson Sampling with Beta priors.
    Each model is a "bandit arm" with success/failure counts.
    """
    
    def __init__(self, alpha: float = 1.0, beta: float = 1.0):
        """
        Initialize with Beta priors.
        Alpha = successes, Beta = failures
        Uniform prior: alpha=1, beta=1
        """
        self.alpha = alpha
        self.beta = beta
    
    def sample(self) -> float:
        """
        Sample from Beta distribution.
        Returns a probability estimate between 0 and 1.
        """
        return np.random.beta(self.alpha, self.beta)
    
    def update_success(self):
        """Update after successful response."""
        self.alpha += 1
    
    def update_failure(self):
        """Update after failed response."""
        self.beta += 1
    
    def update_with_reward(self, reward: float):
        """
        Update based on reward score (0-1).
        Higher reward = more success increment
        """
        # Treat reward as probability of success
        if reward >= 0.7:  # Good reward
            self.alpha += 1
        elif reward < 0.3:  # Poor reward
            self.beta += 1
        # Medium rewards (0.3-0.7) contribute partial updates
        else:
            self.alpha += reward / 2
            self.beta += (1 - reward) / 2
    
    def get_posterior_mean(self) -> float:
        """Get posterior mean (expected value of success probability)."""
        return self.alpha / (self.alpha + self.beta)
    
    def get_posterior_variance(self) -> float:
        """Get posterior variance (uncertainty)."""
        total = self.alpha + self.beta
        return (self.alpha * self.beta) / (total * total * (total + 1))


class ThompsonSampler:
    """
    Thompson Sampling optimizer for model selection.
    """
    
    def __init__(self):
        """Initialize sampler with no bandits."""
        self.bandits: Dict[str, BetaBandit] = {}
        self.model_stats: Dict[str, Dict[str, Any]] = {}
    
    def register_model(self, model_name: str, initial_alpha: float = 1.0, initial_beta: float = 1.0):
        """Register a new model for Thompson Sampling."""
        if model_name not in self.bandits:
            self.bandits[model_name] = BetaBandit(alpha=initial_alpha, beta=initial_beta)
            self.model_stats[model_name] = {
                "selections": 0,
                "successes": 0,
                "failures": 0,
                "total_reward": 0.0,
                "avg_reward": 0.0
            }
    
    def select_best_thompson(self, candidate_models: List[str]) -> str:
        """
        Select best model using Thompson Sampling.
        Samples from each candidate's posterior, returns argmax sample.
        """
        if not candidate_models:
            raise ValueError("No candidate models provided")
        
        # Register any new models
        for model in candidate_models:
            self.register_model(model)
        
        # Sample from each candidate's posterior
        samples = {}
        for model in candidate_models:
            sample = self.bandits[model].sample()
            samples[model] = sample
        
        # Select model with highest sample
        selected = max(samples.items(), key=lambda x: x[1])
        return selected[0], samples
    
    def select_best_greedy(self, candidate_models: List[str]) -> str:
        """
        Select best model using greedy (exploitation only).
        Returns model with highest posterior mean.
        """
        if not candidate_models:
            raise ValueError("No candidate models provided")
        
        for model in candidate_models:
            self.register_model(model)
        
        best_model = max(
            candidate_models,
            key=lambda m: self.bandits[m].get_posterior_mean()
        )
        return best_model
    
    def update_performance(self, model_name: str, reward: float):
        """
        Update model performance based on reward score.
        
        Args:
            model_name: Name of the model
            reward: Reward score 0-1
        """
        if model_name not in self.bandits:
            self.register_model(model_name)
        
        # Update bandit
        self.bandits[model_name].update_with_reward(reward)
        
        # Update statistics
        stats = self.model_stats[model_name]
        stats["selections"] += 1
        stats["total_reward"] += reward
        stats["avg_reward"] = stats["total_reward"] / stats["selections"]
        
        if reward >= 0.7:
            stats["successes"] += 1
        else:
            stats["failures"] += 1
    
    def get_model_stats(self, model_name: str) -> Dict[str, Any]:
        """Get statistics for a model."""
        if model_name not in self.model_stats:
            return None
        
        stats = self.model_stats[model_name].copy()
        bandit = self.bandits[model_name]
        stats["posterior_mean"] = round(bandit.get_posterior_mean(), 4)
        stats["posterior_variance"] = round(bandit.get_posterior_variance(), 6)
        stats["alpha"] = bandit.alpha
        stats["beta"] = bandit.beta
        
        return stats
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all registered models."""
        return {
            model: self.get_model_stats(model)
            for model in self.bandits.keys()
        }
    
    def get_model_recommendations(self, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Get top K models by posterior mean (exploitation ranking).
        Returns list of (model_name, posterior_mean) sorted by quality.
        """
        rankings = [
            (model, self.bandits[model].get_posterior_mean())
            for model in self.bandits.keys()
        ]
        rankings.sort(key=lambda x: x[1], reverse=True)
        return rankings[:top_k]


# Global Thompson Sampler instance
_global_sampler = None


def get_thompson_sampler() -> ThompsonSampler:
    """Get or create global Thompson Sampler instance.
    On first call, loads historical α/β from ModelPerformance DB table."""
    global _global_sampler
    if _global_sampler is None:
        _global_sampler = ThompsonSampler()
        # FIX #6: Load persisted bandit state from database
        try:
            from app.database_init import SessionLocal
            from app.models import ModelPerformance
            db = SessionLocal()
            records = db.query(ModelPerformance).all()
            loaded = 0
            for r in records:
                alpha = r.alpha if r.alpha and r.alpha > 0 else 1.0
                beta = r.beta if r.beta and r.beta > 0 else 1.0
                _global_sampler.register_model(r.model_id, initial_alpha=alpha, initial_beta=beta)
                # Restore stats
                _global_sampler.model_stats[r.model_id] = {
                    "selections": r.total_selections or 0,
                    "successes": r.successful_responses or 0,
                    "failures": r.failed_responses or 0,
                    "total_reward": r.total_reward or 0.0,
                    "avg_reward": r.avg_reward or 0.0
                }
                loaded += 1
            db.close()
            if loaded > 0:
                print(f"[BANDIT] Loaded {loaded} model performance records from database")
        except Exception as e:
            print(f"[BANDIT] Could not load DB state (non-fatal): {e}")
    return _global_sampler


def reset_thompson_sampler():
    """Reset global sampler (for testing)."""
    global _global_sampler
    _global_sampler = None
