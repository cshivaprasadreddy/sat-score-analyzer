import numpy as np
import json
from typing import List, Dict, Tuple
from pathlib import Path

class DSATThresholdTuner:
    """Clean threshold tuner for SAT adaptive test analysis"""
    
    def __init__(self):
        self.subjects = ['Math', 'Reading and Writing']
        self.threshold_range = np.arange(0.3, 0.81, 0.01)  # 0.30 to 0.80 in 0.01 steps
    
    def load_data(self):
        """Load student data and scoring maps"""
        with open(Path("Data/scoring_DSAT_v2.json")) as f:
            scoring_data = json.load(f)
        with open(Path("Data/stu1.json")) as f:
            student_responses = json.load(f)
        return scoring_data, student_responses
    
    def calculate_prediction_accuracy(self, data: List[Dict], threshold: float, subject: str) -> float:
        """Calculate threshold prediction accuracy for a specific subject"""
        subject_data = [row for row in data if row.get('subject') == subject]
        if not subject_data:
            return 0
        
        correct_predictions = 0
        for row in subject_data:
            pred = 'hard' if (row['module1_correct'] / row['module1_total']) >= threshold else 'easy'
            if pred == row['module2_difficulty_received']:
                correct_predictions += 1
        return correct_predictions / len(subject_data)
    
    def find_optimal_threshold(self, data: List[Dict], subject: str) -> Tuple[float, float]:
        """Find optimal threshold for a subject"""
        best_accuracy = 0
        best_threshold = 0.5
        
        for threshold in self.threshold_range:
            accuracy = self.calculate_prediction_accuracy(data, threshold, subject)
            if accuracy > best_accuracy:
                best_accuracy = accuracy
                best_threshold = threshold
        
        return best_threshold, best_accuracy
    
    def get_training_data(self) -> List[Dict]:
        """Get threshold training data"""
        return [
            # Math data
            {"subject": "Math", "module1_correct": 10, "module1_total": 22, "module2_difficulty_received": "easy"},
            {"subject": "Math", "module1_correct": 14, "module1_total": 22, "module2_difficulty_received": "hard"},
            {"subject": "Math", "module1_correct": 13, "module1_total": 22, "module2_difficulty_received": "hard"},
            {"subject": "Math", "module1_correct": 11, "module1_total": 22, "module2_difficulty_received": "easy"},
            {"subject": "Math", "module1_correct": 16, "module1_total": 22, "module2_difficulty_received": "hard"},
            {"subject": "Math", "module1_correct": 12, "module1_total": 22, "module2_difficulty_received": "easy"},
            {"subject": "Math", "module1_correct": 15, "module1_total": 22, "module2_difficulty_received": "hard"},
            {"subject": "Math", "module1_correct": 9, "module1_total": 22, "module2_difficulty_received": "easy"},
            
            # Reading and Writing data
            {"subject": "Reading and Writing", "module1_correct": 11, "module1_total": 22, "module2_difficulty_received": "easy"},
            {"subject": "Reading and Writing", "module1_correct": 15, "module1_total": 22, "module2_difficulty_received": "hard"},
            {"subject": "Reading and Writing", "module1_correct": 14, "module1_total": 22, "module2_difficulty_received": "hard"},
            {"subject": "Reading and Writing", "module1_correct": 10, "module1_total": 22, "module2_difficulty_received": "easy"},
            {"subject": "Reading and Writing", "module1_correct": 16, "module1_total": 22, "module2_difficulty_received": "hard"},
            {"subject": "Reading and Writing", "module1_correct": 13, "module1_total": 22, "module2_difficulty_received": "easy"},
            {"subject": "Reading and Writing", "module1_correct": 12, "module1_total": 22, "module2_difficulty_received": "easy"},
            {"subject": "Reading and Writing", "module1_correct": 18, "module1_total": 22, "module2_difficulty_received": "hard"},
        ]
    
    def tune_thresholds(self) -> Dict[str, Dict]:
        """Main threshold tuning function"""
        print("🎯 SAT ADAPTIVE THRESHOLD TUNER")
        print("="*50)
        
        # Get training data
        training_data = self.get_training_data()
        
        results = {}
        
        for subject in self.subjects:
            print(f"\n📊 Analyzing {subject}...")
            
            # Find optimal threshold
            optimal_threshold, accuracy = self.find_optimal_threshold(training_data, subject)
            
            # Calculate subject statistics
            subject_data = [row for row in training_data if row.get('subject') == subject]
            hard_assignments = sum(1 for row in subject_data 
                                 if (row['module1_correct'] / row['module1_total']) >= optimal_threshold)
            easy_assignments = len(subject_data) - hard_assignments
            
            results[subject] = {
                'optimal_threshold': optimal_threshold,
                'accuracy': accuracy,
                'hard_percentage': hard_assignments / len(subject_data),
                'easy_percentage': easy_assignments / len(subject_data),
                'data_points': len(subject_data)
            }
            
            print(f"   ✅ Optimal Threshold: {optimal_threshold:.2f}")
            print(f"   📈 Prediction Accuracy: {accuracy:.1%}")
            print(f"   🔥 Hard Module Assignment: {hard_assignments}/{len(subject_data)} ({hard_assignments/len(subject_data):.1%})")
            print(f"   📚 Easy Module Assignment: {easy_assignments}/{len(subject_data)} ({easy_assignments/len(subject_data):.1%})")
        
        return results
    
    def validate_current_student(self, results: Dict[str, Dict]):
        """Validate thresholds against current student data"""
        print(f"\n🔍 CURRENT STUDENT VALIDATION")
        print("="*50)
        
        try:
            _, student_responses = self.load_data()
            
            for subject in self.subjects:
                threshold = results[subject]['optimal_threshold']
                
                # Get subject responses
                subject_responses = [r for r in student_responses if 
                                   (r['subject']['name'] if isinstance(r['subject'], dict) else r['subject']) == subject]
                module1_responses = [r for r in subject_responses if r['section'] == 'Static']
                
                if module1_responses:
                    current_correct = sum(1 for r in module1_responses if r['correct'])
                    total_module1 = len(module1_responses)
                    current_performance = current_correct / total_module1
                    
                    predicted_difficulty = 'hard' if current_performance >= threshold else 'easy'
                    
                    print(f"\n📋 {subject}:")
                    print(f"   Module 1 Performance: {current_correct}/{total_module1} ({current_performance:.1%})")
                    print(f"   Threshold: {threshold:.2f} ({threshold:.1%})")
                    print(f"   Predicted Module 2: {predicted_difficulty.upper()}")
                    
                    if predicted_difficulty == 'easy' and current_performance < threshold:
                        questions_needed = int((threshold * total_module1) - current_correct) + 1
                        print(f"   🔓 Answer {questions_needed} more Module 1 questions correctly to unlock HARD difficulty!")
                    elif predicted_difficulty == 'hard':
                        questions_buffer = current_correct - int(threshold * total_module1)
                        print(f"   🔒 You're in HARD mode! Don't miss more than {questions_buffer} Module 1 questions")
        
        except Exception as e:
            print(f"   ⚠️ Could not validate current student: {e}")

def main():
    """Main execution function"""
    tuner = DSATThresholdTuner()
    
    # Tune thresholds
    results = tuner.tune_thresholds()
    
    # Validate against current student
    tuner.validate_current_student(results)
    
    print(f"\n💡 KEY INSIGHTS:")
    print(f"   • Math threshold: {results['Math']['optimal_threshold']:.2f} ({results['Math']['accuracy']:.1%} accuracy)")
    print(f"   • Reading & Writing threshold: {results['Reading and Writing']['optimal_threshold']:.2f} ({results['Reading and Writing']['accuracy']:.1%} accuracy)")
    print(f"   • Different subjects need different thresholds for optimal adaptive routing!")
    print("="*50)

if __name__ == "__main__":
    main()
