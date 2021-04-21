import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, '..')))
from SignalDetector.src.delegators.app_delegator import App

def main():
    app = App()
    app.apply_config() \
    .apply_arguments() \
    .fetch_data() \
    .detect_signals() \
    .filter_trendlines() \
    .examining_signals() \
    .print_results() \
    .print_indicators_summary() \

if __name__ == '__main__':
    main()
