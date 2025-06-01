# 🧠 AI-Powered Meeting Summarizer

An interactive web application that transcribes audio recordings, generates concise summaries, extracts key terms, and collects user feedback — all powered by modern AI models.

## 🚀 Features

- 🎙️ Upload audio files (`.mp3`, `.wav`, `.m4a`)
- 📝 Transcription using [Whisper ASR](https://github.com/openai/whisper) by OpenAI
- 🔍 Keyword extraction using TF-IDF (from `scikit-learn`)
- 📊 Feedback submission stored in downloadable `.csv` format

---

## 🛠️ Technologies Used

| Component         | Purpose                                      |
|------------------|----------------------------------------------|
| Whisper (Base)   | Audio transcription                          |
| Scikit-learn     | TF-IDF keyword extraction                    |
| Pandas           | Feedback storage & CSV export                |
| Numpy, OS        | Utility functions & temporary file handling  |

---

## 📂 Project Workflow

1. User uploads an audio file.
2. Whisper transcribes audio into plain text.
3. BART model summarizes the text.
4. TF-IDF extracts and ranks keywords.
5. Fixed speaker ID displayed (placeholder).
6. User submits feedback.
7. Feedback is saved and can be downloaded as `.csv`.

---

## 💡 How to Run Locally

1. **Clone this repo:**

   bash
   git clone https://github.com/your-username/ai-meeting-summarizer.git
   cd ai-meeting-summarizer

2. **Create a virtual environment (optional but recommended):**

   bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows


3. **Install dependencies:**

   bash
   pip install -r requirements.txt

4. **Launch the app:**

   bash
   streamlit run app.py
   
## 📁 File Structure


├── app.py                   # Main Streamlit app
├── uploads                  # Stores audio files
├── requirements.txt         # Python dependencies
├── README.md                # Project documentation

## 🧪 Sample Models Used

* Whisper: `whisper.load_model("base")`

---

## 🧾 License

This project is open-source and available under the [MIT License](LICENSE).

---

## 🙌 Acknowledgements

* [OpenAI Whisper](https://github.com/openai/whisper)
