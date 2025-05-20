from django.shortcuts import render
from django.views import View
import json
from django.http import JsonResponse
from main.session import DatabaseSessionManager

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings('ignore')

def visualize_dataframe(df):
    """
    Automatically visualizes a pandas DataFrame with 6 different charts,
    prioritizing numerical columns, and saves the output as a PNG file.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        The input DataFrame to visualize.
    
    Returns:
    --------
    str
        The path to the saved PNG file.
    """
    try:
        # Make a copy to avoid modifying the original dataframe
        data = df.copy()
        
        # Get numerical and categorical columns
        numerical_cols = data.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = data.select_dtypes(exclude=['number']).columns.tolist()
        
        # Create figure and grid for subplots
        fig = plt.figure(figsize=(20, 15))
        gs = GridSpec(3, 2, figure=fig)
        
        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['axes.labelsize'] = 12
        plt.rcParams['axes.titlesize'] = 14
        plt.rcParams['xtick.labelsize'] = 10
        plt.rcParams['ytick.labelsize'] = 10
        
        # Color palette
        palette = sns.color_palette("viridis", 10)
        
        # CHART 1: Correlation Heatmap (for numerical columns)
        ax1 = fig.add_subplot(gs[0, 0])
        if len(numerical_cols) > 1:
            corr = data[numerical_cols].corr()
            mask = np.triu(np.ones_like(corr, dtype=bool))
            sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="coolwarm", 
                       square=True, linewidths=.5, cbar_kws={"shrink": .8}, ax=ax1)
            ax1.set_title("Correlation Heatmap")
        else:
            ax1.text(0.5, 0.5, "Not enough numerical columns for correlation", 
                     ha='center', va='center', fontsize=12)
            ax1.set_title("Correlation Heatmap (Not Available)")
        
        # CHART 2: Distribution of numerical columns
        ax2 = fig.add_subplot(gs[0, 1])
        if numerical_cols:
            selected_num_cols = numerical_cols[:5] if len(numerical_cols) > 5 else numerical_cols
            melted_data = data[selected_num_cols].melt()
            sns.boxplot(x="variable", y="value", data=melted_data, palette=palette, ax=ax2)
            ax2.set_title("Distribution of Numerical Features")
            ax2.set_xlabel("")
            ax2.set_ylabel("Value")
            plt.xticks(rotation=45)
        else:
            ax2.text(0.5, 0.5, "No numerical columns found", ha='center', va='center', fontsize=12)
            ax2.set_title("Distribution of Numerical Features (Not Available)")
        
        # CHART 3: First numerical column distribution
        ax3 = fig.add_subplot(gs[1, 0])
        if numerical_cols:
            main_num_col = numerical_cols[0]
            sns.histplot(data[main_num_col], kde=True, color=palette[0], ax=ax3)
            mean_val = data[main_num_col].mean()
            median_val = data[main_num_col].median()
            ax3.axvline(mean_val, color='red', linestyle='--', label=f'Mean: {mean_val:.2f}')
            ax3.axvline(median_val, color='green', linestyle='-.', label=f'Median: {median_val:.2f}')
            ax3.set_title(f"Distribution of {main_num_col}")
            ax3.legend()
        else:
            ax3.text(0.5, 0.5, "No numerical columns found", ha='center', va='center', fontsize=12)
            ax3.set_title("Distribution (Not Available)")
        
        # CHART 4: Top categorical column distribution
        ax4 = fig.add_subplot(gs[1, 1])
        if categorical_cols:
            cat_col = categorical_cols[0]
            value_counts = data[cat_col].value_counts().nlargest(10)
            sns.barplot(x=value_counts.index, y=value_counts.values, palette=palette, ax=ax4)
            ax4.set_title(f"Top 10 Categories in {cat_col}")
            ax4.set_xlabel(cat_col)
            ax4.set_ylabel("Count")
            plt.xticks(rotation=45, ha='right')
        elif numerical_cols:
            num_col = numerical_cols[1] if len(numerical_cols) > 1 else numerical_cols[0]
            sns.histplot(data[num_col], bins=10, kde=False, color=palette[2], ax=ax4)
            ax4.set_title(f"Binned Distribution of {num_col}")
        else:
            ax4.text(0.5, 0.5, "No categorical or numerical columns found", 
                     ha='center', va='center', fontsize=12)
            ax4.set_title("Categorical Distribution (Not Available)")
        
        # CHART 5: Scatter plot of top 2 numerical columns
        ax5 = fig.add_subplot(gs[2, 0])
        if len(numerical_cols) >= 2:
            x_col, y_col = numerical_cols[0], numerical_cols[1]
            if categorical_cols:
                hue_col = categorical_cols[0]
                if data[hue_col].nunique() > 5:
                    top_cats = data[hue_col].value_counts().nlargest(5).index
                    plot_data = data[data[hue_col].isin(top_cats)]
                else:
                    plot_data = data
                    
                sns.scatterplot(x=x_col, y=y_col, hue=hue_col, data=plot_data, 
                               palette=palette, alpha=0.7, ax=ax5)
                ax5.set_title(f"{x_col} vs {y_col} by {hue_col}")
            else:
                sns.scatterplot(x=x_col, y=y_col, data=data, color=palette[3], alpha=0.7, ax=ax5)
                ax5.set_title(f"{x_col} vs {y_col}")
        else:
            ax5.text(0.5, 0.5, "Not enough numerical columns for scatter plot", 
                     ha='center', va='center', fontsize=12)
            ax5.set_title("Scatter Plot (Not Available)")
        
        # CHART 6: Time series or bubble chart
        ax6 = fig.add_subplot(gs[2, 1])
        date_col = None
        for col in data.columns:
            try:
                pd.to_datetime(data[col])
                date_col = col
                break
            except:
                continue
        
        if date_col is not None and numerical_cols:
            data[date_col] = pd.to_datetime(data[date_col])
            data = data.sort_values(by=date_col)
            num_col = numerical_cols[0]
            if data[date_col].nunique() > 20:
                data['year_month'] = data[date_col].dt.to_period('M')
                grouped = data.groupby('year_month')[num_col].mean().reset_index()
                grouped['year_month'] = grouped['year_month'].astype(str)
                sns.lineplot(x='year_month', y=num_col, data=grouped, color=palette[4], marker='o', ax=ax6)
                if len(grouped) > 10:
                    n_ticks = 10
                    step = max(1, len(grouped) // n_ticks)
                    ax6.set_xticks(range(0, len(grouped), step))
                    ax6.set_xticklabels(grouped['year_month'].iloc[::step])
            else:
                sns.lineplot(x=date_col, y=num_col, data=data, color=palette[4], marker='o', ax=ax6)
            
            plt.xticks(rotation=45, ha='right')
            ax6.set_title(f"{num_col} Over Time")
        elif len(numerical_cols) >= 3:
            x_col, y_col, size_col = numerical_cols[0], numerical_cols[1], numerical_cols[2]
            size_values = (data[size_col] - data[size_col].min()) / (data[size_col].max() - data[size_col].min()) * 200 + 20
            
            scatter = ax6.scatter(data[x_col], data[y_col], s=size_values, c=size_values, 
                                cmap='viridis', alpha=0.6)
            
            plt.colorbar(scatter, ax=ax6, label=size_col)
            
            ax6.set_title(f"Bubble Chart: {x_col} vs {y_col} (size: {size_col})")
            ax6.set_xlabel(x_col)
            ax6.set_ylabel(y_col)
        else:
            ax6.text(0.5, 0.5, "Not enough columns for additional visualization", 
                     ha='center', va='center', fontsize=12)
            ax6.set_title("Additional Visualization (Not Available)")
        
        # Adjust layout and add title
        plt.tight_layout()
        plt.suptitle("Comprehensive Data Visualization", fontsize=18, y=1.02)
        
        # Save the visualization in the static directory
        import os
        from django.conf import settings
        
        # Create static directory if it doesn't exist
        static_dir = os.path.join(settings.BASE_DIR, 'static')
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)
        
        # Check for existing visualization files and clean them up
        visualization_files = [f for f in os.listdir(static_dir) if f.startswith('visualization') and f.endswith('.png')]
        for file in visualization_files:
            try:
                os.remove(os.path.join(static_dir, file))
            except Exception as e:
                print(f"Error deleting old visualization file {file}: {str(e)}")
        
        # Generate a unique filename using timestamp
        import time
        timestamp = int(time.time())
        filename = f'visualization_{timestamp}.png'
        save_path = os.path.join(static_dir, filename)
        
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
        plt.close()
        
        return filename
        
    except Exception as e:
        plt.close()  # Ensure the figure is closed even if an error occurs
        raise Exception(f"Error generating visualization: {str(e)}")

class VisualizationView(View):
    @staticmethod
    def visualization(request):
        return render(request,'main/visualization.html')
    
    @staticmethod
    def generate_visualization(request):
        session_manager = DatabaseSessionManager()
        user_id = request.session['user']
        
        if not session_manager.validate_session(user_id):
            session_manager.create_session(user_id, request.session['user_name'])
        try:
            session = session_manager.get_session(user_id)
            if session["db_type"] == "mongoDB" or session["db_type"] == "mysql" or session["db_type"] == "postgres":
                df = session['data_frame']
                fig_path = visualize_dataframe(df)
                return JsonResponse({'fig': '/static/' + fig_path})
            elif session["db_type"] == "pandas":
                df = session['pandas_df']
                fig_path = visualize_dataframe(df)
                return JsonResponse({'fig': '/static/' + fig_path})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        