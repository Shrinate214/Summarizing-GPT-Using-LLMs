import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.chains.summarize import load_summarize_chain
from transformers import T5Tokenizer,T5ForConditionalGeneration
from transformers import pipeline
import torch 
import base64

checkpoint="LaMini-Flan-T5-248M"
tokenizer=T5Tokenizer.from_pretrained(checkpoint)
base_model=T5ForConditionalGeneration.from_pretrained(checkpoint, device_map="auto",torch_dtype=torch.float32, offload_folder="C:/Users/akshat shrinate/Desktop/copper/namekart assignment/offload_weights")

def file_processing(file):
    loader=PyPDFLoader(file)
    pages=loader.load_and_split()
    text_splitter=RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=50)
    texts=text_splitter.split_documents(pages)
    final_texts=""
    for text in texts:
        print(text)
        final_texts=final_texts+text.page_content
    return final_texts
def llm_pipeline(filepath):
    pipe_sum=pipeline(
        "summarization",
        model= base_model,
        tokenizer=tokenizer,
        max_length=500,
        min_length=50
    )
    input_text=file_processing(filepath)
    result=pipe_sum(input_text)
    result = result[0]['summary_text']
    return result

@st.cache_data
def displayPDF(file):
    with open(file,"rb") as f:
        base64_pdf=base64.b64encode(f.read()).decode('utf-8')
    pdf_display=F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
    st.markdown(pdf_display,unsafe_allow_html=True)
st.set_page_config(layout='wide',page_title="Summarization App")
def main():
    st.title("Summarize Your Document Using Large Language Model")
    uploaded_file=st.file_uploader("Upload your PDF file",type=['pdf'])
    if uploaded_file is not None:
        if st.button("Summarise"):
            col1,col2=st.columns(2)
            filepath="data/"+uploaded_file.name
            with open(filepath,'wb') as temp_file:
                temp_file.write(uploaded_file.read())
                with col1:
                    st.info("Uploaded PDF File")
                    pdf_viewer=displayPDF(filepath)
                with col2:
                    st.info("Summarized Below")
                    summary=llm_pipeline(filepath)
                    st.success(summary)
                
if __name__=='__main__':
    main()






