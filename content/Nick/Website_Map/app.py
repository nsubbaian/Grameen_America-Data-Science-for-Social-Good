import plotly.graph_objects as go
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html

def renameCols(df):
    df.rename(columns={
        'Not including your children under 18, how many other family members live with you (including spouse/partner, parents, etc.)': 'Amt_AdultsinFamily',
        "How many children under age 18 do you have, who live at home with you": "Amt_childreninFamily",
        "Is your spouse/partner one of those who live with you": "SpouseorPartner_atHome",
        "Who is the family's primary income earner": "primaryIncomeOwner",
        "How much money did the other family members who live with you (children, spouse, others) contribute to your family's income LAST MONTH": "moneyLastMonth_fromFamilyatHome",
        "How much did your family receive in WIC, SNAP/Food Stamps, Social Security, Unemployment Insurance, Medicaid, Housing Assistance, other government benefits LAST MONTH": "moneyLastMonth_fromGovBenefits",
        "What was YOUR contribution to the family's income LAST MONTH": "moneyLastMonth_fromYou",
        "Which best describes your housing situation": "housingSituation",
        "What is the MONTHLY cost of your housing ": "costofHousing_Monthly",
        "Do you have a car": "car",
        "Have a computer": "computer",
        "Do you sell items or provide services to earn money on your own? That is, do you work for yourself (e.g. cooking, babysitting, selling cosmetics)": "ProvideServices_workForYourself",
        "What is the primary location that you sell or provide these services": "location_ofsellingServices",
        "Country of Birth (Member)": "Country_ofBirth_Member",
        "Have you ever had a CHECKING account with a bank in the United States": "CheckingAccount_inUS",
        "What is the current balance in this CHECKING account": "CheckingAcount_balance",
        "Have you ever had a SAVINGS account with a bank in the United States": "SavingsAccount_inUS",
        "What is the current balance in this SAVINGS account": "SavingsAccount_balance",
        "Have you ever had a credit card": "own_creditCard",
        "What was or is the rate of interest (APR) charged on this credit card %": "APR_onCreditCard",
        "Card ID Number (PUID) (Member)": "CardIDNumber_PUID_Member",
        "Reason for Blacklist (Member)": "BlackListReason_Member",
        "Reason For Departure (Why did the Member leave?)": "DepartureReason_Member",
        "Select Business Category": "BusinessCategory",
        "Which of the following best describes what you intend to use this Grameen loan for": "intention_forGrameenLoan",
        "Is this your first Grameen America loan / Es tu primer préstamo con Grameen America?": "isthis_FirstGrameenLoan",
        "Were you running this business or income generating activity before receiving this Grameen America loan": "runningBusiness_beforeGrameenLoan",
        "How many hours a week do you work at your Grameen business or income generating activity": "hoursWorkEveryWeek_GrameenBusiness",
        "What is your average MONTHLY income from your Grameen business or income generating activity": "monthlyIncome_GrameenActivity",
        "What is the primary location where you operate your Grameen America business": "location_GrameenBusiness",
        "NOT including yourself, how many full-time employees (employees working MORE than 30 hours per week) do you pay": "fullTimeEmployees_toPay",
        "NOT including yourself, how many part-time employees (employees working LESS than 30 hours per week) do you pay": "partTimeEmployees_toPay",
        "Which of the following best describes your ethnicity": "yourEthinicity",
        "Which of the following best describes your race": "YourRace",
        "Do you have a wage-earning job (NOT your Grameen activity)": "havewageEarningJob_notGrameenActivity",
        "Which of the following best describes your wage-earning job (NOT your Grameen activity)": "wageEarningJob_notGrameenActivity",
        "How many hours per WEEK do you work at this wage-earning job": "hoursWeekly_wageEarningJob_notGrameenActivity",
        "What is your total MONTHLY income from this wage earning job / Cual es tu ingreso total MENSUAL de este trabajo asalariado?": "monthlyIncome_wageEarningJob_notGrameenActivity",
        "In the last week, how many times did you use your debit/ATM card to pay for some item (such as groceries, business purchases, phone bills, electricity bills, etc.)?": "timesUsed_debitOrATMcard",
        "Phone Provider": "PhoneProvider"
        }, inplace=True)


df_zipcodes = pd.read_excel('Branch Zip Codes.xlsx')
df = pd.read_parquet('all_data_retention_df')
renameCols(df)
df_h = pd.DataFrame()

map = go.Figure(go.Scattergeo(
    lon=df_zipcodes['Long'],
    lat=df_zipcodes['Lat'],
    text=df_zipcodes['Branch'],
    mode='markers',
    marker=dict(size=8, color='lightseagreen')
))
map.update_geos(
    scope="north america",
    showcountries=True, countrycolor="White",
)
map.update_layout(title='Grameen Branches', title_x=0.5, height=390, margin=dict(l=0, r=0, b=10, t=40, pad=0))

hist = go.Figure(go.Histogram())
hist.update_layout(title_x=0.5, height=400, margin=dict(b=10, t=40, pad=0))

dd_list = []
for c in df.columns[5:]:
    dd_list.append({'label': c, 'value': c})

app = dash.Dash()
app.layout = html.Div([
    dcc.Graph(id='map', figure=map),
    dcc.Dropdown(
        id='dropdown',
        options=dd_list,
        value=dd_list[0]['label'],
        placeholder='Select Data',
        style={'width': '400px'}
    ),
    dcc.Graph(id='hist', figure=hist),
])

@app.callback(
    dash.dependencies.Output('hist', 'figure'),
    [dash.dependencies.Input('dropdown', 'value'), dash.dependencies.Input("map", "clickData")])
def update_output(value, data):
    if data is not None:
        global map, hist, df_h
        branch = map.data[0].text[data['points'][0]['pointIndex']]
        df_h = df[df['Branch'] == branch]
        hist.data[0].x = df_h[value]
        hist.update_layout(title_text = branch + ': ' + value, showlegend=False)
    return hist

@app.callback(
    dash.dependencies.Output('map', 'figure'),
    [dash.dependencies.Input("map", "clickData")])
def highlight_branch(data):
    if data is not None:
        global map
        colors = ['lightseagreen']*len(map.data[0].text)
        colors[data['points'][0]['pointIndex']] = 'salmon'
        sizes = [8]*len(map.data[0].text)
        sizes[data['points'][0]['pointIndex']] = 12
        map.data[0].marker.color = colors
        map.data[0].marker.size = sizes
    return map


app.run_server(debug=True, use_reloader=False)  # Turn off reloader if inside Jupyter