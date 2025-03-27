import streamlit as st
import pandas as pd
from scipy import stats

def perform_statistical_tests(data, test_type='ttest'):
    results = []
    columns = data.columns

    # Perform all pairwise comparisons
    for i in range(len(columns)):
        for j in range(i + 1, len(columns)):
            col1 = columns[i]
            col2 = columns[j]

            # Remove missing values
            sample1 = data[col1].dropna()
            sample2 = data[col2].dropna()

            if len(sample1) < 2 or len(sample2) < 2:
                st.warning(f"Skipping {col1} vs {col2} - not enough data points")
                continue

            # Perform the selected test
            if test_type == 'ttest':
                try:
                    _, p_value = stats.ttest_ind(sample1, sample2, equal_var=True)
                except Exception as e:
                    st.error(f"Error in t-test between {col1} and {col2}: {str(e)}")
                    continue
            elif test_type == 'mannwhitney':
                try:
                    _, p_value = stats.mannwhitneyu(sample1, sample2, alternative='two-sided')
                except Exception as e:
                    st.error(f"Error in Mann-Whitney U test between {col1} and {col2}: {str(e)}")
                    continue

            # Format p-value and determine significance
            formatted_p = f"{p_value:.10f}"
            significance = "sig" if p_value < 0.05 else "nonsig"

            results.append({
                'Comparison': f"{col1} vs {col2}",
                'p-value': formatted_p,
                'Significance': significance
            })

    return pd.DataFrame(results)

def main():
    st.set_page_config(layout="centered")  # Disable wide mode
    st.title("Simple Statistical Comparison of Multiple Samples", help=None, anchor=None)
    # st.markdown("""
    # **Compare samples using:**
    # - Unpaired two-sample t-test (parametric)
    # - Wilcoxon rank-sum test (nonparametric/Mann-Whitney U)
    # """)

    # Create a sample dataframe for demonstration
    df = pd.DataFrame({
        'Sample1': [1, 2, 3, 4, 5, None, 7],
        'Sample2': [2, 3, 4, 5, 6, 7, 8],
        'Sample3': [5, 6, 7, 8, 9, 10, 11],
        'Sample4': [1, 1, 2, 2, 3, 3, 4],
        'Sample5': [10, 11, 12, 13, 14, 15, 16],
        'Sample6': [3, 4, 5, 6, 7, 8, 9]
    })

    # Data editor for manual input
    st.subheader("Data")

    # Add ability to rename columns
    rename_all = st.checkbox("Rename all samples", value=False)

    if rename_all:
        new_names = []
        for i, col in enumerate(df.columns):
            new_name = st.text_input(f"{col}", value=col)
            new_names.append(new_name)
        df.columns = new_names

    edited_df = st.data_editor(df, num_rows="dynamic")

    # Remove completely empty columns
    edited_df = edited_df.dropna(axis=1, how='all')

    # Select test type
    test_type = st.radio(
        "Select statistical test",
        options=['ttest', 'mannwhitney'],
        format_func=lambda x: "Unpaired two-sample t-test (parametric)" if x == 'ttest' else "Wilcoxon rank-sum test (non-parametric/Mann-Whitney U)"
    )

    # Auto-run when test type changes or data is edited
    if len(edited_df.columns) >= 2:
        results_df = perform_statistical_tests(edited_df, test_type)
        if len(results_df) > 0:
            st.subheader("Results")
            st.dataframe(results_df)
        else:
            st.warning("No valid comparisons could be made. Check your data.")

if __name__ == "__main__":
    main()
