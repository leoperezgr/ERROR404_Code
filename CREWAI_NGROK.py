import subprocess
import threading
import time
from flask import Flask, request, jsonify
from crewai import Agent, Task, Crew, Process
from crewai.llm import MockLLM

# ---------------- NGROK ------------------

def start_ngrok():
    subprocess.Popen(["ngrok", "http", "5000"])
    time.sleep(3)
    try:
        import requests
        tunnels = requests.get("http://localhost:4040/api/tunnels").json()
        print("\n🔗 NGROK URL:", tunnels['tunnels'][0]['public_url'])
    except:
        print("No se pudo obtener la URL pública de ngrok.")

threading.Thread(target=start_ngrok, daemon=True).start()

# ---------------- LLM OFFLINE ------------------

llm_local = MockLLM()   # <--- NO usa OpenAI, NO usa Ollama

# ---------------- CREWAI ------------------

emprendedor = Agent(
    role="Emprendedor",
    goal="Presentar una propuesta.",
    backstory="Un pitch sencillo.",
    llm=llm_local
)

juez = Agent(
    role="Juez",
    goal="Evaluar la propuesta.",
    backstory="Da retroalimentación básica.",
    llm=llm_local
)

pitch = Task(
    description="El emprendedor presenta su idea.",
    expected_output="Un pitch muy simple.",
    agent=emprendedor
)

evaluacion = Task(
    description="El juez responde al pitch.",
    expected_output="Retro breve.",
    agent=juez
)

crew = Crew(
    agents=[emprendedor, juez],
    tasks=[pitch, evaluacion],
    process=Process.sequential
)

# ---------------- API ------------------

app = Flask(__name__)

@app.route("/simulacion", methods=["POST"])
def simulacion():
    data = request.json
    idea = data.get("idea", "Sin idea")

    result = crew.kickoff(inputs={"input": idea})
    return jsonify({"resultado": str(result)})

@app.route("/")
def home():
    return "API de CrewAI funcionando."

# ---------------- RUN ------------------

if __name__ == "__main__":
    app.run(port=5000, debug=False)
