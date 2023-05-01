import inquirer
import os
from engine import Compiler, Generator, Validator

def folder_question():
    folders = [f for f in os.listdir('./generated') if os.path.isdir(os.path.join('./generated', f))]
    if len(folders) == 0:
        print("Generated folder is not found.")
        exit(0)
    questions = [inquirer.List('target_folder',
                message="Target folder?",
                choices=folders,
            )]
    return inquirer.prompt(questions)

questions = [inquirer.List('action',
                message="What do you need?",
                choices=['Generate', 'Batch Regenerate', 'Compile', 'Validate', 'Exit'],
            )]
answers = inquirer.prompt(questions)

runner = None
if answers['action'] == 'Generate' or answers['action'] == 'Batch Regenerate':
    runner = Generator()
    if 'Batch' in answers['action']:
        answers = folder_question()
        runner.batch_run(f"./generated/{answers['target_folder']}")
        exit(0)
elif answers['action'] == 'Compile' or answers['action'] == 'Validate':
    action = answers['action']
    answers = folder_question()
    if action == 'Compile':
        runner = Compiler(answers['target_folder'])
    elif action == 'Validate':
        runner = Validator(answers['target_folder'])
elif answers['action'] == 'Exit':
    exit(0)

if runner != None:
    runner.run()