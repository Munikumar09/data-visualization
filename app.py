import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# takes the file and returns the name and data of the files in as dataframe
def get_formated_file(file):
    name = "_".join((file.name.split("_"))[0:2])
    return (name, pd.read_json(file, lines=True))


# returns the color based on the value
def color_survived(df):
    return (
        ["background-color: rgb(2, 97, 3)"] * len(df)
        if df.per_change_cer > 0
        else ["background-color: rgb(186,0,0)"] * len(df)
    )


# save the files in the session_state
if "data" not in st.session_state:
    st.session_state["data"] = {}

text = "please upload the files from your system"
# file uploader
uploads = st.sidebar.file_uploader(
    "upload data set files in jsonl format",
    accept_multiple_files=True,
    type=[".jsonl"],
)
# storing file name and data as dataframe inside session_state
for file in uploads:
    key, value = get_formated_file(file)
    st.session_state["data"][key] = value
df_list = st.session_state["data"]
# check that more than 2 files are uploaded or not
if len(df_list) <= 1:
    st.write("please upload atleast two files")
elif len(df_list) > 1:
    # if uploaded files are more than 2 then showing the dropdown widget
    selected_options = st.sidebar.multiselect(
        "please select 2 models for comparison", list(df_list.keys())
    )
    if len(selected_options) == 2:
        # retriving the selected dataframes from dataframe list
        df1 = df_list[selected_options[0]]
        df2 = df_list[selected_options[1]]
        df1_cols = list(df1)
        df2_cols = list(df2)
        # constructing a overall dataframe from the two dataframes
        final_dataframe = pd.DataFrame(
            {
                df1_cols[0]: df1[df1_cols[0]],
                selected_options[0] + "_cer": df1[df1_cols[1]] * 100,
                selected_options[1] + "_cer": df2[df2_cols[1]] * 100,
                selected_options[0] + "_wer": df1[df1_cols[2]] * 100,
                selected_options[1] + "_wer": df2[df2_cols[2]] * 100,
                "per_change_cer": (1 - (df1[df1_cols[1]] / df2[df1_cols[1]])) * 100,
                "per_change_wer": (1 - (df1[df1_cols[2]] / df2[df1_cols[2]])) * 100,
            }
        )

        st.markdown(
            """
            #### Comparing <span style= "color:green">{} </span> with <span style= "color:green">{}</span> based on their wer and cer scores
            """.format(
                selected_options[0], selected_options[1]
            ),
            unsafe_allow_html=True,
        )
        # coloring the rows bases on the cer scores
        st.dataframe(final_dataframe.style.apply(color_survived, axis=1))
        st.text("Lower the value better the accuracy of the model")
        # calculating the mean values of cer and wer scores
        mean_cer1 = final_dataframe[final_dataframe.columns[1]].mean()
        mean_cer2 = final_dataframe[final_dataframe.columns[2]].mean()
        mean_wer1 = final_dataframe[final_dataframe.columns[3]].mean()
        mean_wer2 = final_dataframe[final_dataframe.columns[4]].mean()
        # comparing the results based on the cer mean value
        st.markdown(
            """
            <span style="color:green">{}</span> model has <span style="color:green">[{:.4f}]</span> better average CER score than <span style="color:red">{}</span> model <span style="color:red">[{:.4f}]</span>
            """.format(
                selected_options[0] if mean_cer1 <= mean_cer2 else selected_options[1],
                float(mean_cer1 if mean_cer1 <= mean_cer2 else mean_cer2),
                selected_options[0] if mean_cer1 > mean_cer2 else selected_options[1],
                float(mean_cer1 if mean_cer1 > mean_cer2 else mean_cer2),
            ),
            unsafe_allow_html=True,
        )
        # comparing the results based on the wer mean value
        st.markdown(
            """
            <span style="color:green">{}</span> model has <span style="color:green">[{:.4f}]</span> better average WER score than <span style="color:red">{}</span> model <span style="color:red">[{:.4f}]</span>
            """.format(
                selected_options[0] if mean_wer1 <= mean_wer2 else selected_options[1],
                float(mean_wer1 if mean_wer1 <= mean_wer2 else mean_wer2),
                selected_options[0] if mean_wer1 > mean_wer2 else selected_options[1],
                float(mean_wer1 if mean_wer1 > mean_wer2 else mean_wer2),
            ),
            unsafe_allow_html=True,
        )
        # CER bar chart
        st.markdown(
            """
                    ### Character Error Count (CER) Distribution
                    """
        )

        bar_chart_cer = go.Figure()
        bar_chart_cer.add_trace(
            go.Bar(
                x=final_dataframe["dataset"],
                y=final_dataframe[selected_options[0] + "_cer"],
                name=selected_options[0],
                marker_color="yellow",
            )
        )
        bar_chart_cer.add_trace(
            go.Bar(
                x=final_dataframe["dataset"],
                y=final_dataframe[selected_options[1] + "_cer"],
                name=selected_options[1],
                marker_color="brown",
            )
        )
        bar_chart_cer.update_layout(
            yaxis=dict(
                title="CER (%)",
                titlefont_size=16,
                tickfont_size=14,
            ),
            xaxis=dict(
                title="DataSet",
                titlefont_size=16,
                tickfont_size=14,
            ),
            barmode="group",
        )
        st.plotly_chart(bar_chart_cer, use_container_width=True)
        # WER bar chart
        st.markdown(
            """
                    ### Word Error Count (WER) Distribution
                    """
        )
        bar_chart_wer = go.Figure()
        bar_chart_wer.add_trace(
            go.Bar(
                x=final_dataframe["dataset"],
                y=final_dataframe[selected_options[0] + "_wer"],
                name=selected_options[0],
                marker_color="yellow",
            )
        )
        bar_chart_wer.add_trace(
            go.Bar(
                x=final_dataframe["dataset"],
                y=final_dataframe[selected_options[1] + "_wer"],
                name=selected_options[1],
                marker_color="brown",
            )
        )
        bar_chart_wer.update_layout(
            yaxis=dict(
                title="WER (%)",
                titlefont_size=16,
                tickfont_size=14,
            ),
            xaxis=dict(
                title="DataSet",
                titlefont_size=16,
                tickfont_size=14,
            ),
            barmode="group",
        )
        st.plotly_chart(bar_chart_wer, use_container_width=True)
    else:
        st.write("please select only two models for comparison")
