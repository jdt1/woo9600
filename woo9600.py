from woocommerce import API
from datetime import datetime, timedelta
import json
from typing import List, Dict, Tuple
import statistics
from collections import defaultdict

def print_retro_header():
    """Print a cool retro-style header."""
    header = """
╔═════════════════════════════════════════════════════════════════════════════╗
║                    W O O C O M M E R C E   A N A L Y T I C S                ║
║                        [ Sales Performance Monitor ]                        ║
╚═════════════════════════════════════════════════════════════════════════════╝
"""
    return header

class WooCommerceAnalytics:
    def __init__(self, url: str, consumer_key: str, consumer_secret: str):
        self.wcapi = API(
            url=url,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            version="wc/v3",
            timeout=60
        )

    def get_sales_data(self, days: int = 30) -> List[Dict]:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        all_orders = []
        page = 1

        while True:
            orders = self.wcapi.get("orders", params={
                'after': start_date.isoformat(),
                'before': end_date.isoformat(),
                'per_page': 100,
                'page': page,
                'status': 'completed'
            }).json()

            if not orders:
                break

            all_orders.extend(orders)
            page += 1

        return all_orders

    def aggregate_daily_sales(self, orders: List[Dict]) -> Dict[str, int]:
        daily_sales = defaultdict(int)
        for order in orders:
            date = datetime.fromisoformat(order['date_created']).strftime('%Y-%m-%d')
            daily_sales[date] += 1
        return dict(sorted(daily_sales.items()))

    def calculate_moving_average(self, data: List[int], window: int, weights: List[float] = None) -> List[float]:
        if weights is None:
            weights = [1/window] * window

        if len(weights) != window:
            raise ValueError("Length of weights must equal window size")

        if abs(sum(weights) - 1) > 1e-10:
            raise ValueError("Weights must sum to 1")

        result = []
        for i in range(len(data)):
            if i < window - 1:
                result.append(None)
                continue

            weighted_sum = sum(w * v for w, v in zip(weights, data[i-window+1:i+1]))
            result.append(round(weighted_sum, 2))

        return result

class RetroASCIIGraph:
    def __init__(self):
        self.height = 20
        self.max_y = 20
        self.min_y = 0
        self.left_margin = 6  # Space for y-axis labels
        self.label_spacing = 3  # Each label + 2 dots spacing

    def normalize_data(self, data: List[float]) -> List[float]:
        return [
            None if x is None else
            self.height - 1 - int((min(x, self.max_y) / self.max_y) * (self.height - 1))
            for x in data
        ]

    def draw(self, data_series: List[Tuple[List[float], str, str]], days_ago: List[int]) -> str:
        # Calculate width based on number of x-axis labels and spacing
        self.width = len(days_ago) * self.label_spacing - 1
        self.total_width = self.width + self.left_margin + 2  # +2 for borders

        normalized_series = [
            (self.normalize_data(data), label, symbol)
            for data, label, symbol in data_series
        ]

        # Initialize graph with dots
        graph = [['·' for _ in range(self.width)] for _ in range(self.height)]

        # Plot data points
        x_scale = (self.width - 1) / (len(days_ago) - 1)
        for normalized_data, _, symbol in normalized_series:
            for i, y in enumerate(normalized_data):
                if y is not None:
                    x = int(i * x_scale)
                    if 0 <= x < self.width and 0 <= y < self.height:
                        graph[y][x] = symbol

        output = []

        # Add legend
        output.append('╔════ DATA SERIES ═════════════════════╗')
        for _, label, symbol in data_series:
            output.append(f'║ {symbol} : {label:<32} ║')
        output.append('╚══════════════════════════════════════╝')
        output.append('')

        # Add top border
        output.append('╔' + '═' * self.total_width + '╗')

        # Add graph with y-axis labels
        for i in range(self.height):
            y_value = self.max_y - i
            row = f'║ {y_value:2d} │ {"".join(graph[i])} ║'
            output.append(row)

        # Add x-axis separator
        output.append('╟' + '─' * self.left_margin + '┴' + '─' * self.width + '╢')

        # Create x-axis with evenly spaced labels
        x_axis = [' ' for _ in range(self.width)]
        for i, day in enumerate(days_ago):
            pos = i * self.label_spacing
            label = str(day)
            for j, char in enumerate(label):
                if pos + j < self.width:
                    x_axis[pos + j] = char

        # Add x-axis to output
        output.append(f'║ {" " * self.left_margin}{"".join(x_axis)} ║')
        output.append(f'║ {" " * self.left_margin}{"Days Ago":^{self.width}} ║')

        # Add bottom border
        output.append('╚' + '═' * self.total_width + '╝')

        return '\n'.join(output)

    def __init__(self):
        self.width = 100  # Graph area width
        self.height = 20
        self.max_y = 20
        self.min_y = 0
        self.left_margin = 6  # Space for y-axis labels
        self.total_width = self.width + self.left_margin + 1

    def normalize_data(self, data: List[float]) -> List[float]:
        return [
            None if x is None else
            self.height - 1 - int((min(x, self.max_y) / self.max_y) * (self.height - 1))
            for x in data
        ]

    def draw(self, data_series: List[Tuple[List[float], str, str]], days_ago: List[int]) -> str:
        normalized_series = [
            (self.normalize_data(data), label, symbol)
            for data, label, symbol in data_series
        ]

        # Initialize graph with dots
        graph = [['·' for _ in range(self.width)] for _ in range(self.height)]

        # Plot data points
        x_scale = (self.width - 1) / (len(days_ago) - 1)
        for normalized_data, _, symbol in normalized_series:
            for i, y in enumerate(normalized_data):
                if y is not None:
                    x = int(i * x_scale)
                    if 0 <= x < self.width and 0 <= y < self.height:
                        graph[y][x] = symbol

        output = []

        # Add legend
        output.append('╔════ DATA SERIES ═════════════════════╗')
        for _, label, symbol in data_series:
            output.append(f'║ {symbol} : {label:<32} ║')
        output.append('╚══════════════════════════════════════╝')
        output.append('')

        # Add top border
        output.append('╔' + '═' * self.total_width + '╗')

        # Add graph with y-axis labels
        for i in range(self.height):
            y_value = self.max_y - i
            row = f'║ {y_value:2d} │ {"".join(graph[i])} ║'
            output.append(row)

        # Add x-axis separator
        output.append('╟' + '─' * self.left_margin + '┴' + '─' * self.width + '╢')

        # Calculate x-axis label positions
        x_labels = []
        label_positions = []
        for i, day in enumerate(days_ago):
            pos = int(i * x_scale)
            label_positions.append(pos)
            x_labels.append(str(day))

        # Create x-axis with aligned labels
        x_axis = [' ' for _ in range(self.width)]
        for pos, label in zip(label_positions, x_labels):
            # Center the label around its position
            start = max(0, pos - len(label)//2)
            for j, char in enumerate(label):
                if start + j < self.width:
                    x_axis[start + j] = char

        # Add x-axis to output
        output.append(f'║ {" " * self.left_margin}{"".join(x_axis)}║')
        output.append(f'║ {" " * self.left_margin}{"Days Ago":^{self.width}}║')

        # Add bottom border
        output.append('╚' + '═' * self.total_width + '╝')

        return '\n'.join(output)


def main():
    print(print_retro_header())

    # Load credentials from keys.json
    with open("keys.json") as f:
        keys = json.load(f)
        url = keys["url"]
        consumer_key = keys["consumer_key"]
        consumer_secret = keys["consumer_secret"]

    wc = WooCommerceAnalytics(url, consumer_key, consumer_secret)

    try:
        print("⚡ Fetching sales data...")
        days_to_fetch = 30
        orders = wc.get_sales_data(days=days_to_fetch)
        daily_sales = wc.aggregate_daily_sales(orders)

        print("📊 Processing statistics...")
        sales = list(daily_sales.values())
        days_ago = list(range(days_to_fetch-1, -1, -1))

        ma7 = wc.calculate_moving_average(sales, 7)
        ma7_weighted = wc.calculate_moving_average(
            sales,
            7,
            [0.05, 0.1, 0.1, 0.15, 0.15, 0.2, 0.25]
        )

        graph = RetroASCIIGraph()
        visualization = graph.draw([
            (sales, "Daily Sales", "█"),
            (ma7, "7-day Moving Average", "◆"),
            (ma7_weighted, "7-day Weighted MA", "●")
        ], days_ago)

        print(visualization)
        print("\n[Press any key to exit]")

    except Exception as e:
        print(f"╔═══ ERROR ═══╗")
        print(f"║ {str(e):<11} ║")
        print(f"╚═════════════╝")

if __name__ == "__main__":
    main()