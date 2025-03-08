import streamlit as st
import time
import os
from dotenv import load_dotenv

from ncbi_utils import search_gene_papers, fetch_paper_details, get_gene_info
from openai_utils import analyze_papers

load_dotenv()

st.set_page_config(
    page_title="Gene Research Assistant",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""...""", unsafe_allow_html=True)

st.title("Gene Research Assistant")

with st.sidebar:
    st.header("Search Parameters")

    gene_name = st.text_input("Gene & SNP Input", value="")
    search_btn = st.button("Analyze", type='primary')

if search_btn:
    if not gene_name:
        st.error("Enter Gene")
    else:
        tabs = st.tabs(["Research Papers", "Analysis"])

        with st.spinner(f"Researching for {gene_name}"):
            combined_info = get_gene_info(gene_name)
            max_results = 20
            custom_date_range = None

            with tabs[0]:
                st.header(f"Research paper for {gene_name}")

                pmids = search_gene_papers(gene_name, max_results, custom_date_range)

                if not pmids:
                    st.warning(f"No paper found for {gene_name}. Try a different parameters")
                else:
                    st.success(f"Found {len(pmids)} papers.")
                    
                    papers = fetch_paper_details(pmids)

                    for i, paper in enumerate(papers):
                        with st.expander(f"{i+1}. {paper['title']}"):
                            st.markdown(f"**Authors:** {paper['author']}")
                            st.markdown('...')
            
            with tabs[1]:
                st.header(f"Analysis for {gene_name}")

                if not pmids:
                    st.warning("No paper to analyze.")
                else:
                    papers = fetch_paper_details(pmids)

                    snp_id = combined_info.get("snp_info", {}).get("rs_id", "")
                    genotype = combined_info.get("snp_info", {}).get("genotype", "")

                    with st.spinner("Generating analysis..."):
                        analysis = analyze_papers(papers, gene_name, snp_id=snp_id, genotype=genotype)
                        st.markdown(analysis)

st.markdown("---")

if not os.getenv("OPENAI_API_KEY"):
    st.sidebar.warning("Openai api key not found. Make sure it's added in the .env file")
