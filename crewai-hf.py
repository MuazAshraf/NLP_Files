from flask import Flask, request, jsonify
import requests
from crewai import Agent, Task, Crew, Process
from langchain_community.llms import HuggingFaceHub

app = Flask(__name__)

#<------------------Crew AI------------------------>
llm_yi = HuggingFaceHub(
    repo_id="01-ai/Yi-1.5-34B-Chat",
    huggingfacehub_api_token="hf_key",
    task="text-generation",
    max_new_tokens=2048
)
@app.route('/execute-tasks', methods=['POST'])
def execute_tasks():
    data = request.json
    
    if not data:
        return jsonify({"error": "Invalid or missing JSON data"}), 400

    try:
        # Create Agent objects
        agents = []
        for i in range(1, 4):
            role_key = f'role{i}'
            goal_key = f'goal{i}'
            backstory_key = f'backstory{i}'
            
            role = data.get(role_key)
            goal = data.get(goal_key)
            backstory = data.get(backstory_key)

            if not role or not goal or not backstory:
                return jsonify({"error": f"Missing role, goal, or backstory for agent {i}"}), 400

            agent = Agent(
                role=role,
                goal=goal,
                backstory=backstory,
                verbose=True,
                allow_delegation=False,
                llm=llm_yi
            )
            agents.append(agent)

        # Create Task objects
        tasks = []
        for i in range(1, 4):
            task_desc_key = f'task{i}_description'
            task_output_key = f'task{i}_expected_output'

            description = data.get(task_desc_key)
            expected_output = data.get(task_output_key)

            if not description or not expected_output:
                return jsonify({"error": f"Missing description or expected output for task {i}"}), 400

            task = Task(
                description=description,
                agent=agents[i-1],
                expected_output=expected_output
            )
            tasks.append(task)

        # Instantiate your crew with a sequential process
        crew = Crew(agents=agents, tasks=tasks, verbose=2, process=Process.sequential)

        # Get your crew to work!
        result = crew.kickoff()

        return jsonify({"result": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# @app.route('/execute-tasks', methods=['POST'])
# def execute_tasks():
#     data = request.json
    
#     if not data:
#         return jsonify({"error": "Invalid or missing JSON data"}), 400

#     try:
#         # Capture form data
#         role1 = data['role1']
#         goal1 = data['goal1']
#         backstory1 = data['backstory1']
        
#         role2 = data['role2']
#         goal2 = data['goal2']
#         backstory2 = data['backstory2']

#         role3 = data['role3']
#         goal3 = data['goal3']
#         backstory3 = data['backstory3']
        
#         task1_description = data['task1_description']
#         task1_expected_output = data['task1_expected_output']
#         task2_description = data['task2_description']
#         task2_expected_output = data['task2_expected_output']
#         task3_description = data['task3_description']
#         task3_expected_output = data['task3_expected_output']

#         # Create Agent and Task objects dynamically
#         agent1 = Agent(role=role1, goal=goal1, backstory=backstory1, verbose=True, allow_delegation=False, llm=llm_yi)
#         agent2 = Agent(role=role2, goal=goal2, backstory=backstory2, verbose=True, allow_delegation=False, llm=llm_yi)
#         agent3 = Agent(role=role3, goal=goal3, backstory=backstory3, verbose=True, allow_delegation=False, llm=llm_yi)

#         task1 = Task(description=task1_description, agent=agent1, expected_output=task1_expected_output)
#         task2 = Task(description=task2_description, agent=agent2, expected_output=task2_expected_output)
#         task3 = Task(description=task3_description, agent=agent3, expected_output=task3_expected_output)

#         # Instantiate your crew with a sequential process
#         crew = Crew(agents=[agent1, agent2, agent3], tasks=[task1, task2,task3], verbose=2, process=Process.sequential)

#         # Get your crew to work!
#         result = crew.kickoff()

#         return jsonify({"result": result})
    
#     except KeyError as e:
#         return jsonify({"error": f"Missing key in JSON data: {str(e)}"}), 400
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
