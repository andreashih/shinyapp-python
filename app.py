from shiny import App, render, ui, reactive
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import pandas as pd
import numpy as np

# read data
cnstr_shiny = pd.read_csv("data/cnstr_shiny_sense_pred.csv")
# define selections
cnstr_forms = cnstr_shiny['Form'].unique().tolist()
relation_choices = ['吸引 (Attraction)', '不吸引 (Repulsion)']
column_choices = ['構式形式', '構式例子', '上下文', '關聯', '搭配強度', 
                '構式義（人工標記）', '構式義（機器預測）', 'PTT 板']

app_ui = ui.page_fluid(
    ui.panel_title("Collostruction Analysis"),

    ui.layout_sidebar(

      ui.panel_sidebar(
        ui.input_text("word", "輸入字詞", placeholder="什麼"),
        ui.input_select("cnstr_form", "構式", cnstr_forms),
        ui.input_radio_buttons("relation", "詞組與構式關係", relation_choices),
        ui.input_checkbox_group("column", "表格欄位", column_choices),
        ui.input_numeric("n", "顯示數目", value=10),
        width = 3
      ),

      ui.panel_main(

        ui.navset_tab(
            ui.nav("Table", ui.output_table("table")),
            ui.nav("Plot", ui.output_plot("plot", inline=True))     
        ),
      ),
    ),
)


def server(input, output, session):

    # update cnstr form choices based on input words
    @reactive.Effect
    def _():
        x = input.word()
        form_choices = []

        for form in cnstr_forms:
            if x is None:
                form_choices = []
            elif x in form:
                form_choices.append(form)

        ui.update_select(
            "cnstr_form",
            label="構式",
            choices=form_choices
        )

    @output
    @render.table
    def table() -> object:

        cnstr_form = input.cnstr_form()
        relation = input.relation()
        n = input.n()
        column = input.column()
        column_mapping = {'構式形式': 'Form', '構式例子': 'Construction', 
                        '上下文': 'Context', '關聯': 'Relation', '搭配強度': 'Collostruction_strength', 
                        '構式義（人工標記）': 'Sense_annotated', 
                        '構式義（機器預測）': 'Sense_predicted', 'PTT 板': 'Boardname'}

        # filter cnstr form
        cnstr_table = cnstr_shiny[cnstr_shiny['Form'] == cnstr_form]

        # check relation
        if relation == '吸引 (Attraction)':
            cnstr_table = cnstr_table[cnstr_table['Relation'] == 'attraction']
        else:
            cnstr_table = cnstr_table[cnstr_table['Relation'] == 'repulsion']

        # sort by collostruction strength
        cnstr_table = cnstr_table.sort_values(by=['Collostruction_strength'], ascending=False)

        # # select columns
        # column_display = [column_mapping.get(key) for key in column]
        # cnstr_table = cnstr_table[column_display]
        
        # slice first n rows
        cnstr_table = cnstr_table[0:n]

        # select columns
        if len(column) == 0:
            cnstr_table = cnstr_table[['Form', 'Construction', 'Context', 'Collostruction_strength']]
        else:
            column_display = [column_mapping.get(key) for key in column]
            cnstr_table = cnstr_table[column_display]
        
        return cnstr_table

    @output
    @render.plot(alt="A histogram")
    def plot() -> object:
        cnstr_form = input.cnstr_form()
        relation = input.relation()
        n = input.n()

        cnstr_table = cnstr_shiny[cnstr_shiny['Form'] == cnstr_form]

        # check relation
        if relation == '吸引 (Attraction)':
            cnstr_table = cnstr_table[cnstr_table['Relation'] == 'attraction']
        else:
            cnstr_table = cnstr_table[cnstr_table['Relation'] == 'repulsion']

        # select columns
        cnstr_table = cnstr_table[['pair', 'obs.w1_2.in_c', 'delta.p.constr.to.word',
                                    'delta.p.word.to.constr', 'Collostruction_strength']]

        # get distinct rows
        cnstr_table = cnstr_table.drop_duplicates()

        # sort by collostruction strength
        cnstr_table = cnstr_table.sort_values(by=['Collostruction_strength'], ascending=False)

        # slice first n rows
        cnstr_table = cnstr_table[0:n]

        # pivot_longer
        cnstr_table_long = cnstr_table.melt(id_vars='pair',
                                            value_vars=["obs.w1_2.in_c", "delta.p.constr.to.word",
                                            "delta.p.word.to.constr", "Collostruction_strength"],
                                            var_name='metric',
                                            value_name='strength',
                                            ignore_index=True)

        cnstr_table_long.sort_values(['metric','strength'],ascending=False)

        # plot settings
        sns.set_theme()
        matplotlib.font_manager.fontManager.addfont('data/TaipeiSansTCBeta-Regular.ttf') # 新增字體
        matplotlib.rc('font', family = 'Taipei Sans TC Beta') # 將 font-family 設為台北思源黑體
        ##plt.figure(figsize=(8,6))

        # plot bar charts
        g = sns.catplot(data=cnstr_table_long,
                        col_wrap =2,
                        kind="bar",
                        orient = "h",
                        sharex=False,
                        y="pair", x="strength", col="metric", ci=None
            )
        g.set_axis_labels("吸引程度", "詞組")
        g.set_titles('{col_name}')

        return g

app = App(app_ui, server)