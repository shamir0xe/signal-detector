from src.delegators.app_delegator import App

def main():
    App() \
    .apply_config() \
    .apply_arguments() \
    .fetch_data() \
    .detect_signals() \
    .filter_trendlines() \
    .remove_duplicates() \
    .examining_signals() \
    .calculate_success_rate() \
    .print_results()

if __name__ == '__main__':
    main()
