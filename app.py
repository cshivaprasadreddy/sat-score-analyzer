from flask import Flask, render_template, jsonify
import json
from pathlib import Path
import sys
import os

# Add the current directory to Python path to import our analyzer
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from whatif import DSATWhatIfAnalyzer

app = Flask(__name__)

def load_data():
    """Load student data and scoring maps"""
    try:
        with open(Path("Data/scoring_DSAT_v2.json")) as f:
            scoring_data = json.load(f)
        with open(Path("Data/stu1.json")) as f:
            student_responses = json.load(f)
        return scoring_data, student_responses
    except Exception as e:
        print(f"Error loading data: {e}")
        return None, None

def analyze_student_data():
    """Run the SAT analysis and return structured results"""
    scoring_data, student_responses = load_data()
    
    if not scoring_data or not student_responses:
        return None
    
    # Initialize analyzer
    analyzer = DSATWhatIfAnalyzer(scoring_data)
    
    # Set dynamic thresholds
    historical_data = analyzer.collect_threshold_data()
    analyzer.set_dynamic_thresholds(historical_data)
    
    # Generate recommendations
    results = analyzer.generate_recommendations(student_responses)
    
    # Calculate subject-specific scores for visualization
    subject_scores = {}
    total_current = results['current_total_score']
    total_potential = total_current
    
    for subject in analyzer.subjects:
        recs = results['recommendations'][subject]
        
        # Calculate current subject score (approximate split)
        if subject == "Math":
            current_subject_score = total_current // 2
        else:
            current_subject_score = total_current - (total_current // 2)
        
        potential_gain = recs['total_potential_gain']
        potential_subject_score = current_subject_score + potential_gain
        total_potential += potential_gain
        
        # Get complexity breakdown
        easy_questions = [q for q in recs['high_impact_questions'] if q.get('difficulty', 'medium').lower() == 'easy']
        medium_questions = [q for q in recs['high_impact_questions'] if q.get('difficulty', 'medium').lower() == 'medium']
        hard_questions = [q for q in recs['high_impact_questions'] if q.get('difficulty', 'medium').lower() == 'hard']
        
        subject_scores[subject] = {
            'current': current_subject_score,
            'potential': potential_subject_score,
            'max_gain': potential_gain,
            'threshold': analyzer.adaptive_thresholds[subject],
            'current_difficulty': results['current_module2_difficulties'][subject],
            'top_questions': recs['high_impact_questions'][:5],
            'complexity_breakdown': {
                'easy': len(easy_questions),
                'medium': len(medium_questions),
                'hard': len(hard_questions)
            },
            'complexity_impact': {
                'easy': sum(q['impact_score'] for q in easy_questions),
                'medium': sum(q['impact_score'] for q in medium_questions),
                'hard': sum(q['impact_score'] for q in hard_questions)
            }
        }
    
    return {
        'subject_scores': subject_scores,
        'total_current': total_current,
        'total_potential': total_potential,
        'total_gain': total_potential - total_current,
        'thresholds': analyzer.adaptive_thresholds
    }

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/analysis')
def get_analysis():
    """API endpoint to get analysis data"""
    data = analyze_student_data()
    if data:
        return jsonify(data)
    else:
        return jsonify({'error': 'Failed to load data'}), 500

@app.route('/api/score-progression/<subject>')
def get_score_progression(subject):
    """Get score progression data for a specific subject"""
    data = analyze_student_data()
    if not data or subject not in data['subject_scores']:
        return jsonify({'error': 'Subject not found'}), 404
    
    subject_data = data['subject_scores'][subject]
    
    # Calculate progression scores
    progression = [subject_data['current']]
    cumulative_gain = 0
    
    for q in subject_data['top_questions']:
        cumulative_gain += q['impact_score']
        progression.append(subject_data['current'] + cumulative_gain)
    
    return jsonify({
        'labels': ['Current', 'Fix Top 1', 'Fix Top 2', 'Fix Top 3', 'Fix Top 4', 'Fix Top 5'],
        'data': progression[:6],  # Ensure we don't exceed available data
        'questions': subject_data['top_questions']
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
