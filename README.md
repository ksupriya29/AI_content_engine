# 🤖 AI Content Engine

An AI-powered content generation platform built using **Python, Streamlit, OpenAI API, and OpenRouter API**.

AI Content Engine allows users to generate high-quality **text, images, and videos** using advanced Artificial Intelligence models. The application provides a simple interface to interact with multiple AI generation capabilities.

---

## 🚀 Features

### ✍️ AI Text Generation
- Generate creative and professional content
- Create summaries, articles, and responses
- Uses powerful Large Language Models (LLMs)

### 🖼️ AI Image Generation
- Generate images from text prompts
- Convert ideas into AI-generated visuals

### 🎬 AI Video Generation
- Generate AI-based video content
- Supports creative video generation workflows

### 🤖 Multi-Model AI Support
- Integration with OpenAI API
- Integration with OpenRouter API
- Flexible AI model usage

### 🔐 Secure API Management
- API keys stored using `.env`
- Sensitive credentials excluded from GitHub

---

# 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Backend development |
| Streamlit | Web application framework |
| OpenAI API | AI content generation |
| OpenRouter API | Multi-model AI access |
| python-dotenv | Environment management |

---

# 📂 Project Structure

```
AI_content_engine/
│
├── content_engine/
│   ├── app.py
│   ├── config.py
│   ├── text_gen.py
│   ├── image_gen.py
│   ├── video_gen.py
│   ├── requirements.txt
│   └── .env
│
├── README.md
├── .gitignore
└── streamlit_output.txt
```

---

# ⚙️ Installation & Setup

## 1. Clone Repository

```bash
git clone https://github.com/ksupriya29/AI_content_engine.git
```

## 2. Navigate to Project

```bash
cd AI_content_engine/content_engine
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 Environment Setup

Create a `.env` file inside the `content_engine` folder.

Add your API keys:

```env
OPENAI_API_KEY=your_openai_api_key
OPENROUTER_API_KEY=your_openrouter_api_key
```

⚠️ Never upload `.env` files or API keys to GitHub.

---

# ▶️ Run Application

Start the Streamlit application:

```bash
streamlit run app.py
```

The application will open at:

```
http://localhost:8501
```

---

# 📸 Screenshots

Add application screenshots here:

Example:

```markdown
![AI Content Engine Screenshot](images/demo.png)
```

---

# 🎯 Future Enhancements

- Add more AI models
- Add user authentication
- Store generated content history
- Deploy on cloud platforms
- Improve prompt optimization
- Add advanced AI workflows

---

# 👩‍💻 Author

**Supriya Kosgi**

GitHub:
https://github.com/ksupriya29

---

⭐ If you find this project useful, consider giving it a star!