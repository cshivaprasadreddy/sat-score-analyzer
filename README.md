# SAT Score Improvement Analysis System

A comprehensive SAT analysis system with threshold tuning and web dashboard for strategic score improvement.

## 🎯 Core Components

### 1. **Threshold Tuner** (`threshold_tuner.py`)
- **Purpose**: Find optimal adaptive thresholds for each SAT subject
- **Key Features**:
  - Subject-specific threshold optimization (Math: 55%, Reading & Writing: 60%)
  - Prediction accuracy validation (100% accuracy on training data)
  - Current student validation with actionable insights
  - Clean, focused analysis with minimal dependencies

**Usage:**
```bash
python threshold_tuner.py
```

### 2. **What-If Analysis** (`whatif.py`)
- **Purpose**: Strategic question prioritization for maximum score improvement
- **Key Features**:
  - Complexity-based efficiency bonus (Easy +5, Medium +2, Hard +0 points)
  - Dynamic threshold adaptation per subject
  - Module 1 vs Module 2 impact analysis
  - Comprehensive strategic output with action plans

**Usage:**
```bash
python whatif.py
```

### 3. **Web Dashboard** (`app.py` + `templates/dashboard.html`)
- **Purpose**: Interactive visualization of SAT analysis results
- **Key Features**:
  - Real-time score comparison charts
  - Subject-specific progression visualization
  - Complexity strategy breakdown
  - Professional UI with responsive design

**Usage:**
```bash
python app.py
# Open: http://127.0.0.1:5000
```

## 📊 Data Requirements

```
Data/
├── stu1.json              # Student response data
└── scoring_DSAT_v2.json   # SAT scoring maps
```

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Threshold Analysis**
   ```bash
   python threshold_tuner.py
   ```

3. **Run Score Improvement Analysis**
   ```bash
   python whatif.py
   ```

4. **Launch Web Dashboard** (Optional)
   ```bash
   python app.py
   ```

## 🎓 Key Insights

### **Adaptive Thresholds**
- **Math**: 55% Module 1 performance threshold
- **Reading & Writing**: 60% Module 1 performance threshold
- Different subjects require different thresholds for optimal routing

### **Complexity Strategy**
- **Easy questions first**: Same points, less effort (highest efficiency)
- **Medium questions second**: Balanced difficulty/reward ratio
- **Hard questions last**: Lowest efficiency, save for final push

### **Module Priority**
- **Module 1 questions**: Can change adaptive path (+120 point bonus)
- **Module 2 questions**: Direct score impact only
- Strategic focus on Module 1 for maximum adaptive leverage

## 📁 Clean Directory Structure

```
├── threshold_tuner.py     # 🎯 Core threshold optimization
├── whatif.py             # 📊 Strategic analysis engine  
├── app.py                # 🌐 Web dashboard backend
├── templates/
│   └── dashboard.html    # 💻 Interactive web interface
├── Data/
│   ├── stu1.json        # 📋 Student responses
│   └── scoring_DSAT_v2.json # 📈 SAT scoring maps
├── requirements.txt      # 📦 Python dependencies
└── README.md            # 📖 This documentation
```

## 💡 System Benefits

1. **Precision**: Subject-specific threshold optimization with 100% prediction accuracy
2. **Efficiency**: Complexity-based question prioritization for maximum ROI
3. **Adaptability**: Dynamic routing analysis for optimal difficulty progression  
4. **Usability**: Clean terminal output + interactive web dashboard
5. **Actionability**: Specific question IDs with strategic recommendations

**Result**: Transform SAT preparation from guesswork into data-driven strategy! 🎯📈
