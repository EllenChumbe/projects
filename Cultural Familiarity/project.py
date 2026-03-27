import pandas as pd
import matplotlib
matplotlib.use('macosx') #('Agg')
import matplotlib.pyplot as plt
from textwrap import wrap
import textwrap
from matplotlib.backends.backend_pdf import PdfPages

def read_files():
    df = pd.read_csv('Consolidated.csv')
    # Third row contains column names, first 2 rows should not be read into df_order
    df_order = pd.read_csv('Model Key.csv', header=2) 
    return df, df_order

def get_unique_countries(df):
    countries = list((df['Country'].unique()))
    countries = [s.replace('USA','the United States') for s in countries]
    countries = [s.replace('United Kingdom','the United Kingdom') for s in countries]
    return countries

def replace_country_names_in_prompts(df, countries, prompts_columns_list):
    # Find country names in df_prompts and replace them with label [COUNTRY]
    df_prompts = df[prompts_columns_list]
    df_prompts = df_prompts.replace(countries, 'COUNTRY', regex = True)
    df_prompts = df_prompts.stack().unique()
    return df_prompts

def get_generic_prompt(df, columns_list, countries):    
    '''
    Input: df: DataFrame, column_list: list of strings (column names)
    Output: df with name of countries in df[column_name] replaced with 'COUNTRY' (generic label)  
    '''
    df[columns_list] = df[columns_list].replace(countries, 'COUNTRY', regex = True)
    return df

def get_prompt_number(row, prompt_text, n_prompts):
    for i in range(1, n_prompts+1):
        if row[f'Prompt{i}'] == prompt_text:
            return i

def get_score_per_method_graph(df_merged_order):
    # Average score per response type
    categories = ['RAG', 'Search', 'Vanilla']

    values = [round(df_merged_order[df_merged_order['Response Type']=='RAG']['Scores'].mean(),2), 
            round(df_merged_order[df_merged_order['Response Type']=='Search']['Scores'].mean(),2), 
            round(df_merged_order[df_merged_order['Response Type']=='Vanilla']['Scores'].mean(),2)]
    
    fig, ax = plt.subplots(nrows=1, figsize=(10,5))
    p1 = ax.bar(categories, values, align="center")
    ax.grid(False)
    ax.set_title("Average annotated scores per response type",fontsize=16,fontweight='bold')
    ax.set_xlabel("Response types", fontsize=12)
    ax.set_ylim(0,3.2)
    plt.yticks(ticks=[0, 1, 2, 3])
    ax.set_ylabel("Avg scores", fontsize=12)
    ax.bar_label(p1, fontsize=13)
    plt.tight_layout()

def get_score_per_country_and_method_graph(df_merged_order):
    # Average score per country and response type
    df_country_response_means = round(df_merged_order.groupby(['Country','Response Type'])['Scores'].mean(),2).reset_index()
    ax = df_country_response_means.pivot(index='Country', 
                                         columns='Response Type', 
                                         values= 'Scores'
                                         ).plot(kind='bar', figsize=(10,5))

    #Grouped Bar Chart
    plt.style.use('seaborn-v0_8-notebook')
    plt.grid(False)
    plt.xlabel('Countries', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.ylabel('Average Scores', fontsize=12)
    plt.ylim(0,3.8)
    plt.yticks(ticks=[0,1,2,3])
    plt.title('Average score per country and response type',fontsize=18,fontweight='bold') 
    plt.tight_layout()
    for container in ax.containers:
        ax.bar_label(container, fmt='%.2f', fontsize=8)
    plt.legend()

def get_score_per_prompt_and_method_graph(df_merged_order):
    # Average score per prompt and response type
    df_prompt_response_means = round(df_merged_order.groupby(['Prompt_text','Response Type'])['Scores'].mean(),2).reset_index()
    ax = df_prompt_response_means.pivot(index='Prompt_text', 
                                   columns='Response Type', 
                                   values= 'Scores'
                                   ).plot(kind='barh', figsize=(10,10))
    
    plt.style.use('seaborn-v0_8-notebook')
    
    # Wrap y-tick labels
    labels = [textwrap.fill(label.get_text(), 45) for label in ax.get_yticklabels()]
    ax.set_yticklabels(labels)
    
    plt.grid(False)
    plt.xlabel('Average Scores', fontsize=13)
    plt.xlim(0,3.5)
    plt.xticks(ticks=[0,1,2,3])
    plt.ylabel('Prompts', fontsize=13)
    plt.title('Average score per prompt and response type', fontsize=18, fontweight="bold", ha="center") 
    for container in ax.containers:
        ax.bar_label(container, fmt='%.2f', fontsize=9)
    plt.legend(fontsize=13)
    plt.tight_layout()

def export_graphs(df_merged_order):
    # Create a PdfPages object
    with PdfPages('graphs.pdf') as pdf:
        # First plot
        get_score_per_method_graph(df_merged_order)
        pdf.savefig() # Save current figure into PDF
        plt.close() # Close figure to free memory

        # Second plot
        get_score_per_country_and_method_graph(df_merged_order)
        pdf.savefig() 
        plt.close()

        # Third plot
        get_score_per_prompt_and_method_graph(df_merged_order)
        pdf.savefig() 
        plt.close()

        # Adding metadata PDF file
        d = pdf.infodict()
        d['Title'] = 'Cultural Familiarity Analysis'
        d['Author'] = 'Ellen Chumbe'

def main():
    print('Start')
    df, df_order = read_files()
    countries = get_unique_countries(df)
    
    # Generate list of column names iteratively. Columns will be selected from df and df_sample later.
    prompts_columns_list = [f'Prompt{i+1}' for i in range(10)] 
    df_prompts = replace_country_names_in_prompts(df, countries, prompts_columns_list) # to be used later
    generations_columns_list = [f'Generation {i+1}.{j+1}' for i in range(10) for j in range(3)]
    scores_columns_list = [f'Score {i+1}.{j+1}' for i in range(10) for j in range(3)]
    generations_keys_columns_list = [f'Generation {i+1}.{j+1} Key' for i in range(10) for j in range(3)]

    # Selecting columns from df
    selected_cols = ['Country', 'Annotator #'] + prompts_columns_list + generations_columns_list + scores_columns_list
    df = get_generic_prompt(df, prompts_columns_list, countries)
    df_sample = df[selected_cols]

    # Selecting columns from df
    selected_order_cols = ['Country'] + prompts_columns_list + generations_columns_list + generations_keys_columns_list
    df_order = get_generic_prompt(df_order, prompts_columns_list, countries)
    df_order_sample = df_order[selected_order_cols]

    # The following was intended to work with USA data, but next steps proved that data was incomplete and was ultimately discarded.
    for i in range(len(df_sample)):
        if df_sample.loc[i,'Country'] == 'USA':
            df_sample.loc[i,'Country'] = 'United States'
    
    # Merging both dataframes to consolidate prompts, generations, scores, and order of response types 
    df_merged = pd.merge(df_sample, df_order_sample, on=['Country']+ prompts_columns_list + generations_columns_list, how='inner')
    
    # Removing USA and UK data
    rows_to_drop = df_merged[(df_merged['Country'] == 'United States')| (df_merged['Country'] =='United Kingdom')].index
    df_merged.drop(rows_to_drop, inplace=True)

    # Creating list of dictionaries to hold data per Country-Annotator#-Prompt_text
    rows = []
    n_prompts = 10 
    n_generations = 3 # number of response generations per prompt

    for _, row in df_merged.iterrows():
        for p in range(len(df_prompts)): # df_prompts has unique prompts detected
            for g in range(1, n_generations + 1):
                prompt_text = df_prompts[p]
                n = get_prompt_number(row, prompt_text, n_prompts) # get prompt number that contains df_prompts[p] in rows
                if n is None:
                    continue
                rows.append({
                    "Country": row["Country"],
                    "Annotator#": row["Annotator #"],
                    "Prompt_text": df_prompts[p],
                    "Generations": row[f"Generation {n}.{g}"],
                    "Scores": row[f"Score {n}.{g}"],
                    "Response_keys": row[f"Generation {n}.{g} Key"] 
                })

    df_merged_order = pd.DataFrame(rows)
    response_type = [x.split(' ',1)[0] for x in df_merged_order['Response_keys']]
    df_merged_order['Response Type'] = response_type

    # Export graphs to PDF file
    export_graphs(df_merged_order)

    print('End')
    
if __name__ == "__main__":
    main()