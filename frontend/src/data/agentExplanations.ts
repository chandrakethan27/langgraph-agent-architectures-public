export interface AgentExplanation {
  id: string;
  title: string;
  badge: string;
  whatItIs: string;
  analogy: string;
  howItWorks: string;
  whenToUse: string;
  keyConcepts: string[];
}

export const AGENT_EXPLANATIONS: Record<string, AgentExplanation> = {
  module_01: {
    id: "module_01",
    title: "Sequential Prompt Chaining",
    badge: "Linear Graph",
    whatItIs: "A straight, assembly-line workflow where the output of one LLM node is passed directly as the input to the next node.",
    analogy: "Writing a book with two authors: Author 1 writes the outline, and Author 2 takes that outline to write the complete chapter.",
    howItWorks: "State flows linearly along fixed edges: START ➔ generate_outline ➔ write_content ➔ END. Each node updates keys in the shared State.",
    whenToUse: "Multi-stage generative tasks that are too big for a single prompt, such as drafting articles, summarizing and polishing reports, or generating code from specifications.",
    keyConcepts: ["StateGraph", "START / END", "Sequential Edges", "State Schema"]
  },
  module_02: {
    id: "module_02",
    title: "Dynamic Intent Routing",
    badge: "Conditional Edges",
    whatItIs: "An intelligent classifier evaluates the user's input and dynamically routes the request to a dedicated expert agent.",
    analogy: "A hospital reception triage: You explain your symptoms, and the nurse routes you to Cardiology, Orthopedics, or General Medicine.",
    howItWorks: "Classifier node inspects prompt intent ➔ conditional edge branch ➔ Math Expert, Code Expert, or General Assistant ➔ END.",
    whenToUse: "Multi-functional chatbots, customer support desks, and enterprise assistants where different questions require completely different instructions or tools.",
    keyConcepts: ["Conditional Edges", "Intent Classification", "Specialized Nodes", "Dynamic Branching"]
  },
  module_03: {
    id: "module_03",
    title: "ReAct Agent (Reasoning + Action)",
    badge: "Cyclic Tool Loop",
    whatItIs: "An autonomous agent that iterates through a loop: it thinks about the problem, calls external tools (calculator, web search, database), observes the results, and repeats until solved.",
    analogy: "A detective solving a mystery: 'I need to check the suspect's alibi. Let me search the records. Now that I see the flight logs, I can formulate my final conclusion.'",
    howItWorks: "Cyclic graph: Agent Node ➔ checks if tools are needed ➔ calls ToolNode ➔ feeds observation back into Agent Node ➔ terminates at END when final answer is ready.",
    whenToUse: "Live data lookups, calculations, interacting with APIs, web browsing, or any task requiring external facts beyond the LLM's training cutoff.",
    keyConcepts: ["Tool Binding", "ToolNode", "Cyclic Feedback Loops", "add_messages Reducer"]
  },
  module_03b: {
    id: "module_03b",
    title: "Plan-and-Execute Architecture",
    badge: "Replanning Cycle",
    whatItIs: "Rather than jumping into action immediately, the agent creates a structured multi-step plan, executes one step at a time, and dynamically replans after each step.",
    analogy: "A GPS navigation app during rush hour: It calculates the initial route. If an unexpected roadblock happens on step 2, it re-routes the remaining journey.",
    howItWorks: "Planner Node creates a numbered plan ➔ Executor Node runs current step ➔ Replanner Node evaluates progress and updates the plan ➔ loops until all tasks are marked done.",
    whenToUse: "Complex multi-step research, codebase refactoring, migrations, and long-horizon tasks where standard agents lose track of the overall goal.",
    keyConcepts: ["Explicit Planning", "Dynamic Replanning", "Task State Tracking", "Cyclic Termination"]
  },
  module_04: {
    id: "module_04",
    title: "Memory Architecture (Short-Term vs. Long-Term)",
    badge: "State Persistence",
    whatItIs: "Combines short-term memory (remembering the ongoing conversation in the current thread) with cross-thread long-term memory (remembering user preferences and facts across sessions).",
    analogy: "Your personal doctor: Remembers what you said 5 minutes ago in today's visit (Short-term) AND remembers your chronic allergies from two years ago (Long-term).",
    howItWorks: "Checkpointer persists conversation state by thread_id. In parallel, a long-term user store retrieves and saves cross-thread user facts, injecting them into the prompt.",
    whenToUse: "Personalized AI companions, customer CRM agents, and ongoing assistance where user facts must survive across new conversations.",
    keyConcepts: ["Thread Checkpointing", "Cross-Thread Store", "User Profiles", "MemorySaver"]
  },
  module_05: {
    id: "module_05",
    title: "Human-in-the-Loop (HITL) & Breakpoints",
    badge: "Safety Guardrail",
    whatItIs: "Automatically pauses the agent right before executing dangerous, high-risk, or irreversible actions, allowing a human operator to review, approve, or reject it.",
    analogy: "Two-factor authorization for bank wire transfers: The system prepares a $10,000 transfer, pauses, and requires your explicit approval before releasing the money.",
    howItWorks: "Compiled with interrupt_before=['dangerous_action_node']. The graph state freezes at the breakpoint until an external approval payload resumes execution.",
    whenToUse: "Database deletions (`DROP TABLE`), financial transactions, sending outgoing emails/SMS to customers, or deploying code to production.",
    keyConcepts: ["interrupt_before", "State Freezing", "Human Authorization", "Safe Resumption"]
  },
  module_06: {
    id: "module_06",
    title: "Time-Travel & State Rewinding",
    badge: "Checkpoint Branching",
    whatItIs: "Allows inspecting the agent's full historical state timeline, rewinding back to an earlier checkpoint, modifying a variable, and branching execution down an alternative path.",
    analogy: "Rewinding a video game to an earlier save point before making a fatal mistake, and choosing a different path to win.",
    howItWorks: "LangGraph checkpointer writes a state snapshot at each node. graph.get_state_history(config) lets you browse past states and re-invoke from any prior checkpoint_id.",
    whenToUse: "Debugging agent logic, A/B testing different prompts from the exact same intermediate state, and building Undo/Redo features in AI applications.",
    keyConcepts: ["Checkpoint History", "State Rewind", "State Branching", "Replay Execution"]
  },
  module_07: {
    id: "module_07",
    title: "Hierarchical Multi-Agent Team (Supervisor)",
    badge: "Multi-Agent System",
    whatItIs: "A team of specialized agents coordinated by a Manager/Supervisor agent that breaks down tasks, assigns work to specialists (Researcher, Coder), and reviews the final output.",
    analogy: "A software engineering agency: The Project Manager takes the client request, instructs the Researcher to find specs, directs the Coder to implement it, reviews quality, and delivers.",
    howItWorks: "Supervisor Node evaluates state ➔ delegates to Researcher ➔ returns to Supervisor ➔ delegates to Coder ➔ returns to Supervisor ➔ signals FINISH.",
    whenToUse: "Complex collaborative workflows where specialized prompts and distinct personas deliver vastly superior results compared to a single monolithic prompt.",
    keyConcepts: ["Supervisor Pattern", "Worker Delegation", "Role Specialization", "Multi-Agent State"]
  },
  module_08: {
    id: "module_08",
    title: "Deep Agents & Nested Sub-Graphs",
    badge: "Modular Sub-Graphs",
    whatItIs: "Embedding an entirely compiled sub-graph inside a single node of a parent graph. The parent sees the sub-agent as a single black-box step.",
    analogy: "A corporate department: The Marketing Department has its own internal workflows, review stages, and meetings. The CEO just requests a 'campaign' and receives the completed deliverable.",
    howItWorks: "A parent node invokes a compiled child StateGraph with its own independent State schema, nodes, and edges, then maps the result back to the parent state.",
    whenToUse: "Enterprise-grade agent platforms where independent engineering teams build and maintain distinct sub-agents without polluting the main graph's state.",
    keyConcepts: ["Nested Graphs", "Sub-Agent Encapsulation", "State Mapping", "Modular Architecture"]
  },
  module_09: {
    id: "module_09",
    title: "Reflection & Self-Correction",
    badge: "Critique-Refine Loop",
    whatItIs: "An agent produces a draft, passes it to an internal Critic/Evaluator agent that tests and grades it, and if flaws are found, loops back to rewrite and self-correct.",
    analogy: "An author working with an editor: The author drafts a chapter, the editor highlights mistakes and weak points, and the author revises until approved for publication.",
    howItWorks: "Generator Node drafts content ➔ Evaluator Node checks against strict rubrics ➔ conditional edge: if rejected, loops back to Generator with critique; if passed, finishes.",
    whenToUse: "Code generation (running self-tests to fix syntax errors), adhering to strict regulatory constraints, and high-precision technical writing.",
    keyConcepts: ["Generator-Critic Loop", "Self-Correction", "Automated Feedback", "Iterative Refinement"]
  },
  module_09b: {
    id: "module_09b",
    title: "Parallel Map-Reduce (Fan-Out / Fan-In)",
    badge: "Concurrent Execution",
    whatItIs: "Splits a large input into chunks, processes all chunks simultaneously using parallel worker nodes (Fan-Out), and synthesizes all results into a unified summary (Reduce).",
    analogy: "Summarizing a 300-page book: Worker 1 reads Part 1, Worker 2 reads Part 2, and Worker 3 reads Part 3 simultaneously. The Editor combines all 3 summaries into one executive brief.",
    howItWorks: "Fan-Out node branches into multiple parallel edges to concurrent workers. State uses Annotated[List[str], operator.add] to cleanly merge simultaneous worker outputs into Reduce node.",
    whenToUse: "High-throughput document summarization, batch data processing, analyzing multiple documents at once, and speeding up independent processing jobs.",
    keyConcepts: ["Fan-Out / Fan-In", "Parallel Edges", "Concurrent State Reducers", "operator.add"]
  },
  module_10: {
    id: "module_10",
    title: "Observability & LLM-as-a-Judge Evaluation",
    badge: "Automated QA",
    whatItIs: "An automated evaluation pipeline where an impartial LLM grades an agent's outputs against benchmark test datasets, scoring accuracy and explaining failures.",
    analogy: "A teacher grading student exams: Compares each answer against the benchmark answer key, assigns a score from 0-100, and writes diagnostic feedback.",
    howItWorks: "Iterates through test cases, invokes agent, prompts an LLM Judge with grading rubrics, aggregates accuracy scores, and logs execution traces directly to LangSmith.",
    whenToUse: "CI/CD testing for AI agents, prompt regression testing when changing models, and quantitative quality assurance before launching to production.",
    keyConcepts: ["LLM-as-a-Judge", "Benchmark Datasets", "LangSmith Tracing", "Quantitative Metrics"]
  },
  module_11: {
    id: "module_11",
    title: "Real-Time Streaming Architecture",
    badge: "Low-Latency Stream",
    whatItIs: "Streams partial outputs, token deltas, and intermediate node events in real time so users don't have to wait for the entire multi-step graph to finish.",
    analogy: "Live television broadcast vs. waiting for a DVD to be pressed, packaged, and shipped to your house.",
    howItWorks: "Uses LangGraph's .stream() API to emit token-by-token generation deltas and node state transitions as they occur in real time.",
    whenToUse: "Interactive conversational agents, user-facing search tools, and any interface where low perceived latency and responsiveness are essential.",
    keyConcepts: [".stream() Mode", "Token Streaming", "Event Dispatching", "Interactive UI"]
  },
  module_12: {
    id: "module_12",
    title: "Context & Dynamic Dependency Injection",
    badge: "Runtime Configuration",
    whatItIs: "Injects external configurations, tenant IDs, database connection strings, and feature toggles into nodes at runtime without modifying the graph's state schema.",
    analogy: "A hotel keycard: The hotel room and elevator remain identical, but your keycard dynamically grants access to your specific floor and room number.",
    howItWorks: "Passes RunnableConfig with configurable dictionary into graph.invoke(). Nodes read tenant credentials and database URLs directly from the injected config.",
    whenToUse: "Multi-tenant SaaS architectures, enterprise applications with row-level tenant security, and seamlessly switching between staging and production environments.",
    keyConcepts: ["RunnableConfig", "Dependency Injection", "Multi-Tenant Isolation", "Configurable Parameters"]
  }
};
