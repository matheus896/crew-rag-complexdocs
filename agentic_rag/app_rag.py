import streamlit as st
import os
import tempfile
import gc
import base64
import time

from crewai import Agent, Crew, Process, Task, LLM
from crewai_tools import SerperDevTool
from src.agentic_rag.tools.custom_tool import DocumentSearchTool

@st.cache_resource
def load_llm():
    llm = LLM(model="gemini/gemini-2.0-flash")
    return llm

# ===========================
#   Define Agents & Tasks
# ===========================
def create_agents_and_tasks(pdf_tool):
    """Creates a Crew with the given PDF tool (if any) and a web search tool."""
    web_search_tool = SerperDevTool()

    retriever_agent = Agent(
        role="Retrieve relevant information to answer the user query: {query}",
        goal=(
            "Retrieve the most relevant information from the available sources "
            "for the user query: {query}. Always try to use the PDF search tool first. "
            "If you are not able to retrieve the information from the PDF search tool, "
            "then try to use the web search tool."
        ),
        backstory=(
            "You're a meticulous analyst with a keen eye for detail. "
            "You're known for your ability to understand user queries: {query} "
            "and retrieve knowledge from the most suitable knowledge base."
        ),
        verbose=True,
        tools=[t for t in [pdf_tool, web_search_tool] if t],
        llm=load_llm()
    )

    response_synthesizer_agent = Agent(
        role="Response synthesizer agent for the user query: {query}",
        goal=(
            "Synthesize the retrieved information into a concise and coherent response "
            "based on the user query: {query}. If you are not able to retrieve the "
            'information then respond with "I\'m sorry, I couldn\'t find the information '
            'you\'re looking for."'
        ),
        backstory=(
            "You're a skilled communicator with a knack for turning "
            "complex information into clear and concise responses."
        ),
        verbose=True,
        llm=load_llm()
    )

    retrieval_task = Task(
        description=(
            "Retrieve the most relevant information from the available "
            "sources for the user query: {query}"
        ),
        expected_output=(
            "The most relevant information in the form of text as retrieved "
            "from the sources."
        ),
        agent=retriever_agent
    )

    response_task = Task(
        description="Synthesize the final response for the user query: {query}",
        expected_output=(
            "A concise and coherent response based on the retrieved information "
            "Sempre responda em português brasileiro."
            "From the right source for the user query: {query}. If you are not "
            "able to retrieve the information, then respond with: "
            '"I\'m sorry, I couldn\'t find the information you\'re looking for."'
        ),
        agent=response_synthesizer_agent
    )

    crew = Crew(
        agents=[retriever_agent, response_synthesizer_agent],
        tasks=[retrieval_task, response_task],
        process=Process.sequential,  # or Process.hierarchical
        verbose=True
    )
    return crew

# ===========================
#   Streamlit Setup
# ===========================
if "messages" not in st.session_state:
    st.session_state.messages = []  # Histórico do chat

if "pdf_tool" not in st.session_state:
    st.session_state.pdf_tool = None  # Armazena a ferramenta DocumentSearchTool

if "crew" not in st.session_state:
    st.session_state.crew = None      # Armazena o objeto Crew

def reset_chat():
    st.session_state.messages = []
    gc.collect()

def display_pdf(file_bytes: bytes, file_name: str):
    """Exibe o PDF carregado em um iframe."""
    base64_pdf = base64.b64encode(file_bytes).decode("utf-8")
    pdf_display = f"""
    <iframe
        src="data:application/pdf;base64,{base64_pdf}"
        width="100%"
        height="600px"
        type="application/pdf"
    >
    </iframe>
    """
    st.markdown(f"### Prévia de {file_name}")
    st.markdown(pdf_display, unsafe_allow_html=True)

# ===========================
#   Barra Lateral
# ===========================
with st.sidebar:
    st.header("Adicione Seu Documento PDF")
    uploaded_file = st.file_uploader("Escolha um arquivo PDF", type=["pdf"])

    if uploaded_file is not None:
        # Se houver um novo arquivo e ainda não tivermos definido pdf_tool...
        if st.session_state.pdf_tool is None:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_file_path = os.path.join(temp_dir, uploaded_file.name)
                with open(temp_file_path, "wb") as f:
                    f.write(uploaded_file.getvalue())

                with st.spinner("Indexando PDF... Aguarde..."):
                    # st.session_state.pdf_tool = DocumentSearchTool(file_path="/Users/akshay/Eigen/ai-engineering-hub/agentic_rag_deepseek/knowledge/dspy.pdf")
                    st.session_state.pdf_tool = DocumentSearchTool(file_path=temp_file_path)
                    # Teste de busca
                    # result = st.session_state.pdf_tool._run("Qual é o propósito do DSpy?")
                    # st.info("Resultados da Busca Inicial:", icon="🔍")
                    # st.write(result)

            st.success("PDF indexado! Pronto para conversar.")

        # Opcionalmente, exiba o PDF na barra lateral
        display_pdf(uploaded_file.getvalue(), uploaded_file.name)

    st.button("Limpar Chat", on_click=reset_chat)

# ===========================
#   Interface Principal do Chat
# ===========================
st.markdown("""
    ### Agentic-RAG documentos complexos do mundo real <img src="data:image/png;base64,{}" width="70" style="vertical-align: -12px;">
""".format(base64.b64encode(open("assets/google-gemini-256.png", "rb").read()).decode()), unsafe_allow_html=True)

# Renderiza a conversa existente
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada do chat
prompt = st.chat_input("Faça uma pergunta sobre seu PDF...")

if prompt:
    # 1. Mostra a mensagem do usuário imediatamente
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Construa ou reutilize o Crew (apenas uma vez após o PDF ser carregado)
    if st.session_state.crew is None:
        st.session_state.crew = create_agents_and_tasks(st.session_state.pdf_tool)

    # 3. Obtém a resposta
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        # Obtém a resposta completa primeiro
        with st.spinner("Pensando..."):
            inputs = {"query": prompt}
            result = st.session_state.crew.kickoff(inputs=inputs).raw

        # Divide por linhas primeiro para preservar blocos de código e outros markdown
        lines = result.split('\n')
        for i, line in enumerate(lines):
            full_response += line
            if i < len(lines) - 1:  # Não adiciona nova linha à última linha
                full_response += '\n'
            message_placeholder.markdown(full_response + "▌")
            time.sleep(0.15)  # Ajusta a velocidade conforme necessário

        # Mostra a resposta final sem o cursor
        message_placeholder.markdown(full_response)

    # 4. Salva a mensagem do assistente na sessão
    st.session_state.messages.append({"role": "assistant", "content": result})
