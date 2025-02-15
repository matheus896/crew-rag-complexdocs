Este projeto foi inicialmente inspirado e é baseado no repositório [ai-engineering-hub/agentic_rag_deepseek](https://github.com/patchy631/ai-engineering-hub/tree/main/agentic_rag_deepseek) de [patchy631](https://github.com/patchy631). Agradecemos a ele por estabelecer as bases deste trabalho.

## 📋 Requirements

-   Python >= 3.11
-   [GroundX API Key](https://docs.eyelevel.ai/documentation/fundamentals/quickstart#step-1-getting-your-api-key)
-   [SERPER API Key](https://serper.dev/)
-   `groundx`
-   `crewai`
-   `crewai-tools`
-   `streamlit`
-   `python-dotenv` (implícito, para carregar variáveis de ambiente do arquivo .env)

## 🚀 Getting Started

1.  **Clone the repository:**

    ```bash
    git clone [https://github.com/patchy631/ai-engineering-hub.git](https://github.com/matheus896/crew-rag-complexdocs)
    cd ai-engineering-hub/agentic_rag_deepseek
    ```

2.  **Create and activate a virtual environment (recommended):**

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use .venv\Scripts\activate
    ```

3.  **Install dependencies:**

    ```bash
    pip install groundx crewai crewai-tools streamlit python-dotenv
    ```
    (Certifique-se de que `requirements.txt` esteja atualizado, se houver)

4.  **API Keys Setup:**
    *   Crie um arquivo `.env` no diretório raiz do projeto.
    *   Adicione suas chaves de API ao arquivo `.env`.  Consulte o arquivo `.env.example` para ver o formato correto (ex: `GROUNDX_API_KEY=your_groundx_key`, `SERPER_API_KEY=your_serper_key`).
    * Garanta que a variável `OPENAI_API_KEY` esteja configurada, mesmo não sendo utilizada diretamente. A `crewai` exige por padrão.

5.  **Run the application:**

    ```bash
    streamlit run post-agentic-rag.py
    ```

## 🎯 Usage

1.  Abra o aplicativo no seu navegador (o endereço será exibido no terminal).
2.  Na barra lateral, carregue um documento PDF.
3.  Digite sua pergunta na caixa de entrada do chat.
4.  A aplicação irá processar a pergunta, pesquisar no documento (e na web, se necessário) e exibir a resposta.
5.  Use o botão "Limpar Chat" para iniciar uma nova conversa.

## 💡 Features in Detail

### **Agentic RAG Workflow**

O coração do projeto é o workflow agentic RAG, que utiliza o CrewAI para orquestrar dois agentes principais:

*   **`retriever_agent`**:  Responsável por recuperar informações relevantes.  Prioriza a pesquisa no documento PDF usando o GroundX. Se a informação não for encontrada no PDF, ele usa a ferramenta Serper para pesquisar na web.
*   **`response_synthesizer_agent`**: Recebe as informações recuperadas pelo `retriever_agent` e as sintetiza em uma resposta coerente e concisa para o usuário.

Esses agentes trabalham em conjunto, executando tarefas sequencialmente (`Process.sequential`) para fornecer a resposta final.  O uso de agentes permite uma abordagem modular e flexível para o processo de RAG.

### **GroundX Integration**

A integração com o GroundX é feita através da classe `DocumentSearchTool` (que deve estar definida em `src/agentic_rag/tools/custom_tool.py`).  Esta classe é responsável por:

*   **Indexação do PDF:** Quando um PDF é carregado, o `DocumentSearchTool` processa o documento, provavelmente usando a API do GroundX para indexar o conteúdo e torná-lo pesquisável.
*   **Pesquisa no Documento:**  O `retriever_agent` usa o `DocumentSearchTool` para realizar pesquisas no PDF indexado, buscando trechos relevantes para responder à pergunta do usuário.

### **LLM (Large Language Model)**

O projeto usa o modelo `gemini/gemini-2.0-flash` como LLM para geração de texto. O LLM é usado tanto pelo `retriever_agent` quanto pelo `response_synthesizer_agent` para entender as perguntas, processar informações e gerar respostas.  O uso de um LLM permite que o sistema lide com linguagem natural de forma eficaz.

### **Interface Streamlit**

A interface do usuário é construída com Streamlit, o que facilita a criação de aplicativos web interativos.  Os principais componentes da interface incluem:

*   **Barra Lateral:** Permite carregar arquivos PDF e limpar o histórico de chat.
*   **Visualização de PDF:** Exibe o PDF carregado para referência.
*   **Chat:**  Permite que os usuários façam perguntas e visualizem as respostas dos agentes.
*   **Efeito de Digitação**:  Simula a digitação da resposta pelo agente em tempo real.

## 🤝 Contributing

Contribuições são bem-vindas!  Por favor, faça um fork do repositório e envie um pull request com suas melhorias.

## 📄 License
Este projeto foi criado com o intuito de ser um material educativo, demonstrando como integrar tecnologias como a CrewAI e a GroundX para a criação de aplicações RAG. Sinta-se à vontade para usar, modificar e distribuir este código para fins educacionais e de pesquisa. A atribuição é apreciada, mas não obrigatória. Para uso comercial, por favor, entre em contato.

## 🙏 Acknowledgments

*   [CrewAI](https://www.crewai.com/)
*   [EyelevelAI (GroundX)](https://www.eyelevel.ai/)
*   [Serper](https://serper.dev/)
*   [Streamlit](https://streamlit.io/)
*   [Google Gemini](https://ai.google.dev/gemini-api/docs)

---

Made with ❤️ using CrewAI, GroundX, Serper, and Streamlit
