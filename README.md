# Vision-based Workout Technique Assessment
The Vision-Based Workout Technique Assessment project aims to enhance the UrTraining platform by integrating technologies to evaluate and correct users’ exercise techniques in real-time. By leveraging pose estimation algorithms and ML models, this feature will provide users with feedback on their form, promoting safer and more effective workouts

## 1. Team  

| Team Member | Role | Telegram |
|--------------|------|-----------|
| **Ildar Rakiev (Lead)** | Pipeline & Visualization | [@mescudiway](https://t.me/mescudiway) |
| **Ilona Dziurava** | ML Model & Documentation | [@a_b_r_i_c_o_s](https://t.me/a_b_r_i_c_o_s) |
| **Anisya Kochetkova** | Pose Estimation & Data Processing | [@anis1305](https://t.me/anis1305) |

---

## 2. Project Idea  

The **Vision-Based Workout Technique Assessment** project enhances our existing **UrTraining** platform by integrating a computer vision module capable of evaluating and correcting users’ exercise techniques in real time.  

By leveraging pose estimation algorithms and machine learning models, this feature aims to:  
- 🧠 **Provide real-time feedback** on posture and movement quality;  
- 📊 **Analyze performance** via joint angles and motion dynamics;  
- 💪 **Deliver personalized recommendations** to improve technique and reduce injury risk.   

---

## 3. Techniques & Methods  

Vision-based exercise assessment combines pose estimation and classification of motion correctness.  
Our approach builds on prior work (Pose Trainer [1], Physics-informed Motion Models [2], and GCN-based posture learning [4]) while focusing on efficient real-time assessment using MediaPipe and SVM models.

### 3.1 Pose Estimation  
Human poses are extracted using **MediaPipe Pose**, which provides 33 2D/3D landmarks.  
These serve as inputs for subsequent analysis, reducing data dimensionality while retaining biomechanical relevance.

### 3.2 CV Pipeline  
1. Capture input from a camera or video stream;  
2. Detect and track human body poses;  
3. Extract pose landmarks using MediaPipe;  
4. Compute engineered features (angles, distances, dynamics);  
5. Pass features into a classification model (rule-based model + autoencoder);  
6. Provide visual and textual feedback.

### 3.3 Feature Representation  
- Joint angles (e.g., hip–knee–ankle, shoulder–elbow–wrist)  
- Spatial relationships (normalized distances, ratios)  
- Temporal dynamics (angle variation and velocity across frames)
- Frame details and information about peak phases

### 3.4 Model  
We employ an **autoencoder** architecture that takes a set of exercise feature vectors and evaluate anomalies based on recovery errors. That is, autoencoder tries to understand the "normal" examples of exercises, so that later it can detect some irrelevant features data. 

**Encoder** compresses the source data into a small vector (8 features) — a "bottleneck" of the network, where it is forced to present all information compactly in vector. The second step is when the decoder restores the vector to its original size.

- Here we have the loss as **MSE (RMS error)** between input and output as the key metric to understand whether the features are valid.

The idea of the autoencoder is to learn how to "reproduce normal data." If the data is **abnormal**, the autoencoder will not recover it well, and the MSE will be **high**.

### 3.5 Evaluation Metrics  
- **Accuracy:** Overall correctness  
- **Precision & Recall:** Detection quality for specific errors  
- **F1-score:** Balance between precision and recall  
- **Confusion Matrix:** Identifies frequent misclassifications  
> 🎯 Expected outcome: *F1-score ≥ 0.80* for baseline exercises (squats, push-ups)

### 3.6 Feedback & Visualization  
- **Real-time skeleton overlay** with highlighted incorrect joints  
- **Text-based hints:** e.g., “Straighten your back” or “Bend deeper at the knees”  
- **Post-session summary:** accuracy percentage, repetition count, and improvement tips  

### 3.7 Technical Stack  
| Component | Tools |
|------------|-------|
| Pose Estimation | MediaPipe, OpenCV |
| Machine Learning | Scikit-learn (SVM) |
| Data Processing | NumPy, Pandas |
| Visualization | OpenCV, Matplotlib, Plotly |
| Integration | FastAPI (microservice for UrTraining) |

---

## 4. Dataset  

**Dataset:** [DynTherapy: Physical Therapy Exercises Dataset](https://data.mendeley.com/datasets/hghdm99rwg/1)
This dataset contains 33 pose keypoints extracted via MediaPipe across multiple physical therapy exercises.  
Each exercise includes multiple repetitions under varying conditions and is segmented into *Start* and *End* positions for improved temporal modeling.

---

## 5. Installation & Usage  

### Requirements
- Python 3.9+  
- pip, virtualenv  

### Local Setup & Run Instructions

#### 1. Clone the repository

```bash
git clone https://github.com/IldarRakiev/Workout-Technique-Assessment.git
cd Workout-Technique-Assessment
```

#### 2. Backend Setup (FastAPI)
```bash
cd backend
python -m venv venv
source venv/bin/activate     # or .\venv\Scripts\activate on Windows
docker-compose build
docker-compose up -d
```

Server will be accessible at **port 8000**.

### 3. Frontend Setup (React + Tailwind)
```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at **port 5173**.

### Example Usage

**Upload a video** via the frontend.
The model will:

- Extract **pose keypoints** using MediaPipe
- Analyze **motion features**
- Output correctness evaluation and **feedback visualization**
source venv/bin/activate  # (on Windows: venv\Scripts\activate)
pip install -r requirements.txt
