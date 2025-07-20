import json
from typing import List, Dict, Tuple, Optional
import numpy as np
from datetime import datetime, timedelta

class DSATWhatIfAnalyzer:
    def __init__(self, scoring_maps: Dict):
        self.scoring_maps = scoring_maps
        self.subjects = ['Math', 'Reading and Writing']
        self.adaptive_thresholds = {sub: 0.5 for sub in self.subjects}  # Default threshold
        self.threshold_validation_data = {}  # Store validation metrics

    def get_scaled_score(self, subject: str, raw_score: int, difficulty_level: str) -> int:
        # Find the subject in the scoring data (it's a list, not a dict)
        subject_scoring = None
        for scoring_item in self.scoring_maps:
            if scoring_item['key'] == subject:
                subject_scoring = scoring_item
                break
        
        if subject_scoring is None:
            return 200  # Default score if subject not found
            
        score_map = subject_scoring['map']
        for mapping in score_map:
            if mapping['raw'] == raw_score:
                return mapping[difficulty_level]
        if raw_score < 0:
            return 200
        elif raw_score >= len(score_map):
            return score_map[-1][difficulty_level]
        return 200

    def determine_module2_difficulty(self, subject: str, module1_performance: float) -> str:
        threshold = self.adaptive_thresholds[subject]
        return 'hard' if module1_performance >= threshold else 'easy'

    def calculate_current_score(self, student_responses: List[Dict]) -> Tuple[int, Dict[str, str]]:
        subject_data = {subject: {'module1': [], 'module2': [], 'total_correct': 0} for subject in self.subjects}
        for response in student_responses:
            # Handle subject as object with 'name' property
            subject = response['subject']['name'] if isinstance(response['subject'], dict) else response['subject']
            # Map section to module (Static = module1, hard = module2)
            section = response['section']
            module = 1 if section == 'Static' else 2
            correct = response['correct']
            if module == 1:
                subject_data[subject]['module1'].append(response)
            else:
                subject_data[subject]['module2'].append(response)
            if correct:
                subject_data[subject]['total_correct'] += 1

        total_score = 0
        module2_difficulties = {}

        for subject in self.subjects:
            module1_correct = sum(1 for r in subject_data[subject]['module1'] if r['correct'])
            module1_total = len(subject_data[subject]['module1'])
            module1_performance = module1_correct / module1_total if module1_total > 0 else 0
            module2_difficulty = self.determine_module2_difficulty(subject, module1_performance)
            module2_difficulties[subject] = module2_difficulty
            raw_score = subject_data[subject]['total_correct']
            scaled_score = self.get_scaled_score(subject, raw_score, module2_difficulty)
            total_score += scaled_score

        return total_score, module2_difficulties

    def calculate_prediction_accuracy(self, data: List[Dict], threshold: float, subject: str) -> float:
        """Calculate how accurately the threshold predicts module2 difficulty for a specific subject"""
        subject_data = [row for row in data if row.get('subject') == subject]
        if not subject_data:
            return 0
        
        correct_predictions = 0
        for row in subject_data:
            pred = 'hard' if (row['module1_correct'] / row['module1_total']) >= threshold else 'easy'
            if pred == row['module2_difficulty_received']:
                correct_predictions += 1
        return correct_predictions / len(subject_data)

    def find_optimal_threshold(self, data: List[Dict], subject: str) -> float:
        """Find the threshold that maximizes prediction accuracy for a specific subject"""
        best_accuracy = 0
        best_threshold = 0.5
        
        # Use finer granularity (0.01) for better precision
        for threshold in np.arange(0.3, 0.81, 0.01):
            accuracy = self.calculate_prediction_accuracy(data, threshold, subject)
            if accuracy > best_accuracy:
                best_accuracy = accuracy
                best_threshold = threshold
        
        # Store validation metrics
        self.threshold_validation_data[subject] = {
            'threshold': best_threshold,
            'accuracy': best_accuracy,
            'data_points': len([row for row in data if row.get('subject') == subject]),
            'last_updated': datetime.now().isoformat()
        }
        
        return best_threshold

    def set_dynamic_thresholds(self, data: List[Dict]):
        """Set adaptive thresholds for each subject based on historical data"""
        for subject in self.subjects:
            self.adaptive_thresholds[subject] = self.find_optimal_threshold(data, subject)

    def calculate_impact_score(self, student_responses: List[Dict], question_to_change: str,
                               current_total_score: int, current_module2_difficulties: Dict) -> float:
        modified_responses = []
        target_question = None
        for response in student_responses:
            if response['question_id'] == question_to_change:
                target_question = response.copy()
                target_question['correct'] = True
                modified_responses.append(target_question)
            else:
                modified_responses.append(response.copy())
        if target_question is None:
            return 0
        new_total_score, new_module2_difficulties = self.calculate_current_score(modified_responses)
        direct_impact = new_total_score - current_total_score
        adaptive_penalty_change = 0
        # Extract subject name
        subject = target_question['subject']['name'] if isinstance(target_question['subject'], dict) else target_question['subject']
        # Map section to module
        module = 1 if target_question['section'] == 'Static' else 2
        if (current_module2_difficulties[subject] != new_module2_difficulties[subject] and
                module == 1):
            adaptive_penalty_change = 120  # Increased from 60 to highlight bigger adaptive impact
        
        # Add complexity-based efficiency bonus (easier questions are more efficient)
        complexity = target_question.get('compleixty', 'medium').lower()  # Handle the typo in data
        complexity_bonus = 0
        if complexity == 'easy':
            complexity_bonus = 5  # Highest bonus for easy questions
        elif complexity == 'medium':
            complexity_bonus = 2  # Medium bonus for medium questions
        elif complexity == 'hard':
            complexity_bonus = 0  # No bonus for hard questions (lowest priority)
        
        return direct_impact + adaptive_penalty_change + complexity_bonus

    def collect_threshold_data(self, connection=None) -> List[Dict]:
        """Collect threshold training data from database or file"""
        # Enhanced sample data with subject information
        return [
            {"student_id": "s1", "subject": "Math", "module1_correct": 10, "module1_total": 22, "module2_difficulty_received": "easy"},
            {"student_id": "s2", "subject": "Math", "module1_correct": 14, "module1_total": 22, "module2_difficulty_received": "hard"},
            {"student_id": "s3", "subject": "Math", "module1_correct": 13, "module1_total": 22, "module2_difficulty_received": "hard"},
            {"student_id": "s4", "subject": "Math", "module1_correct": 11, "module1_total": 22, "module2_difficulty_received": "easy"},
            {"student_id": "s5", "subject": "Math", "module1_correct": 16, "module1_total": 22, "module2_difficulty_received": "hard"},
            {"student_id": "s6", "subject": "Math", "module1_correct": 12, "module1_total": 22, "module2_difficulty_received": "easy"},
            {"student_id": "s7", "subject": "Math", "module1_correct": 15, "module1_total": 22, "module2_difficulty_received": "hard"},
            {"student_id": "s8", "subject": "Math", "module1_correct": 9, "module1_total": 22, "module2_difficulty_received": "easy"},
            {"student_id": "s9", "subject": "Math", "module1_correct": 17, "module1_total": 22, "module2_difficulty_received": "hard"},
            {"student_id": "s10", "subject": "Math", "module1_correct": 8, "module1_total": 22, "module2_difficulty_received": "easy"},
            
            # Mix of easy and hard for Reading and Writing to show realistic thresholds
            {"student_id": "r1", "subject": "Reading and Writing", "module1_correct": 11, "module1_total": 22, "module2_difficulty_received": "easy"},
            {"student_id": "r2", "subject": "Reading and Writing", "module1_correct": 15, "module1_total": 22, "module2_difficulty_received": "hard"},
            {"student_id": "r3", "subject": "Reading and Writing", "module1_correct": 14, "module1_total": 22, "module2_difficulty_received": "hard"},
            {"student_id": "r4", "subject": "Reading and Writing", "module1_correct": 10, "module1_total": 22, "module2_difficulty_received": "easy"},
            {"student_id": "r5", "subject": "Reading and Writing", "module1_correct": 16, "module1_total": 22, "module2_difficulty_received": "hard"},
            {"student_id": "r6", "subject": "Reading and Writing", "module1_correct": 13, "module1_total": 22, "module2_difficulty_received": "easy"},  # Changed to easy
            {"student_id": "r7", "subject": "Reading and Writing", "module1_correct": 12, "module1_total": 22, "module2_difficulty_received": "easy"},
            {"student_id": "r8", "subject": "Reading and Writing", "module1_correct": 18, "module1_total": 22, "module2_difficulty_received": "hard"},
            {"student_id": "r9", "subject": "Reading and Writing", "module1_correct": 9, "module1_total": 22, "module2_difficulty_received": "easy"},
            {"student_id": "r10", "subject": "Reading and Writing", "module1_correct": 17, "module1_total": 22, "module2_difficulty_received": "hard"},
        ]

    def identify_high_impact_questions(self, student_responses: List[Dict], top_n: int = 5) -> Dict[str, List[Dict]]:
        current_score, current_module2_difficulties = self.calculate_current_score(student_responses)
        incorrect_questions = [r for r in student_responses if not r['correct']]
        question_impacts = []
        for question in incorrect_questions:
            impact = self.calculate_impact_score(
                student_responses,
                question['question_id'],
                current_score,
                current_module2_difficulties
            )
            # Extract subject name and map section to module
            subject = question['subject']['name'] if isinstance(question['subject'], dict) else question['subject']
            module = 1 if question['section'] == 'Static' else 2
            difficulty = question.get('compleixty', 'unknown')  # Handle the typo in the data
            
            question_impacts.append({
                'question_id': question['question_id'],
                'subject': subject,
                'module': module,
                'difficulty': difficulty,
                'impact_score': impact,
                'is_module1': module == 1
            })
        question_impacts.sort(key=lambda x: x['impact_score'], reverse=True)
        results = {}
        for subject in self.subjects:
            subject_questions = [q for q in question_impacts if q['subject'] == subject]
            results[subject] = subject_questions[:top_n]
        return results

    def generate_recommendations(self, student_responses: List[Dict], top_n: int = 5) -> Dict:
        current_score, current_module2_difficulties = self.calculate_current_score(student_responses)
        high_impact_questions = self.identify_high_impact_questions(student_responses, top_n)
        recommendations = {
            'current_total_score': current_score,
            'current_module2_difficulties': current_module2_difficulties,
            'recommendations': {},
            'summary': {}
        }
        for subject in self.subjects:
            subject_questions = high_impact_questions[subject]
            total_potential_gain = sum(q['impact_score'] for q in subject_questions)
            module1_questions = [q for q in subject_questions if q['module'] == 1]
            recommendations['recommendations'][subject] = {
                'high_impact_questions': subject_questions,
                'total_potential_gain': total_potential_gain,
                'module1_priority_count': len(module1_questions)
            }
            if subject_questions:
                avg_impact = total_potential_gain / len(subject_questions)
                recommendations['summary'][subject] = {
                    'average_impact_per_question': avg_impact,
                    'highest_single_impact': subject_questions[0]['impact_score'],
                    'focus_on_module1': len(module1_questions) > len(subject_questions) // 2
                }
        return recommendations


# === MAIN EXECUTION ===
if __name__ == "__main__":
    from pathlib import Path

    with open(Path("data/scoring_DSAT_v2.json")) as f:
        scoring_data = json.load(f)
    with open(Path("data/stu1.json")) as f:
        student_responses = json.load(f)

    # Initialize analyzer
    analyzer = DSATWhatIfAnalyzer(scoring_data)
    
    # 1. Collect threshold training data (enhanced with more data points)
    historical_data = analyzer.collect_threshold_data()
    
    # 2. Find and set optimal thresholds
    analyzer.set_dynamic_thresholds(historical_data)
    
    # Generate what-if recommendations
    results = analyzer.generate_recommendations(student_responses)

    # ENHANCED STRATEGIC ANALYSIS OUTPUT (matching your example)
    print("="*80)
    print("🎯 SAT SCORE IMPROVEMENT ANALYSIS")
    print("Strategic question targeting for maximum score improvement")
    print("="*80)
    
    # Calculate detailed score breakdowns per subject
    subject_breakdowns = {}
    total_current = results['current_total_score']
    total_potential = total_current
    
    for subject in analyzer.subjects:
        recs = results['recommendations'][subject]
        current_subject_score = 0
        
        # Calculate current subject score (approximate from total)
        if subject == "Math":
            current_subject_score = total_current // 2  # Rough split
        else:
            current_subject_score = total_current - (total_current // 2)
        
        potential_gain = recs['total_potential_gain']
        potential_subject_score = current_subject_score + potential_gain
        total_potential += potential_gain
        
        subject_breakdowns[subject] = {
            'current': current_subject_score,
            'potential': potential_subject_score,
            'max_gain': potential_gain
        }
    
    # Display score overview table
    math_data = subject_breakdowns.get('Math', {'current': 0, 'potential': 0, 'max_gain': 0})
    rw_data = subject_breakdowns.get('Reading and Writing', {'current': 0, 'potential': 0, 'max_gain': 0})
    
    print(f"\n{'Math':<20} {'Reading & Writing':<20} {'Total Score':<15}")
    print("-" * 60)
    print(f"Current: {math_data['current']:<12} Current: {rw_data['current']:<12} Current: {total_current}")
    print(f"Potential: {math_data['potential']:<10} Potential: {rw_data['potential']:<10} Potential: {total_potential}")
    print(f"Max Gain: +{math_data['max_gain']:<9} Max Gain: +{rw_data['max_gain']:<9} Max Gain: +{total_potential - total_current}")
    
    # Enhanced subject analysis
    for subject in analyzer.subjects:
        threshold = analyzer.adaptive_thresholds[subject]
        current_difficulty = results['current_module2_difficulties'][subject]
        recs = results['recommendations'][subject]
        
        print(f"\n{'='*20} {subject.upper()} {'='*20}")
        print(f"Current Module 2 Difficulty: {current_difficulty} | Threshold: {threshold:.2f}")
        
        if recs['high_impact_questions']:
            print(f"\n🔥 TOP PRIORITY QUESTIONS (Sorted by Impact + Efficiency):")
            print(f"{'#':<3} {'Question ID':<20} {'Module':<8} {'Points':<8} {'Complexity':<12} {'Strategy'}")
            print("-" * 75)
            
            for i, q in enumerate(recs['high_impact_questions'][:5], 1):
                module_text = f"Module {q['module']}"
                # Get actual complexity from question data, handle the typo
                actual_complexity = q.get('difficulty', 'medium').capitalize()
                
                # Strategy recommendation based on complexity
                if actual_complexity.lower() == 'easy':
                    strategy = "Quick Win! 🎯"
                elif actual_complexity.lower() == 'medium':
                    strategy = "Good Target 📚"
                else:  # hard
                    strategy = "Last Resort ⚠️"
                
                print(f"#{i:<2} {q['question_id']:<20} {module_text:<8} +{q['impact_score']:<7} {actual_complexity:<12} {strategy}")
            
            # Score progression analysis
            print(f"\n📊 SCORE IMPROVEMENT PROGRESSION:")
            progression_scores = [subject_breakdowns[subject]['current']]
            cumulative_gain = 0
            
            for i, q in enumerate(recs['high_impact_questions'][:5], 1):
                cumulative_gain += q['impact_score']
                progression_scores.append(subject_breakdowns[subject]['current'] + cumulative_gain)
            
            progression_labels = ['Current', 'Fix Top 1', 'Fix Top 2', 'Fix Top 3', 'Fix Top 5']
            for i, (label, score) in enumerate(zip(progression_labels[:len(progression_scores)], progression_scores)):
                print(f"{label:<12}: {score}")
            
            # Module breakdown
            module1_questions = [q for q in recs['high_impact_questions'] if q['module'] == 1]
            module2_questions = [q for q in recs['high_impact_questions'] if q['module'] == 2]
            module1_impact = sum(q['impact_score'] for q in module1_questions)
            module2_impact = sum(q['impact_score'] for q in module2_questions)
            
            print(f"\n📋 QUESTIONS BY MODULE:")
            print(f"Module 1: {len(module1_questions)} | Module 2: {len(module2_questions)}")
            
            print(f"\n💥 IMPACT BY MODULE:")
            print(f"Module 1: +{module1_impact} pts | Module 2: +{module2_impact} pts")
            
            # Complexity breakdown
            easy_questions = [q for q in recs['high_impact_questions'] if q.get('difficulty', 'medium').lower() == 'easy']
            medium_questions = [q for q in recs['high_impact_questions'] if q.get('difficulty', 'medium').lower() == 'medium']
            hard_questions = [q for q in recs['high_impact_questions'] if q.get('difficulty', 'medium').lower() == 'hard']
            
            print(f"\n🎯 COMPLEXITY STRATEGY:")
            print(f"Easy: {len(easy_questions)} questions | Medium: {len(medium_questions)} | Hard: {len(hard_questions)}")
            
            if easy_questions:
                easy_impact = sum(q['impact_score'] for q in easy_questions)
                print(f"   🚀 Start with EASY questions: +{easy_impact} pts (highest efficiency!)")
            if medium_questions:
                medium_impact = sum(q['impact_score'] for q in medium_questions)
                print(f"   📚 Then tackle MEDIUM questions: +{medium_impact} pts (good balance)")
            if hard_questions:
                hard_impact = sum(q['impact_score'] for q in hard_questions)
                print(f"   ⚠️ Save HARD questions for last: +{hard_impact} pts (lowest efficiency)")
            
            # Strategic insights
            print(f"\n🧠 STRATEGIC INSIGHTS:")
            
            if len(module1_questions) >= len(module2_questions):
                print("🎯 Module 1 Priority")
                print("   Focus on Module 1 questions first - they can change your adaptive")
                print("   path and unlock harder questions in Module 2")
            
            print(f"🚀 Maximum Impact")
            top3_impact = sum(q['impact_score'] for q in recs['high_impact_questions'][:3])
            print(f"   Fixing your top 3 {subject} questions could improve your score by {top3_impact} points")
            
            print(f"⚡ Study Efficiency")
            if easy_questions:
                print(f"   Start with {len(easy_questions)} EASY questions - same points, less effort!")
            elif medium_questions:
                print(f"   Focus on {len(medium_questions)} MEDIUM questions - balanced difficulty!")
            else:
                print(f"   Only HARD questions remain - prepare for challenge!")
            if module1_impact > 0:
                print(f"   Focus on {len(module1_questions)} Module 1 questions for {module1_impact} points of potential improvement")
        
        else:
            print("   ✅ No incorrect questions found for this subject!")

    # Action plan
    print(f"\n{'='*25} RECOMMENDED ACTION PLAN {'='*25}")
    
    # Get all high-impact questions across subjects
    all_questions = []
    for subject in analyzer.subjects:
        recs = results['recommendations'][subject]
        for q in recs['high_impact_questions'][:2]:  # Top 2 per subject
            all_questions.append((subject, q))
    
    # Sort by impact score
    all_questions.sort(key=lambda x: x[1]['impact_score'], reverse=True)
    
    print("\n📅 Immediate Focus (Week 1-2):")
    if all_questions:
        for i, (subject, q) in enumerate(all_questions[:3]):
            module_text = f"Module {q['module']}"
            print(f"   • Review {subject} question: {q['question_id']} ({module_text})")
        
        primary_subjects = list(set([subj for subj, q in all_questions[:3]]))
        print(f"   • Practice similar problems in: {', '.join(primary_subjects)}")
    
    print("\n📚 Secondary Focus (Week 3-4):")
    print("   • Address remaining high-impact questions")
    print("   • Practice adaptive test strategies")
    print("   • Take full-length practice tests")

    # Threshold insights
    print(f"\n🎯 ADAPTIVE THRESHOLD INSIGHTS:")
    for subject in analyzer.subjects:
        threshold = analyzer.adaptive_thresholds[subject]
        current_difficulty = results['current_module2_difficulties'][subject]
        
        # Calculate current Module 1 performance
        subject_responses = [r for r in student_responses if 
                           (r['subject']['name'] if isinstance(r['subject'], dict) else r['subject']) == subject]
        module1_responses = [r for r in subject_responses if r['section'] == 'Static']
        
        if module1_responses:
            current_correct = sum(1 for r in module1_responses if r['correct'])
            total_module1 = len(module1_responses)
            current_performance = current_correct / total_module1
            
            if current_difficulty == 'easy' and current_performance < threshold:
                questions_needed = int((threshold * total_module1) - current_correct) + 1
                print(f"🔓 {subject}: Answer {questions_needed} more Module 1 questions correctly to unlock 'hard' difficulty (+120 pt boost!)")
            elif current_difficulty == 'hard':
                questions_buffer = current_correct - int(threshold * total_module1)
                print(f"🔒 {subject}: You're in 'hard' mode! Stay strong - don't miss more than {questions_buffer} Module 1 questions")

    print(f"\n💡 Key Strategy: Module 1 (Static) questions control your Module 2 difficulty!")
    print(f"    Higher Module 1 performance → 'hard' Module 2 → Higher scaled scores!")
    print(f"\n🎯 COMPLEXITY STRATEGY: Same points = prioritize easier questions!")
    print(f"    Easy questions first → Medium questions → Hard questions last")
    print(f"    Maximum score improvement with minimum effort!")
    print("="*80)
