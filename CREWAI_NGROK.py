import subprocess
import threading
import time
from flask import Flask, request, jsonify
from crewai import Agent, Task, LLM, Crew, Process

def start_ngrok():
    subprocess.Popen(["ngrok", "http", "5000"])
    time.sleep(3)
    try:
        import requests
        tunnels = requests.get("http://localhost:4040/api/tunnels").json()
        print("\nNGROK PUBLIC URL:", tunnels["tunnels"][0]["public_url"], "\n")
    except Exception:
        pass

threading.Thread(target=start_ngrok, daemon=True).start()

llm_local = LLM(
    model="llama3",
    api_base="http://localhost:11434/v1",
    api_key="ollama"
)

emprendedor = Agent(
    role="Emprendedor",
    goal="Presentar una idea convincente.",
    backstory="Innovador buscando inversión.",
    llm=llm_local
)

juez_1 = Agent(
    role="Juez Conservador",
    goal="Evaluar riesgos financieros.",
    backstory="Cauteloso con inversiones.",
    llm=llm_local
)

juez_2 = Agent(
    role="Juez Visionario",
    goal="Evaluar innovación.",
    backstory="Busca ideas disruptivas.",
    llm=llm_local
)

pitch = Task(
    description="El emprendedor presenta la idea: {{idea}}",
    expected_output="Pitch claro.",
    agent=emprendedor
)

evaluacion_1 = Task(
    description="El juez conservador analiza la idea.",
    expected_output="Evaluación del riesgo.",
    agent=juez_1
)

evaluacion_2 = Task(
    description="El juez visionario analiza la innovación.",
    expected_output="Evaluación creativa.",
    agent=juez_2
)

crew = Crew(
    agents=[emprendedor, juez_1, juez_2],
    tasks=[pitch, evaluacion_1, evaluacion_2],
    process=Process.sequential
)

app = Flask(__name__)

@app.route("/")
def home():
    return "Sistema Multiagente funcionando. Usa /simulacion por GET o POST."

@app.route("/simulacion", methods=["GET", "POST"])
def simulacion():
    if request.method == "GET":
        idea = request.args.get("idea", "Sin idea por GET")
    else:
        data = request.json
        idea = data.get("idea", "Sin idea por POST")

    try:
        resultado = crew.kickoff(inputs={"idea": idea})
        return jsonify({"idea": idea, "resultado": str(resultado)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=False)
