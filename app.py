import streamlit as st
import pandas as pd
import pickle

st.set_page_config(page_title='Player Recommend', initial_sidebar_state='auto')

@st.cache(show_spinner=False)
def getData():
    outfield_df = pd.read_pickle('Data/outfield.pickle')
    gk_df = pd.read_pickle('Data/goalkeeper.pickle')

    with open('Data/outfield_id.pickle', 'rb') as file:
        outfield_id = pickle.load(file)
    with open('Data/goalkeeper_id.pickle', 'rb') as file:
        gk_id = pickle.load(file)

    with open('Data/engine_outfield.pickle', 'rb') as file:
        outfield_engine = pickle.load(file)
    with open('Data/engine_goalkeeper.pickle', 'rb') as file:
        gk_engine = pickle.load(file)

    return [outfield_df, outfield_id, outfield_engine], [gk_df, gk_id, gk_engine]


with st.spinner(text="Fetching data"):
    outfield_data, gk_data = getData()

st.title('Football player recommendation based on 2021-2022 statistics')
st.subheader("Created by [**Rohan Choudhary**](%s)" % 'https://www.linkedin.com/in/rohanchoudhary12/')
st.markdown("***")

col1, col2 = st.columns([1, 2.2])

with col1:
    radio = st.radio('Player type', ['Outfield players', 'Goalkeepers'])

with col2:
    df, player_id, engine = outfield_data if radio == 'Outfield players' else gk_data
    players = sorted(list(player_id.keys()))
    age_default = (min(df.Age), max(df.Age))
    goat_index = [players.index(player) for player in players if player.startswith('Cristiano Ronaldo') or player.startswith('Manuel Neuer')][0]
    query = st.selectbox('Player name', players, index=goat_index or 0,
                         help='Search player as a name or from a specific team without deleting any character')

def getRecommendations(metric, df_type, league='All', comparison='All positions', age=age_default,
                       count=10):

    df_res = df.iloc[:, [1, 3, 5, 6]].copy()

    df_res['Player'] = list(player_id.keys())
    df_res.insert(1, 'Similarity', metric)
    df_res = df_res.sort_values(by=['Similarity'], ascending=False)
    metric = [str(num) + '%' for num in df_res['Similarity']]
    df_res['Similarity'] = metric
    # ignoring the top result
    df_res = df_res.iloc[1:, :]

    # comparison filtering
    if comparison == 'Same position' and df_type == 'outfield':
        q_pos = list(df[df['Player'] == query.split('(')[0]].Pos)[0]
        df_res = df_res[df_res['Pos'] == q_pos]

    # league filtering
    if league != 'All':
        df_res = df_res[df_res['Comp'] == league]

    # age filtering
    if age != age_default:
        df_res = df_res[(df_res['Age'] >= age[0]) & (df_res['Age'] <= age[1])]
    df_res[['Age']] = df[['Age']].astype('int')

    # returning the final result
    df_res = df_res.iloc[:count, :].reset_index(drop=True)
    df_res.index = df_res.index + 1
    df_res.rename(columns={'Pos': 'Position', 'Comp': 'League'}, inplace=True)
    return df_res


col4, col5, col6, col7 = st.columns([1.3, 2, 2, 2])

with col4:
    count = st.slider('Number of results', 0, 20, 5)

with col5:
    league = st.selectbox('League', sorted(list(df.Comp.unique()) + ['All']),
                          help='Select any league as filter or All')

with col6:
    position = st.selectbox('Comparison with position', ['All positions', 'Same position'],
                            help='Choose same position or all/any')

with col7:
    age = st.slider('Age bracket', 15, 42, (20, 32))

sims = engine[query]
df_type = 'outfield' if len(df) > 2000 else 'gk'
recommendations = getRecommendations(sims, df_type=df_type, league=league, comparison=position, age=age, count=count)
st.table(recommendations)

st.markdown("***")

st.write("All the FIFA, PES, DLS and other such games enjoyer, are you in a situation where you can't "
         "purchase your favourite player or the player that will complete your team puzzle? Well you can "
         "look for their alternatives here with 113 different features including position, goals, assists, "
         "goal and assists, all these stats per 90, tackles won, passes complete etc.")
st.write("**Tech Involved: Machine Learning, PCA, Cosine Similarity.**")
st.write("*Connect with me on linkedin if you want to contribute in this project.*")
st.write("[Data credits](%s)" %'https://fbref.com/en/')
