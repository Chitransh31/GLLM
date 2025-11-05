"""
Description of this file:

This is a Streamlit application that uses LLM pipelines with Langchain and Langgraph to generate G-codes for CNC machines.
The application takes a natural language instruction as input and generates a G-code based on the instruction.
The G-code is then validated and can be downloaded or visualized as a 3D plot.

The application is written in Python and uses the Streamlit library for the user interface.
It also uses the Langchain and Langgraph libraries for the LLM pipelines.

Authors: Mohamed Abdelaal, Samuel Lokadjaja

This work was done at Software AG, Darmstadt, Germany in 2023-2024 and is published under the Apache License 2.0.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import uuid
import streamlit as st
from gllm.utils.rag_utils import setup_langchain_with_rag
from gllm.utils.model_utils import setup_model, setup_langchain_without_rag
from gllm.utils.params_extraction_utils import extract_parameters_logic, display_extracted_parameters, parse_extracted_parameters, extract_numerical_values
from gllm.utils.gcode_utils import display_generated_gcode, generate_gcode_logic, plot_generated_gcode, validate_gcode, clean_gcode, generate_gcode_unstructured_prompt, generate_task_descriptions
from gllm.utils.graph_utils import construct_graph, _print_event
from gllm.utils.plot_utils import plot_user_specification, refine_gcode
import plotly.express as px  # Import Plotly Express
from gllm.utils.params_extraction_utils import from_dict_to_text
from langgraph.checkpoint.sqlite import SqliteSaver
from gllm.utils.llm_router import LLMRouter, QueryType, get_optimal_model_for_step

st.set_page_config(page_title="G-code Generator with Intelligent Model Routing", layout="wide")



def extract_parameters(description_text):

        extracted_parameters, missing_parameters = extract_parameters_logic(st.session_state['langchain_chain'], description_text)
        # update the relevant Streamlit states
        st.session_state['extracted_parameters'] = from_dict_to_text(extracted_parameters)
        st.session_state['missing_parameters'] = missing_parameters
        st.session_state['user_inputs'].update(extracted_parameters)


def main():

    # Hide Streamlit default menu and footer
    st.markdown(
        """
        <style>
        /* remove header/footer/hamburger */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* shrink top padding so content starts earlier */
        div.block-container {
            padding-top: 0rem;
            padding-bottom: 1rem;
        }

        /* additional fallback selectors (Streamlit internal classes change over versions) */
        .block-container { padding-top: 0rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    


    _printed = set()
    thread_id = str(uuid.uuid4())
    config = {
        "configurable": {
            # Checkpoints are accessed by thread_id
            "thread_id": thread_id,},
            "recursion_limit": 1000}

    # st.title("G-code Generator for CNC Machines")
    st.title("🤖 G-code Generator with Intelligent Model Routing")
    st.write("Please describe your CNC machining task in natural language:")
    input_description = st.text_area("Task Description", height=150)

    pdf_files = st.file_uploader("Upload PDF files with additional knowledge (RAG)", accept_multiple_files=True, type=['pdf'])

    # Initialize the LLM Router
    if "llm_router" not in st.session_state:
        st.session_state['llm_router'] = LLMRouter(
            enable_rag=bool(pdf_files),
            pdf_files=pdf_files
        )

    # ⚡ Collapsible menu for model and prompt settings
    with st.expander("⚙️ Model & Routing Settings", expanded=False):
        
        # Auto-routing toggle
        enable_auto_routing = st.checkbox(
            "Enable Intelligent Auto-Routing",
            value=True,
            help="Automatically select the best model for each task. Disable to manually choose a model."
        )
        
        if not enable_auto_routing:
            # Manual model selection
            model_str = st.selectbox(
                'Choose a Language Model:', 
                ('Zephyr-7b', 'GPT-3.5', 'Fine-tuned StarCoder',
                'CodeLlama', 'DeepSeek-Coder-1B', 'Phi-3-Mini'), 
                index=1,
                help="Manually choose a model. Auto-routing is disabled."
            )
            model = setup_model(model=model_str)
        else:
            # Show routing info
            st.info("🧠 **Auto-Routing Enabled**: The system will automatically select the best model for each step:")
            st.markdown("""
            - **Parameter Extraction**: Fast, efficient models (Phi-3-Mini, DeepSeek-Coder)
            - **G-code Generation**: Code specialists (Fine-tuned StarCoder, CodeLlama)
            - **Machine Knowledge**: Knowledge-rich models (GPT-3.5, Zephyr-7b)
            - **Refinement**: Code specialists with optimization focus
            """)
            
            # User can still express preference
            user_preference = st.selectbox(
                'Preferred Model (optional):', 
                ('Auto', 'GPT-3.5', 'Fine-tuned StarCoder', 'CodeLlama', 
                 'Zephyr-7b', 'DeepSeek-Coder-1B', 'Phi-3-Mini'),
                index=0,
                help="Override auto-routing with your preferred model when suitable for the task."
            )
            
            if user_preference == 'Auto':
                user_preference = None
            
            st.session_state['user_model_preference'] = user_preference
            model_str = user_preference if user_preference else 'Auto'
            model = None  # Will be set dynamically per task

        # Let the user choose whether to use structured or unstructured prompt
        prompt_type = st.selectbox('Prompt Type:', ('Structured', 'Unstructured'), index=0)

        disable_extract_button = False if prompt_type == 'Structured' else True    # Disable Parameter Extraction if user selects unstructured prompt

        # user selects whether to use the task decomposor
        st.session_state['decompose_task'] = st.selectbox("Decompose The task Description: ", ('Yes', 'No'), index=0, disabled=disable_extract_button)
        
        st.session_state['enable_auto_routing'] = enable_auto_routing


    # Setup langchain chain with intelligent routing
    if "langchain_chain" not in st.session_state:
        if st.session_state.get('enable_auto_routing', False):
            # Use router to get optimal model for parameter extraction
            router = st.session_state['llm_router']
            context = {'task': 'parameter_extraction'}
            model, query_type, model_name = router.route(
                input_description if input_description else "",
                context=context,
                user_preference=st.session_state.get('user_model_preference')
            )
            st.session_state['current_model_name'] = model_name
            st.info(f"🎯 Using **{model_name}** for parameter extraction")
        
        if pdf_files:
            st.session_state['langchain_chain'] = setup_langchain_with_rag(pdf_files, model)
        else:
            st.session_state['langchain_chain'] = setup_langchain_without_rag(model=model)


    if "extracted_parameters" not in st.session_state:
        st.session_state['extracted_parameters'] = None
        st.session_state['missing_parameters'] = None
        st.session_state['user_inputs'] = {}
        st.session_state['gcode'] = None
        st.session_state['task_descriptions'] = []
        st.session_state['decompose_task'] = None
        st.session_state['extracted_parameters_backup'] = None
        st.session_state['user_inputs_backup'] = {}

    if "parsed_parameters" not in st.session_state:
        st.session_state.parsed_parameters = {}

    #################################################
    ############# Parameters Extraction #############
    #################################################



    disable_extract_button = False if prompt_type == 'Structured' else True    # Disable Parameter Extraction if user selects unstructured prompt

    # user selects whether to use the task decomposor
    # st.session_state['decompose_task'] = st.selectbox("Decompose The task Description: ", ('Yes', 'No'), index=0, disabled=disable_extract_button)

    extract_button = st.button("Extract Parameters", disabled=disable_extract_button)
    if extract_button and "langchain_chain" in st.session_state:
        extract_parameters(description_text=input_description)
        st.session_state['extracted_parameters_backup'] = st.session_state['extracted_parameters']
        st.session_state['user_inputs_backup'] = st.session_state['user_inputs']

        # generate subtask descriptions if the input task invovles more than one shape
        values_in_number_shapes = extract_numerical_values(st.session_state['user_inputs'], 'Number of Shapes')
        number_shapes = values_in_number_shapes[0] if type(values_in_number_shapes) is list else values_in_number_shapes

        if number_shapes > 1 and st.session_state['decompose_task'] == 'Yes':
            st.session_state['task_descriptions'] = generate_task_descriptions(model, model_str, input_description)
            st.session_state['extracted_parameters'] += f"Subtasks: {st.session_state['task_descriptions']}\n"
        else:
            st.session_state['task_descriptions'] = [input_description]

    if st.session_state['extracted_parameters']:
        display_extracted_parameters()

    if st.button("Simulate Tool Path (2D)", disabled=disable_extract_button):
        if st.session_state['extracted_parameters']:
            st.session_state['parsed_parameters'] = parse_extracted_parameters(st.session_state['extracted_parameters'])
            
            # Check if parsed_parameters is valid before plotting
            if st.session_state.parsed_parameters and isinstance(st.session_state.parsed_parameters, dict):
                st.text("If the plotted path is incorrect, please adjust the task description.")
                st.pyplot(plot_user_specification(parsed_parameters=st.session_state.parsed_parameters))
            else:
                st.error("Could not parse parameters for visualization. Please check your task description and try extracting parameters again.")
                st.write("Debug: parsed_parameters =", st.session_state.parsed_parameters)

    ################################################
    ############ G-Code Generation #################
    ################################################

    if st.button("Generate G-code"):

        # Use intelligent routing for G-code generation
        if st.session_state.get('enable_auto_routing', False):
            router = st.session_state['llm_router']
            context = {'task': 'gcode_generation'}
            gcode_model, query_type, gcode_model_name = router.route(
                input_description if input_description else "",
                context=context,
                user_preference=st.session_state.get('user_model_preference')
            )
            st.success(f"🎯 Using **{gcode_model_name}** for G-code generation")
            
            # Update the langchain chain with the new model
            if pdf_files:
                st.session_state['langchain_chain'] = setup_langchain_with_rag(pdf_files, gcode_model)
            else:
                st.session_state['langchain_chain'] = setup_langchain_without_rag(model=gcode_model)

        gcodes_combined = ""

        if not st.session_state['task_descriptions']:
            st.session_state['task_descriptions'] = [input_description]

        for subtask_description in st.session_state['task_descriptions']:
            print("++++++++++++++++++++++++++++++++++++++++++")
            print("SUBTASK DESCRIPTION:", subtask_description)
            print("++++++++++++++++++++++++++++++++++++++++++")
            if disable_extract_button:
                st.session_state['gcode'] = generate_gcode_unstructured_prompt(st.session_state['langchain_chain'], subtask_description)
            else:

                if len(st.session_state['task_descriptions']) > 1:
                    extract_parameters(description_text=subtask_description)

                if "langchain_chain" in st.session_state and 'parsed_parameters' in st.session_state:
                    # Assume construct_graph is modified to return the graph builder and the memory object
                    # Or, instantiate the checkpointer here. Let's use SqliteSaver as an example.

                    with SqliteSaver.from_conn_string(":memory:") as memory:
                        # Construct the graph *builder*
                        graph_builder = construct_graph(
                            st.session_state['langchain_chain'],
                            st.session_state['user_inputs'],
                            st.session_state['extracted_parameters']
                        )
                        
                        # Compile the graph with the checkpointer
                        graph = graph_builder.compile(checkpointer=memory)

                        # Stream events from the compiled graph
                        events = graph.stream(
                            {"messages": [("user", subtask_description)], "iterations": 0},
                            config,
                            stream_mode="values"
                        )

                        for event in events:
                            # Defensively check if the 'generation' key exists in the event
                            if "generation" in event:
                                # This code will only run when the key is present
                                gcodes_combined += f"\n{event['generation']}"
                                gcodes_combined = refine_gcode(gcodes_combined)
                                st.session_state['gcode'] = gcodes_combined

        # restore the extracted parameters from the input task description
        st.session_state['user_inputs'] = st.session_state['user_inputs_backup']
        st.session_state['extracted_parameters'] = st.session_state['extracted_parameters_backup']

    display_generated_gcode()

    plot_generated_gcode()

    # Model Routing Dashboard
    if st.session_state.get('enable_auto_routing', False):
        with st.expander("🧠 Model Routing Dashboard", expanded=False):
            st.markdown("### Intelligent Model Selection")
            
            router = st.session_state['llm_router']
            
            # Show routing explanation for current task
            if input_description:
                explanation = router.get_routing_explanation(
                    input_description,
                    context={'task': 'gcode_generation'}
                )
                st.markdown(explanation)
            
            # Model capability matrix
            st.markdown("### Model Capability Matrix")
            
            import pandas as pd
            from gllm.utils.llm_router import MODEL_REGISTRY, QueryType
            
            # Create capability matrix
            matrix_data = []
            for model_key, config in MODEL_REGISTRY.items():
                row = {
                    'Model': config.name,
                    'Capability': config.capability.value.replace('_', ' ').title(),
                    'Priority': config.priority,
                    'G-code Gen': '✓' if QueryType.GCODE_GENERATION in config.use_cases else '',
                    'Params': '✓' if QueryType.PARAMETER_EXTRACTION in config.use_cases else '',
                    'Knowledge': '✓' if QueryType.MACHINE_KNOWLEDGE in config.use_cases else '',
                    'General': '✓' if QueryType.GENERAL_QUERY in config.use_cases else '',
                }
                matrix_data.append(row)
            
            df = pd.DataFrame(matrix_data)
            df = df.sort_values('Priority', ascending=False)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Current session models
            if 'current_model_name' in st.session_state:
                st.markdown("### Models Used This Session")
                st.success(f"**Current Model**: {st.session_state['current_model_name']}")

     # Debug information
    if st.checkbox("Show Debug Info"):
        st.write("Session State:", st.session_state)

if __name__ == "__main__":
    main()
