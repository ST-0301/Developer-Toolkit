import os

def process_code_files_from_paths(path_list_text):
    formatted_output = ""
    paths = [p.strip().strip('"').strip("'") for p in path_list_text.splitlines() if p.strip()]
    
    if not paths:
        return ""

    for file_path in paths:
        if not os.path.exists(file_path):
            formatted_output += f"Error: File not found at '{file_path}'\n\n"
            continue
        
        if not os.path.isfile(file_path):
            formatted_output += f"Error: '{file_path}' is a directory, not a file.\n\n"
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
                
            formatted_output += f"File: {file_path}\n"
            formatted_output += "-" * 50 + "\n"
            formatted_output += file_content + "\n"
            formatted_output += "=" * 50 + "\n\n"
            
        except UnicodeDecodeError:
            formatted_output += f"Error: {file_path} is not a readable text file.\n\n"
        except Exception as e:
            formatted_output += f"Error reading {file_path}: {str(e)}\n\n"
            
    return formatted_output, len(paths)