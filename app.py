import pandas as pd
import streamlit as st
import plotly.graph_objects as go


def get_formated_file(file):
    name = "_".join((file.name.split("_"))[0:2])
    return (name, pd.read_json(file, lines=True))
def get_custome_text_list(df,cols):
    custome_text=[]
    columns_list=list(df)
    for i in range(len(df)):
        text="""
        {}:{}
        {}:{:.2f}
        {}:{:.2f}
        {}:{:.2f}""".format(columns_list[cols[0]],df[columns_list[cols[0]]][i],
                                                   columns_list[cols[1]],float(df[columns_list[cols[1]]][i]),
                                                   columns_list[cols[2]],float(df[columns_list[cols[2]]][i]),
                                                   columns_list[cols[3]],float(df[columns_list[cols[3]]][i]),
                                                   )
        custome_text.append(text)
    return custome_text

if "data" not in st.session_state:
    st.session_state["data"] = {}
rad = st.sidebar.radio("Navigation", ["Home", "upload files", "compare data"])
if rad == "Home":
    st.write(
        """
             This is small application to compare and visualize the data  
             You can compare and visualize the data in two steps  
             1. Upload the data files (must be in jsonl format) in upload files section  
             2. Select two models from dropdown menu in the compare section
             """
    )
if rad == "upload files":
    st.session_state["data"].clear()
    text = "please select the files from your system"
    uploads = st.sidebar.file_uploader(
        "upload data set files in jsonl format",
        accept_multiple_files=True,
        type=[".jsonl"],
    )
    if len(uploads) > 0:
        text = "files are successfully uploaded you can move to next section to compare the data"
    for file in uploads:
        key, value = get_formated_file(file)
        st.session_state["data"][key] = value
    st.write(text)
    
    if(len(uploads)>0):
        st.write("The uploaded files contain the following data: ")
        for k,v in st.session_state["data"].items():
            st.write(v)

if rad == "compare data":
    files_list = st.session_state["data"]
    if len(files_list) <=1 :
        st.write("please upload more than one file")
    elif len(files_list) > 1:
        options = st.sidebar.multiselect(
            "please select 2 models for comparison", list(files_list.keys())
        )
        if len(options) == 2:
            df1 = files_list[options[0]]
            df2 = files_list[options[1]]
            df1_cols = list(df1)
            df2_cols = list(df2)
            dataframe_long = pd.DataFrame(
                {
                    df1_cols[0]: df1[df1_cols[0]],
                    options[0] + "_cer": df1[df1_cols[1]] * 100,
                    options[1] + "_cer": df2[df2_cols[1]] * 100,
                    options[0] + "_wer": df1[df1_cols[2]] * 100,
                    options[1] + "_wer": df2[df2_cols[2]] * 100,
                    "per_change_cer": (1 - (df1[df1_cols[1]] / df2[df1_cols[1]])) * 100,
                    "per_change_wer": (1 - (df1[df1_cols[2]] / df2[df1_cols[2]])) * 100,
                }
            )
            
            
            def color_survived(val):
                color = "green" if val > 0 else "red"
                return f"background-color: {color}"

            st.markdown(
                """
                #### Comparing <span style= "color:green">{} </span> with <span style= "color:green">{}</span> based on their wer and cer scores
                """.format(options[0],options[1]),
                unsafe_allow_html=True
            )
            st.dataframe(
                dataframe_long.style.applymap(
                    color_survived, subset=["per_change_wer", "per_change_cer"]
                )
            )
            st.text("Lower the value better the accuracy of the model")
            mean_cer1=dataframe_long[dataframe_long.columns[1]].mean()
            mean_cer2=dataframe_long[dataframe_long.columns[2]].mean()
            mean_wer1=dataframe_long[dataframe_long.columns[3]].mean()
            mean_wer2=dataframe_long[dataframe_long.columns[4]].mean()
            st.markdown(
                """
                <span style="color:green">{}</span> model has <span style="color:green">[{:.4f}]</span> better average CER score than <span style="color:red">{}</span> model <span style="color:red">[{:.4f}]</span>
                """.format(options[0] if mean_cer1 <= mean_cer2 else options[1],
                           float(mean_cer1 if mean_cer1 <= mean_cer2 else mean_cer2),
                           options[0] if mean_cer1 > mean_cer2 else options[1],
                           float(mean_cer1 if mean_cer1 > mean_cer2 else mean_cer2)),unsafe_allow_html=True)
            st.markdown(
                """
                <span style="color:green">{}</span> model has <span style="color:green">[{:.4f}]</span> better average WER score than <span style="color:red">{}</span> model <span style="color:red">[{:.4f}]</span>
                """.format(options[0] if mean_wer1 <= mean_wer2 else options[1],
                           float(mean_wer1 if mean_wer1 <= mean_wer2 else mean_wer2),
                           options[0] if mean_wer1 > mean_wer2 else options[1],
                           float(mean_wer1 if mean_wer1 > mean_wer2 else mean_wer2)),unsafe_allow_html=True)
            st.markdown(
                """
                        ### Character Error Count (CER) Distribution
                        """
            )
            
            bar_chart_cer = go.Figure()
            bar_chart_cer.add_trace(
                go.Bar(
                    x=dataframe_long["dataset"],
                    y=dataframe_long[options[0] + "_cer"],
                    name=options[0],
                    marker_color="yellow",
                )
            )
            bar_chart_cer.add_trace(
                go.Bar(
                    x=dataframe_long["dataset"],
                    y=dataframe_long[options[1] + "_cer"],
                    name=options[1],
                    marker_color="brown",
                )
            )
            bar_chart_cer.update_traces(
                texttemplate="%{text:.2s}", textposition="outside"
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
                uniformtext_minsize=8,
                uniformtext_mode="hide",
            )
            st.plotly_chart(bar_chart_cer)
            st.markdown(
                """
                        ### Word Error Count (WER) Distribution
                        """
            )
            bar_chart_wer = go.Figure()
            bar_chart_wer.add_trace(
                go.Bar(
                    x=dataframe_long["dataset"],
                    y=dataframe_long[options[0] + "_wer"],
                    name=options[0],
                    marker_color="yellow",
                )
            )
            bar_chart_wer.add_trace(
                go.Bar(
                    x=dataframe_long["dataset"],
                    y=dataframe_long[options[1] + "_wer"],
                    name=options[1],
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
            columns_list=list(dataframe_long)
            st.plotly_chart(bar_chart_wer)
            candle_stick_cer=go.Figure(data=[go.Candlestick(
                x=dataframe_long[columns_list[0]],
                open=dataframe_long[columns_list[1]],
                high=dataframe_long[columns_list[2]],
                low=dataframe_long[columns_list[1]],
                close=dataframe_long[columns_list[2]],
                text=get_custome_text_list(dataframe_long,[0,1,2,5]),
                hoverinfo="text"
                )])
            candle_stick_cer.update_layout(xaxis_rangeslider_visible=False,template="plotly_dark")
            candle_stick_cer.update_layout(xaxis_title="DataSet",yaxis_title="CER",title="CER Distribution (candlesticks)")
            st.plotly_chart(candle_stick_cer,use_container_width=True)
            positive=(dataframe_long[columns_list[5]] > 0).sum()
            negative=len(dataframe_long)-positive
            st.write("""
                     we got {} positive outcomes and {} negative outcomes when {} model is compared with {} model
                     """.format(positive,negative,options[0],options[1]),unsafe_allow_html=True)
            candle_stick_wer=go.Figure(data=[go.Candlestick(
                x=dataframe_long[columns_list[0]],
                open=dataframe_long[columns_list[3]],
                high=dataframe_long[columns_list[4]],
                low=dataframe_long[columns_list[3]],
                close=dataframe_long[columns_list[4]],
                text=get_custome_text_list(dataframe_long,[0,3,4,6]),
                hoverinfo="text"
                )])
            candle_stick_wer.update_layout(xaxis_rangeslider_visible=False,template="plotly_dark")
            candle_stick_wer.update_layout(xaxis_title="DataSet",yaxis_title="WER",title="WER Distribution (candlesticks)")
            st.plotly_chart(candle_stick_wer,use_container_width=True)
            positive=(dataframe_long[columns_list[6]] > 0).sum()
            negative=len(dataframe_long)-positive
            st.write("""
                     we got {} positive outcomes and {} negative outcomes when {} model is compared with {} model
                     """.format(positive,negative,options[0],options[1]),unsafe_allow_html=True)
        else:
            st.write("please select only two models for comparison")
    else:
        st.write("Please select two models for comparison")
