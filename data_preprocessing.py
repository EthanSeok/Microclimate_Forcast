import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def preprocess_env(env_dir):
    csv_files = []

    for root, dirs, files in os.walk(env_dir):
        for file in files:
            if file.endswith('.csv'):
                csv_files.append(os.path.join(root, file))

    df_list = []
    for file in csv_files:
        df = pd.read_csv(file, parse_dates=['tm'])
        df_list.append(df)

    final_df = pd.concat(df_list, ignore_index=True)

    final_df['day'] = final_df['tm'].dt.day
    final_df['hour'] = final_df['tm'].dt.hour

    return final_df

def preprocess_inner(inner_path):
    inner = pd.read_csv(inner_path, parse_dates=['Date&Time'])

    inner['year'] = inner['Date&Time'].dt.year
    inner['month'] = inner['Date&Time'].dt.month
    inner['day'] = inner['Date&Time'].dt.day
    inner['hour'] = inner['Date&Time'].dt.hour

    return inner

def data_preprocessing(env_dir, inner_path):
    env = preprocess_env(env_dir)
    inner = preprocess_inner(inner_path)

    data = pd.merge(inner, env, on=['year', 'month', 'day', 'hour'], how='left')
    data = data.drop(columns=['year', 'month', 'day', 'hour', 'tm', 'STEMP', 'SWAT', 'SEC', '지점', '날짜', '시간'])
    data = data.rename(columns={'TEMP': 'inner_temp', 'HUMI': 'inner_hum', 'CO2': 'inner_CO2', 'PPF': 'inner_PPF', '일사(MJ/m2)': 'out_radn_m', '온도': 'out_temp', '풍속': 'out_wind', '습도': 'out_hum'})

    data['out_radn_w'] = data['out_radn_m'] * 277.78

    data = data.interpolate(method='linear', limit_direction='both')

    # print(data.info())
    return data


def plot_data(data):
    fig, ax = plt.subplots(figsize=(14, 7))
    sns.lineplot(data=data, x='Date&Time', y='out_temp', label='out_temp')
    sns.lineplot(data=data, x='Date&Time', y='inner_temp', label='inner_temp')
    ax.tick_params(axis='x', rotation=45)
    plt.legend()
    plt.show()

def main():
    env_dir = 'output/cache/ASOS/146'
    inner_path = 'input/greenhouse_inner.csv'

    data = data_preprocessing(env_dir, inner_path)
    data.to_csv('output/preprocessed_data.csv', index=False, encoding='utf-8-sig')
    # plot_data(data)
    # print(data.info())


if __name__ == '__main__':
    main()
