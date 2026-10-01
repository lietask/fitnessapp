# Gym Tracker

Gym Tracker is a centralized fitness analytics, nutrition monitoring, and sleep tracking web application. Built on Streamlit and backed by Supabase PostgreSQL, the platform provides automated set synchronization, progressive overload telemetry, algorithmic load suggestions, and workout consistency visualization.

---

## Architecture and Core Capabilities

### Workout Logging and History
* **Set Synchronization Engine**: Allows logging between 1 and 8 sets per exercise. Updating the primary set (Set 1) automatically synchronizes load and repetition fields across all subsequent sets.
* **Rapid Form Submission**: Supports hotkey form submission (`Cmd + Enter` / `Ctrl + Enter`) via client-side DOM event listeners.
* **Historical Audit and Filtering**: Multi-parameter query interface supporting filtering across usernames, exercise classifications, and date ranges.

### Health Telemetry: Nutrition and Sleep
* **Macronutrient Tracking**: Records daily caloric intake alongside macronutrient breakdowns (protein, carbohydrates, and dietary fats).
* **Sleep Architecture Logging**: Captures total time asleep, awake periods, sleep stage distribution (REM, Core, Deep), and composite sleep quality scores.
* **Idempotent Storage**: Implements composite unique key constraints (`date, user_name`) with database-level upserts to prevent duplicate daily telemetry.

### Analytics and Load Prescriptions
* **Estimated One-Rep Max (e1RM)**: Uses empirical strength formulations to calculate maximum single-repetition capacity from multi-rep historical data.
* **Load Prescriptions**: Derives target working weights based on rolling five-session average e1RM for hypertrophy (8 reps), maximal strength (4 reps), or customized rep goals.
* **Progressive Overload Telemetry**: Time-series charts visualizing volume and e1RM trajectory per exercise.
* **Calendar Consistency Matrix**: Year-long contribution matrix displaying workout frequency and scheduling consistency.

### Data Layer Resilience
* **Transient Fault Recovery**: Built-in exception handling that detects connection interruptions, network timeouts, and protocol errors, automatically re-establishing the database client session.

---

## Technical Specifications

| Category | Component / Tool |
| :--- | :--- |
| **Application Framework** | Streamlit |
| **Database** | PostgreSQL via Supabase |
| **Scientific Computing** | NumPy, Pandas |
| **Data Visualization** | Matplotlib |
| **Interface Styling** | Custom CSS, CSS Grid/Flexbox, JavaScript injections |
| **Runtime Environment** | Python 3.9+ |

---

## Repository Structure

```text
fitnessapp/
├── main.py                 # Application entrypoint, session routing, and authentication
├── style.css               # Application stylesheet and typography definitions
├── requirements.txt        # Runtime dependency manifest
├── services/
│   └── db_service.py       # Supabase client management, query operations, and retry logic
└── views/
    ├── workout_view.py     # Workout capture forms and history query interface
    ├── nutrition_view.py   # Nutrition and sleep metrics management
    └── analytics_view.py   # Statistical modeling, load suggestions, and visualizations
