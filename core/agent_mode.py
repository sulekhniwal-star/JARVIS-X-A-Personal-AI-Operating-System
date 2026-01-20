from core.gemini_llm import GeminiLLM
from core.self_coder import SelfCoder
from skills.web_search import search_web
from skills.system_control import open_app


class AgentMode:
    def __init__(self, tts, memory, persistent_memory):
        self.llm = GeminiLLM()
        self.self_coder = SelfCoder()
        self.tts = tts
        self.memory = memory
        self.persistent_memory = persistent_memory
    
    def run_task(self, goal: str):
        """Execute a multi-step autonomous task to achieve the given goal."""
        try:
            self.tts.speak(f"Starting autonomous agent mode for: {goal}")
            
            reasoning_trace = [f"Goal: {goal}"]
            step_count = 0
            max_steps = 5
            
            while step_count < max_steps:
                step_count += 1
                
                # Ask Gemini to decide next action
                context = "\n".join(reasoning_trace[-3:])  # Last 3 steps for context
                decision_prompt = f"""You are an autonomous AI agent.
Goal: {goal}
Previous actions: {context}
Decide the next best action to achieve the goal.
Respond with one of:
- SEARCH: <query>
- CODE: <task>
- OPEN: <app>
- COMPLETE: <summary>"""
                
                decision = self.llm.generate_reply(decision_prompt, "")
                reasoning_trace.append(f"Step {step_count} Decision: {decision}")
                
                self.tts.speak(f"Step {step_count}: {decision.split(':', 1)[0] if ':' in decision else decision}")
                
                # Execute the decided action
                if decision.startswith("SEARCH:"):
                    query = decision.split("SEARCH:", 1)[1].strip()
                    result = search_web(query)
                    reasoning_trace.append(f"Search result: {result[:200]}...")
                    
                elif decision.startswith("CODE:"):
                    task = decision.split("CODE:", 1)[1].strip()
                    result = self.self_coder.generate_code(task)
                    reasoning_trace.append(f"Code generated for: {task}")
                    
                elif decision.startswith("OPEN:"):
                    app = decision.split("OPEN:", 1)[1].strip()
                    result = open_app(app)
                    reasoning_trace.append(f"Opened: {app}")
                    
                elif decision.startswith("COMPLETE:"):
                    summary = decision.split("COMPLETE:", 1)[1].strip()
                    reasoning_trace.append(f"Task completed: {summary}")
                    self.tts.speak(f"Task completed: {summary}")
                    break
                    
                else:
                    # Fallback - treat as general reasoning
                    reasoning_trace.append(f"Reasoning: {decision}")
                
                # Save progress
                self.memory.add(f"Agent Step {step_count}", decision)
                self.persistent_memory.save(f"Agent Step {step_count}", decision)
                
                self.tts.speak("Step completed.")
            
            # Save full reasoning trace
            full_trace = "\n".join(reasoning_trace)
            self.memory.add("Agent Reasoning Trace", full_trace)
            self.persistent_memory.save("Agent Reasoning Trace", full_trace)
            
            if step_count >= max_steps:
                self.tts.speak("Maximum steps reached. Task may need manual completion.")
            
        except Exception as e:
            self.tts.speak("I encountered an error during autonomous execution.")