import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import io

cmap = ListedColormap(['#67001F', '#B2182B', '#D6604D', '#F4A582', '#FDDBC7', '#FFFFFF', '#D1E5F0', '#92C5DE', '#4393C3', '#2166AC', '#053061'])

class pochbotGraphs:
    def individual_sites_graph(df):

        plt.style.use('dark_background')
        fig, ax = plt.subplots()

        counts = df['Date'].value_counts().sort_index(ascending=True)
        dates = counts.index
        payouts = counts.values

        ax.set_xlabel('Date')
        ax.set_ylabel('Payouts')

        ax.yaxis.grid()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)

        ax.scatter(dates, payouts, marker='.', s = 75, color = '#47a0ff')
        ax.plot(counts, color = '#47a0ff')
        # number of dates and calculate the step size for x-axis ticks
        num_dates = len(dates)
        tick_positions = [0, num_dates // 3, 2 * num_dates // 3, num_dates - 1]
        tick_labels = [dates[i] for i in tick_positions]
        plt.xticks(tick_positions, tick_labels, color='white')
        plt.savefig('graph.png', transparent=True)
        plt.close(fig)
        with open('graph.png', 'rb') as f:
            file = io.BytesIO(f.read())
        return file
    
    def total_sites_done_total(df):
        plt.style.use('dark_background')
        colors = ['red', 'blue', 'purple', 'orange', 'green', 'brown', '#87cbb9', '#577d86', '#660000', '#b36880']
        plt.pie(df['TotalPayout'], labels=df['Name'],autopct='%1.1f%%', colors=colors)
        plt.savefig('graph.png', transparent=True)
        plt.close()
        with open('graph.png', 'rb') as f:
            file = io.BytesIO(f.read())
        return file