import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import argparse
import glob
import os

def plot_benchmark_results(csv_file):
    """
    Creates interactive plots from benchmark results CSV file using Plotly.
    """
    # Read the CSV file
    df = pd.read_csv(csv_file)
    
    # Create subplots with 2x2 layout
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Throughput vs Concurrency',
            'Success Rate vs Concurrency', 
            'Request Rate vs Concurrency',
            'Total Time vs Concurrency'
        ),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Plot 1: Tokens per Second vs Concurrent Users
    fig.add_trace(
        go.Scatter(
            x=df['concurrent_users'],
            y=df['tokens_per_second'],
            mode='lines+markers',
            name='Tokens/Sec',
            line=dict(color='blue', width=3),
            marker=dict(size=8),
            hovertemplate='<b>%{x} users</b><br>%{y:.2f} tokens/sec<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Plot 2: Success Rate vs Concurrent Users
    fig.add_trace(
        go.Scatter(
            x=df['concurrent_users'],
            y=df['success_rate'],
            mode='lines+markers',
            name='Success Rate',
            line=dict(color='green', width=3),
            marker=dict(size=8),
            hovertemplate='<b>%{x} users</b><br>%{y:.1f}%<extra></extra>'
        ),
        row=1, col=2
    )
    
    # Plot 3: Requests per Second vs Concurrent Users
    fig.add_trace(
        go.Scatter(
            x=df['concurrent_users'],
            y=df['requests_per_second'],
            mode='lines+markers',
            name='Requests/Sec',
            line=dict(color='red', width=3),
            marker=dict(size=8),
            hovertemplate='<b>%{x} users</b><br>%{y:.2f} requests/sec<extra></extra>'
        ),
        row=2, col=1
    )
    
    # Plot 4: Total Time vs Concurrent Users
    fig.add_trace(
        go.Scatter(
            x=df['concurrent_users'],
            y=df['total_time'],
            mode='lines+markers',
            name='Total Time',
            line=dict(color='purple', width=3),
            marker=dict(size=8),
            hovertemplate='<b>%{x} users</b><br>%{y:.2f} seconds<extra></extra>'
        ),
        row=2, col=2
    )
    
    # Update x-axes to linear scale for all subplots
    fig.update_xaxes(title_text="Concurrent Users", row=1, col=1)
    fig.update_xaxes(title_text="Concurrent Users", row=1, col=2)
    fig.update_xaxes(title_text="Concurrent Users", row=2, col=1)
    fig.update_xaxes(title_text="Concurrent Users", row=2, col=2)
    
    # Update y-axes
    fig.update_yaxes(title_text="Tokens per Second", range=[0, None], row=1, col=1)  # Start at 0
    fig.update_yaxes(title_text="Success Rate (%)", range=[0, 105], row=1, col=2)
    fig.update_yaxes(title_text="Requests per Second", row=2, col=1)
    fig.update_yaxes(title_text="Total Time (seconds)", row=2, col=2)
    
    # Update layout
    fig.update_layout(
        title=f'Benchmark Results: {os.path.basename(csv_file)}',
        height=800,
        width=1200,
        showlegend=False,
        template='plotly_white',
        font=dict(size=12)
    )
    
    # Save the plot
    plot_filename = csv_file.replace('.csv', '_plots.html')
    fig.write_html(plot_filename)
    
    # Also save as static image
    static_filename = csv_file.replace('.csv', '_plots.png')
    fig.write_image(static_filename, width=1200, height=800)
    
    print(f"Interactive plot saved to: {plot_filename}")
    print(f"Static plot saved to: {static_filename}")
    
    # Show the plot in browser
    fig.show()
    
    # Print summary statistics
    print("\nSummary Statistics:")
    print("=" * 50)
    print(f"Peak throughput: {df['tokens_per_second'].max():.2f} tokens/sec at {df.loc[df['tokens_per_second'].idxmax(), 'concurrent_users']} concurrent users")
    print(f"Peak request rate: {df['requests_per_second'].max():.2f} requests/sec at {df.loc[df['requests_per_second'].idxmax(), 'concurrent_users']} concurrent users")
    print(f"Average success rate: {df['success_rate'].mean():.1f}%")
    print(f"Minimum success rate: {df['success_rate'].min():.1f}% at {df.loc[df['success_rate'].idxmin(), 'concurrent_users']} concurrent users")

def compare_multiple_benchmarks(csv_files):
    """
    Compare results from multiple benchmark runs using Plotly.
    """
    fig = go.Figure()
    
    colors = px.colors.qualitative.Set1
    
    for i, csv_file in enumerate(csv_files):
        df = pd.read_csv(csv_file)
        label = os.path.basename(csv_file).replace('_benchmark_results_', ' ').replace('.csv', '').replace('_', ' ').title()
        
        fig.add_trace(
            go.Scatter(
                x=df['concurrent_users'],
                y=df['tokens_per_second'],
                mode='lines+markers',
                name=label,
                line=dict(color=colors[i % len(colors)], width=3),
                marker=dict(size=8),
                hovertemplate=f'<b>{label}</b><br>%{{x}} users<br>%{{y:.2f}} tokens/sec<extra></extra>'
            )
        )
    
    fig.update_layout(
        title='Throughput Comparison Across Benchmark Runs',
        xaxis_title='Concurrent Users',
        yaxis_title='Tokens per Second',
        yaxis=dict(range=[0, None]),  # Start at 0
        template='plotly_white',
        width=1000,
        height=600,
        font=dict(size=12),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    # Save the comparison plot
    comparison_filename = 'results/benchmark_comparison.html'
    fig.write_html(comparison_filename)
    
    # Also save as static image
    static_comparison_filename = 'results/benchmark_comparison.png'
    fig.write_image(static_comparison_filename, width=1000, height=600)
    
    print(f"Interactive comparison plot saved to: {comparison_filename}")
    print(f"Static comparison plot saved to: {static_comparison_filename}")
    fig.show()

def create_provider_comparison_chart(csv_files):
    """
    Create a comprehensive comparison chart showing multiple metrics for different providers.
    """
    provider_data = []
    
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        provider_name = os.path.basename(csv_file).split('_')[0]
        if provider_name == 'benchmark':
            provider_name = 'docker'
        
        # Get peak performance metrics
        peak_throughput = df['tokens_per_second'].max()
        peak_throughput_users = df.loc[df['tokens_per_second'].idxmax(), 'concurrent_users']
        avg_success_rate = df['success_rate'].mean()
        peak_requests_per_sec = df['requests_per_second'].max()
        
        provider_data.append({
            'Provider': provider_name.title(),
            'Peak Throughput (tokens/sec)': peak_throughput,
            'Optimal Concurrency': peak_throughput_users,
            'Average Success Rate (%)': avg_success_rate,
            'Peak Request Rate (req/sec)': peak_requests_per_sec,
            'File': csv_file
        })
    
    provider_df = pd.DataFrame(provider_data)
    
    # Create comparison bar charts
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Peak Throughput by Provider',
            'Average Success Rate by Provider',
            'Peak Request Rate by Provider', 
            'Optimal Concurrency by Provider'
        ),
        specs=[[{"type": "bar"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "bar"}]]
    )
    
    # Peak Throughput
    fig.add_trace(
        go.Bar(
            x=provider_df['Provider'],
            y=provider_df['Peak Throughput (tokens/sec)'],
            name='Peak Throughput',
            marker_color='blue',
            hovertemplate='<b>%{x}</b><br>%{y:.2f} tokens/sec<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Success Rate
    fig.add_trace(
        go.Bar(
            x=provider_df['Provider'],
            y=provider_df['Average Success Rate (%)'],
            name='Success Rate',
            marker_color='green',
            hovertemplate='<b>%{x}</b><br>%{y:.1f}%<extra></extra>'
        ),
        row=1, col=2
    )
    
    # Request Rate
    fig.add_trace(
        go.Bar(
            x=provider_df['Provider'],
            y=provider_df['Peak Request Rate (req/sec)'],
            name='Request Rate',
            marker_color='red',
            hovertemplate='<b>%{x}</b><br>%{y:.2f} req/sec<extra></extra>'
        ),
        row=2, col=1
    )
    
    # Optimal Concurrency
    fig.add_trace(
        go.Bar(
            x=provider_df['Provider'],
            y=provider_df['Optimal Concurrency'],
            name='Optimal Concurrency',
            marker_color='purple',
            hovertemplate='<b>%{x}</b><br>%{y} users<extra></extra>'
        ),
        row=2, col=2
    )
    
    fig.update_layout(
        title='Provider Performance Comparison',
        height=800,
        width=1200,
        showlegend=False,
        template='plotly_white',
        font=dict(size=12)
    )
    
    # Save the provider comparison
    provider_filename = 'results/provider_comparison.html'
    fig.write_html(provider_filename)
    
    static_provider_filename = 'results/provider_comparison.png'
    fig.write_image(static_provider_filename, width=1200, height=800)
    
    print(f"Provider comparison saved to: {provider_filename}")
    print(f"Static provider comparison saved to: {static_provider_filename}")
    fig.show()
    
    return provider_df

def main():
    parser = argparse.ArgumentParser(description='Generate interactive plots from benchmark results using Plotly')
    parser.add_argument('--csv', type=str, help='Specific CSV file to plot')
    parser.add_argument('--latest', action='store_true', help='Plot the most recent benchmark results')
    parser.add_argument('--compare', action='store_true', help='Compare all available benchmark results')
    parser.add_argument('--provider-comparison', action='store_true', help='Create provider performance comparison charts')
    
    args = parser.parse_args()
    
    if args.csv:
        if os.path.exists(args.csv):
            plot_benchmark_results(args.csv)
        else:
            print(f"Error: File {args.csv} not found")
    elif args.latest:
        # Find the most recent benchmark results file
        csv_files = glob.glob('results/benchmark_results_*.csv') + glob.glob('results/*_benchmark_results_*.csv')
        if csv_files:
            latest_file = max(csv_files, key=os.path.getctime)
            print(f"Using latest file: {latest_file}")
            plot_benchmark_results(latest_file)
        else:
            print("No benchmark results files found")
    elif args.compare:
        # Find all benchmark results files
        csv_files = glob.glob('results/benchmark_results_*.csv') + glob.glob('results/*_benchmark_results_*.csv')
        if len(csv_files) > 1:
            print(f"Comparing {len(csv_files)} benchmark files")
            compare_multiple_benchmarks(csv_files)
        else:
            print("Need at least 2 benchmark files to compare")
    elif args.provider_comparison:
        # Find all benchmark results files and create provider comparison
        csv_files = glob.glob('results/benchmark_results_*.csv') + glob.glob('results/*_benchmark_results_*.csv')
        if len(csv_files) > 1:
            print(f"Creating provider comparison from {len(csv_files)} benchmark files")
            provider_df = create_provider_comparison_chart(csv_files)
            print("\nProvider Performance Summary:")
            print(provider_df.round(2))
        else:
            print("Need at least 2 benchmark files for provider comparison")
    else:
        # If no arguments, try to plot the latest file
        csv_files = glob.glob('results/benchmark_results_*.csv') + glob.glob('results/*_benchmark_results_*.csv')
        if csv_files:
            latest_file = max(csv_files, key=os.path.getctime)
            print(f"No arguments provided, using latest file: {latest_file}")
            plot_benchmark_results(latest_file)
        else:
            print("No benchmark results files found. Run the benchmark first!")
            print("Usage examples:")
            print("  python scripts/plot_results.py --latest")
            print("  python scripts/plot_results.py --csv results/benchmark_results_20250723_143022.csv")
            print("  python scripts/plot_results.py --compare")
            print("  python scripts/plot_results.py --provider-comparison")

if __name__ == "__main__":
    main()
