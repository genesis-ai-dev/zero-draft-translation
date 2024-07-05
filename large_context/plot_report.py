import json
import matplotlib.pyplot as plt
import os
from pathlib import Path
from collections import defaultdict

def load_json_files(file_list):
    data_list = []
    for file_name in file_list:
        report_dir = os.path.join(os.path.dirname(__file__), 'reports')
        report_path = os.path.join(report_dir, file_name)
        with open(report_path, 'r', encoding='utf-8') as file:
            data_list.append(json.load(file))
    return data_list

def find_common_params(data_list):
    common_params = dict(data_list[0]['parameters'])
    for data in data_list[1:]:
        for key, value in list(common_params.items()):
            if data['parameters'].get(key) != value:
                del common_params[key]
    return common_params

def get_differing_params(data, common_params):
    return {k: v for k, v in data['parameters'].items() if k not in common_params}

def get_unique_filename(file_path):
    if not file_path.exists():
        return file_path
    i = 1
    while True:
        new_path = file_path.with_name(f"{file_path.stem}({i}){file_path.suffix}")
        if not new_path.exists():
            return new_path
        i += 1

def create_plots(data_list):
    metrics = ['characTER', 'chrF', 'BLEU']
    common_params = find_common_params(data_list)
    report_dir = Path(os.path.dirname(__file__)) / 'reports'

    diff_params = set(get_differing_params(data_list[0], common_params).keys())
    for data in data_list[1:]:
        diff_params &= set(get_differing_params(data, common_params).keys())
    diff_param = list(diff_params)[0] if diff_params else "Unknown"

    is_genre_comparison = diff_param.lower() == 'genre'

    # Extract verse references from the first data item
    verses = [line.split()[0] for line in data_list[0]['generated_translation']]

    for metric in metrics:
        plt.figure(figsize=(14, 6))
        
        plot_data = []
        for i, data in enumerate(data_list):
            scores = data['scores']
            diff_params = get_differing_params(data, common_params)
            overall_score = scores[metric]['overall']
            
            if is_genre_comparison:
                first_verse = data['generated_translation'][0].split()[0]
                last_verse = data['generated_translation'][-1].split()[0]
                label = f"{', '.join(f'{k}: {v}' for k, v in diff_params.items())} ({first_verse} - {last_verse}, Overall: {overall_score:.4f})"
                x_values = [f"verse_{j+1}" for j in range(len(scores[metric]['individual']))]
            else:
                label = f"{', '.join(f'{k}: {v}' for k, v in diff_params.items())} (Overall: {overall_score:.4f})"
                x_values = verses

            plot_data.append((x_values, scores[metric]['individual'], label, overall_score))
        
        # Sort plot_data by overall score in descending order
        plot_data.sort(key=lambda x: x[3], reverse=True)
        
        for x_values, y_values, label, _ in plot_data:
            plt.plot(x_values, y_values, marker='o', label=label)

        plt.title(f'Comparing {diff_param}')
        plt.xlabel('Verse' if is_genre_comparison else 'Verse Reference')
        plt.ylabel(f'{metric} Score')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend(title="Differing Parameters", loc='center left', bbox_to_anchor=(1, 0.5))

        # Add common parameters as text above the legend with increased font size
        param_text = "\n".join(f"{k}: {v}" for k, v in common_params.items())
        plt.text(1.02, 1.02, param_text, transform=plt.gca().transAxes, fontsize=10,
                 verticalalignment='top', horizontalalignment='left')

        plt.tight_layout()
        
        # Get a unique filename
        file_path = report_dir / f'{metric}_comparison_{diff_param}.png'
        unique_file_path = get_unique_filename(file_path)
        
        plt.savefig(unique_file_path, bbox_inches='tight')
        plt.close()

        print(f"Plot saved as: {unique_file_path}")

    print(f"Comparison plots for {diff_param} have been generated and saved in the reports directory.")

# List of JSON files to process
json_files = [
    'ara to tmz report - 32-sample gospel - claude-3-5-sonnet-20240620 3-gram - 2024-07-04 12_04_06.json',
    'eng to tmz report - 32-sample gospel - claude-3-5-sonnet-20240620 3-gram - 2024-07-04 12_17_22.json',
]




data_list = load_json_files(json_files)
create_plots(data_list)

