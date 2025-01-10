import os
import pandas as pd
from collections import defaultdict
import argparse
import plotly.express as px
import imageio
import tempfile

def process_files_in_directory(directory):
    # Initialize a defaultdict to keep track of accumulated word counts
    accumulated_counts = defaultdict(int)
    all_data = []

    # List all files in the given directory
    file_names = sorted([f for f in os.listdir(directory) if f.startswith('palabras_') and f.endswith('.txt')])

    for file_name in file_names:
        # Extract date from file name
        date_str = file_name.replace("palabras_", "").replace(".txt", "")
        
        # Construct the full path to the file
        file_path = os.path.join(directory, file_name)
        
        # Read the words from the file
        with open(file_path, 'r') as file:
            words = file.read().splitlines()
        
        # Update accumulated word counts
        for word in words:
            accumulated_counts[word] += 1
        
        # Add a row to the dataset with the current accumulated counts
        row = {'date': date_str}
        row.update(accumulated_counts)
        all_data.append(row)
    
    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(all_data)
    
    # Fill missing values with 0 (for words not yet encountered)
    df.fillna(0, inplace=True)

    return df

def create_race_chart(df):
    # Reshape the DataFrame for Plotly
    df_melted = df.melt(id_vars=["date"], var_name="word", value_name="count")

    # Create the race chart using Plotly Express
    fig = px.bar(
        df_melted,
        x="count",
        y="word",
        color="word",
        orientation="h",
        animation_frame="date",
        range_x=[0, df_melted["count"].max() + 5],
        title="Word Frequency Over Time",
        labels={"count": "Cumulative Word Count", "word": "Words"}
    )

    # Update the layout to ensure the chart is visually appealing
    fig.update_layout(
        xaxis_title="Cumulative Word Count",
        yaxis_title="Words",
        yaxis={'categoryorder': 'total ascending'},
        showlegend=False,
        template="plotly_white"
    )

    return fig

def save_animation_as_gif(fig, gif_path, frame_duration=500):
    with tempfile.TemporaryDirectory() as temp_dir:
        # Extract all frames and save them as images
        frame_files = []
        
        for frame_number in range(len(fig.frames)):
            # Update the data in the figure with the data from the current frame
            fig.update(data=fig.frames[frame_number].data)
            
            # Update the layout with the correct frame to match the update
            fig.layout.update(fig.frames[frame_number].layout)
            
            # Add annotation with the current date in the top right corner
            current_date = fig.frames[frame_number].name
            fig.add_annotation(
                xref="paper", yref="paper",
                x=1, y=1.1,  # Adjusted position, slightly above the top right corner
                xanchor="right", yanchor="top",
                text=f"Date: {current_date}",
                showarrow=False,
                font=dict(size=14)
            )
            
            # Save the current frame as an image
            frame_path = os.path.join(temp_dir, f"frame_{frame_number}.png")
            fig.write_image(frame_path)
            frame_files.append(frame_path)
            
            # Remove the annotation for the next frame
            fig.layout.annotations = []

        # Create GIF from saved frames
        with imageio.get_writer(gif_path, mode='I', duration=frame_duration / 1000) as writer:
            for frame_file in frame_files:
                image = imageio.imread(frame_file)
                writer.append_data(image)

    print(f"GIF saved to {gif_path}")


def save_last_row_as_png(df, png_path):
    # Get the last row of the DataFrame
    last_row = df.iloc[-1]
    
    # Convert the last row to a DataFrame for plotting
    last_row_df = last_row.drop('date').reset_index()
    last_row_df.columns = ['word', 'count']
    # Sort by count and select the top 15 words
    top_15_words_df = last_row_df.sort_values(by='count', ascending=False).head(15)
    
    # Create a bar plot using Plotly Express
    fig = px.bar(
        top_15_words_df,
        x='count',
        y='word',
        orientation='h',
        title=f"Word Frequency on {last_row['date']}",
        labels={"count": "Cumulative Word Count", "word": "Words"}
    )
    
    fig.update_layout(
        xaxis_title="Cumulative Word Count",
        yaxis_title="Words",
        yaxis={'categoryorder': 'total ascending'},
        showlegend=False,
        template="plotly_white",
        margin=dict(l=150, r=50, t=50, b=50)  # Adjust margins to ensure all rows are visible
    )

    # Save the plot as a PNG file
    fig.write_image(png_path)
    print(f"PNG saved to {png_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process text files and accumulate word counts.")
    parser.add_argument("input_dir", type=str, help="Directory containing the input text files.")
    parser.add_argument("--output_gif", type=str, help="Path to save the output GIF animation.")
    parser.add_argument("--output_csv", type=str, help="Path to save the output CSV file.")
    parser.add_argument("--output_png", type=str, help="Path to save the bar plot of the last row as a PNG file.")
    parser.add_argument("--show_animation", action="store_true", help="Show the animation in a window.")
    
    args = parser.parse_args()
    
    df = process_files_in_directory(args.input_dir)

    fig = create_race_chart(df)

    if args.output_csv:
        df.to_csv(args.output_csv, index=False)

    if args.output_gif:
        save_animation_as_gif(fig, args.output_gif)
    
    if args.show_animation:
        fig.show()

    if args.output_png:
        save_last_row_as_png(df, args.output_png)
