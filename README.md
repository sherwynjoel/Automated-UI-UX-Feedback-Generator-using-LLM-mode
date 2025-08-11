feedback-generator/
│── feedback_generator_app.py        # Main app entry point (Gradio UI)
│── feedback_generator_model.py      # Loads & runs LLM
│── feedback_generator_inference.py  # Handles predictions
│── feedback_generator_heuristics.py # UI/UX heuristics checks
│── feedback_generator_utils.py      # Helper functions
│── config.yaml                       # App configuration
│── models/                           # LLM model files (.gguf)
│── outputs/                          # Generated reports/screenshots
│── tests/                            # Unit tests
│── requirements.txt                  # Python dependencies
│── README.md                         # Project documentation

Clone the repository
git clone https://github.com/sherwynjoel/Automated-UI-UX-Feedback-Generator-using-LLM-mode.git
cd Automated-UI-UX-Feedback-Generator-using-LLM-mode

Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # For Mac/Linux
.venv\Scripts\activate      # For Windows

 Install dependencies
 pip install -r requirements.txt

 Download the BakLLaVA model
 models/bakllava.Q4_K_M.gguf

 Run the app
 python feedback_generator_app.py





