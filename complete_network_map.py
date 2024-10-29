import pandas as pd
from pyvis.network import Network
import os
import ast
import streamlit as st

# Define the file path for your CSV
file_path = r"C:\Users\amanousi\OneDrive - SLB\Aryou\Training\G11 Project\JPT_Network_Map\All_News_Mapping_Split_Companies.csv"

# Check if the file exists
if not os.path.exists(file_path):
    st.error(f"File not found: {file_path}")
else:
    # Load your data
    news_mapping_df = pd.read_csv(file_path)
    
    # Extract unique companies from the 'Company Pair' column
    companies = set()
    for pair in news_mapping_df['Company Pair']:
        try:
            # Convert the string representation of the tuple into an actual tuple
            company_pair = ast.literal_eval(pair)
            companies.update(company_pair)
        except (ValueError, SyntaxError):
            continue
    companies = sorted(companies)  # Sort for the dropdown

    # Function to create the full network with a count threshold
    def generate_full_network_map(count_threshold=30):
        net = Network(notebook=False)
        filtered_df = news_mapping_df[news_mapping_df['Count'] > count_threshold]

        for _, row in filtered_df.iterrows():
            try:
                company1, company2 = ast.literal_eval(row['Company Pair'])
                net.add_node(company1.strip(), label=company1.strip(), title=company1.strip())
                net.add_node(company2.strip(), label=company2.strip(), title=company2.strip())
                net.add_edge(company1.strip(), company2.strip(), value=row['Count'])
            except (ValueError, SyntaxError):
                st.warning(f"Skipping invalid company pair format: {row['Company Pair']}")

        net.force_atlas_2based()
        net.show_buttons(filter_=['physics'])
        full_network_output_path = "full_network_map.html"
        net.save_graph(full_network_output_path)
        return full_network_output_path

    # Function to create a filtered network for a selected company
    def generate_filtered_network_map(selected_company, count_threshold=5):
        net = Network(notebook=False)
        filtered_df = news_mapping_df[news_mapping_df['Count'] > count_threshold]

        for _, row in filtered_df.iterrows():
            try:
                company_pair = ast.literal_eval(row['Company Pair'])
                if len(company_pair) == 2 and selected_company in company_pair:
                    company1, company2 = company_pair
                    net.add_node(company1.strip(), label=company1.strip(), title=company1.strip())
                    net.add_node(company2.strip(), label=company2.strip(), title=company2.strip())
                    net.add_edge(company1.strip(), company2.strip(), value=row['Count'])
            except (ValueError, SyntaxError):
                st.warning(f"Skipping invalid company pair format: {row['Company Pair']}")

        net.force_atlas_2based()
        net.show_buttons(filter_=['physics'])
        filtered_network_output_path = "filtered_network_map.html"
        net.save_graph(filtered_network_output_path)
        return filtered_network_output_path

    # Streamlit UI
    st.title("Company Network Map Generator")

    # Select full or filtered network
    map_type = st.radio("Select network type:", ("Full Network", "Filtered by Company"))

    if map_type == "Full Network":
        # Full network with a threshold
        st.write("Displaying full network with connections above count threshold.")
        threshold = st.slider("Select count threshold:", min_value=1, max_value=100, value=30)
        full_network_output_path = generate_full_network_map(threshold)
        st.components.v1.html(open(full_network_output_path, 'r').read(), height=600, scrolling=True)

    else:
        # Filtered network by selected company
        selected_company = st.selectbox("Select a company:", companies)
        if st.button("Generate Filtered Network Map"):
            filtered_network_output_path = generate_filtered_network_map(selected_company)
            st.components.v1.html(open(filtered_network_output_path, 'r').read(), height=600, scrolling=True)
