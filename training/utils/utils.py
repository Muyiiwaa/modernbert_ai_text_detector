import pandas as pd
import numpy as np
import kagglehub
import os


def load_ai_data() -> pd.DataFrame:
    """_summary_

    Returns:
        pd.DataFrame: _description_
    """
    data_one = pd.read_csv('data/generated_texts_one.csv')
    data_two = pd.read_csv('data/generated_texts_two.csv')

    ai_data = pd.concat([data_one, data_two])
    ai_data.reset_index(drop =True, inplace = True)
    ai_data['label'] = 1
    ai_data.rename(columns = {'GeneratedText':'text'}, inplace = True)

    return ai_data

def load_human_data() -> pd.DataFrame:
    """_summary_

    Returns:
        pd.DataFrame: _description_
    """
    path = kagglehub.dataset_download("fabiochiusano/medium-articles")
    csv_path = os.path.join(path, "medium_articles.csv")
    df = pd.read_csv(csv_path)
    df = df.sample(n=1000, random_state=23)
    df.reset_index(drop=True, inplace=True)
    df['label'] = 0
    df = df[['text','label']]

    return df

def load_kaggle_data() -> pd.DataFrame:
    path = kagglehub.dataset_download("shanegerami/ai-vs-human-text")
    csv_path = os.path.join(path, "AI_Human.csv")
    df = pd.read_csv(csv_path)
    df.rename(columns = {'generated':'label'}, inplace = True)
    df = pd.concat([df[df['label'] == 1].sample(n=4000, random_state=42),
    df[df['label'] == 0].sample(n=4000, random_state=42)
    ]).sample(frac=1, random_state=42).reset_index(drop=True)
    df = df.astype({'label': 'int'})

    return df

def get_full_data() -> pd.DataFrame:
    ai_data = load_ai_data()
    human_data = load_human_data()
    kaggle_data = load_kaggle_data()
    final_data = pd.concat([ai_data, human_data,kaggle_data])

    return final_data


if __name__ == "__main__":
    data = load_human_data()
    print(f'human: {data.shape}')
    ai_data = load_ai_data()
    print(f'ai: {ai_data.shape}')
    full_data = get_full_data()
    print(full_data.shape)
    full_data.to_csv('final_data.csv', index = False)

