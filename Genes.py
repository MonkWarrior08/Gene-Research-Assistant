import streamlit as st
import time
import os
from dotenv import load_dotenv

from ncbi_util import search_gene_paper, fetch_paper_details, get_gene_info
from openai_util import analyze_papers

load_dotenv()

st.set_page_config(
    page_title="Research Assistant",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add a sidebar menu for navigation (this is optional since Streamlit will automatically
# add navigation for pages in the pages/ directory)
with st.sidebar:    
    st.header("Search Parameters")
    gene_name = st.text_input("Gene & SNP Input", value="")
    search_btn = st.button("Analyze", type='primary')
    
    st.markdown("---")
    st.header("About Gene Research")
    st.markdown("""
    This assistant uses:
    - **NCBI/PubMed API** for scientific gene research and paper retrieval
    - **OpenAI GPT-3.5 Turbo** for intelligent analysis of research findings
    """)

st.title("Gene Research Assistant")
st.markdown("""
This AI assistant searches the National Center for Biotechnology Information (NCBI) 
for scientific research on genes and provides a detailed analysis.

Enter a gene name or SNP identifier in the sidebar to begin.
""")

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

                pmids = search_gene_paper(gene_name, max_results, custom_date_range)

                if not pmids:
                    st.warning(f"No paper found for {gene_name}. Try a different parameters")
                else:
                    st.success(f"Found {len(pmids)} papers.")
                    
                    papers = fetch_paper_details(pmids)

                    for i, paper in enumerate(papers):
                        with st.expander(f"{i+1}. {paper['title']}"):
                            st.markdown(f"**Authors:** {paper['author']}")
                            st.markdown(f"**Journal:** {paper['journal']}")
                            st.markdown(f"**Publication Date:** {paper['publication_date']}")
                            if paper['doi']:
                                st.markdown(f"**DOI:** {paper['doi']}")
                            st.markdown(f"**PMID:** {paper['pmid']}")
                            st.markdown(f"**URL:** [PubMed Link]({paper['url']})")
                            
                            st.markdown("### Abstract")
                            if paper['abstract']:
                                st.markdown(paper['abstract'])
                            else:
                                st.info("No abstract available for this paper.")
            
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