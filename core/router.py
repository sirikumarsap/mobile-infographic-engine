import json
import re
import os

def route_session_inputs(command_call, parameters, prompt_context, attachments):
    """
    DYNAMIC WORKFLOW & STATE INTERCEPTOR:
    Processes directory staging, prompt generation, and dynamic JSON state updates.
    """
    if command_call == "/restrict":
        update_forbidden_tokens(parameters)
        return f"State Update Successful: /configs/system_state.json updated with new restricted tokens."

    elif command_call == "/upload-ref":
        stage_files_to_directory(attachments, "/mobile-infographic-engine/reference/")
        return "Staging Successful: Reference folder updated."
        
    elif command_call == "/upload-asset":
        stage_files_to_directory(attachments, "/mobile-infographic-engine/assets/")
        return "Staging Successful: Assets folder updated."
        
    elif command_call == "/infographic":
        # Pull latest data parameters directly from the JSON state configuration
        state = load_json("/mobile-infographic-engine/configs/system_state.json")
        
        active_references = resolve_source_inputs(
            folder_path="/mobile-infographic-engine/reference/", 
            inline_prompt=prompt_context, 
            chat_attachments=attachments
        )
        active_assets = resolve_source_inputs(
            folder_path="/mobile-infographic-engine/assets/", 
            inline_prompt=prompt_context, 
            chat_attachments=attachments
        )
        
        return execute_pipeline(prompt_context, active_references, active_assets, state)

def update_forbidden_tokens(token_array):
    """
    DATA-DRIVEN STATE UPDATE: Overwrites the target array in system_state.json
    """
    state_file = "/mobile-infographic-engine/configs/system_state.json"
    current_state = load_json(state_file)
    
    # Cast all inputs to unique array list format
    unique_tokens = list(set(token_array))
    current_state["dynamic_restrictions"]["forbidden_tokens"] = unique_tokens
    
    write_json(state_file, current_state)